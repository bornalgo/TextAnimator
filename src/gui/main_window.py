import sys
import typing
import os
import shutil
from src.gui.interface_ui import *
from src.core.text_animator import TextAnimator
from src.core.svg_animator import SvgAnimator
from src.core.ascii_art import taag
from src.core.tools import colorComplement, svgColorToTuple
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QColorDialog, QMessageBox, QFileDialog, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QSize, QThreadPool
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtSvg import QSvgWidget

from src.gui.worker import Worker


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.resetView()

        self.background = QColor("white")
        self.textEdit_backgroundColor = self.background
        self.directory: str = os.path.expanduser('~')
        self.file_name: str = ''
        self.font_name: str = self.ui.fontComboBox.currentFont().family()
        self.font_size: int = self.ui.fontSpinBox.value()

        self.horizontalSpacer = QWidget(self.ui.toolBar)
        self.horizontalSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalSpacer.setVisible(True)
        self.horizontalSpacer = self.ui.toolBar.addWidget(self.horizontalSpacer)

        self.progress = QSvgWidget(':/icons/icons/progress.svg', self.ui.toolBar)
        self.progress.setFixedSize(self.ui.toolBar.iconSize())
        self.progress.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.progress.setVisible(False)
        self.progress = self.ui.toolBar.addWidget(self.progress)

        self.ui.dockWidget_text.topLevelChanged.connect(self.dockWidget_topLevelChanged)
        self.ui.dockWidget_text.closeEvent = lambda event: self.dockWidget_visibilityChange(self.ui.dockWidget_text,
                                                                                            False, event)

        self.ui.dockWidget_image.topLevelChanged.connect(self.dockWidget_topLevelChanged)
        self.ui.dockWidget_image.closeEvent = lambda event: self.dockWidget_visibilityChange(self.ui.dockWidget_image,
                                                                                             False, event)

        self.ui.actionText_Editor_Widget.changed.connect(self.actionWidget_changed)
        self.ui.actionImage_Viewer_Widget.changed.connect(self.actionWidget_changed)

        self.ui.actionExit.triggered.connect(lambda: sys.exit())
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionSave_as.triggered.connect(lambda: self.save(True))
        self.ui.actionSave_toolbar.triggered.connect(self.save)
        self.ui.actionOpen.triggered.connect(self.open)
        self.ui.actionOpen_toolbar.triggered.connect(self.open)
        self.ui.actionNew.triggered.connect(self.new)
        self.ui.actionNew_toolbar.triggered.connect(self.new)
        self.ui.actionAbout.triggered.connect(self.about)

        self.ui.actionReset_View.triggered.connect(self.resetView)

        self.ui.fontComboBox.currentFontChanged.connect(self.fontChanged)
        self.ui.fontSpinBox.valueChanged.connect(self.fontChanged)

        self.ui.pushButton_colorPicker.clicked.connect(self.openColorDialog)

        self.ui.pushButton_erase.clicked.connect(self.erase)
        self.ui.pushButton_convert.clicked.connect(self.convert)

        self.svgAnimator: typing.Union[SvgAnimator, None] = None

        self.svgWidget = QSvgWidget(self.ui.dockWidgetContents_image)
        self.svgWidget.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        self.ui.dockWidgetContents_image.layout().addWidget(self.svgWidget)

        self.update_title()

        self.threadpool = QThreadPool()

    @QtCore.pyqtSlot()
    def dockWidget_topLevelChanged(self):
        dockWidget: QDockWidget = self.sender()
        if dockWidget and dockWidget.isFloating():
            dockWidget.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window | Qt.WindowMinimizeButtonHint |
                                      Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
            dockWidget.show()

    def dockWidget_visibilityChange(self, sender: QDockWidget, state: bool, event):
        dockWidget = sender
        if dockWidget == self.ui.dockWidget_text:
            actionWidget = self.ui.actionText_Editor_Widget
        elif dockWidget == self.ui.dockWidget_image:
            actionWidget = self.ui.actionImage_Viewer_Widget
        else:
            return
        if actionWidget.isChecked() != state:
            actionWidget.setChecked(state)
        self.update_actionReset_View_State()

    @QtCore.pyqtSlot()
    def actionWidget_changed(self):
        actionWidget: QtWidgets.QAction = self.sender()
        state = actionWidget.isChecked()
        if actionWidget == self.ui.actionText_Editor_Widget:
            dockWidget = self.ui.dockWidget_text
        elif actionWidget == self.ui.actionImage_Viewer_Widget:
            dockWidget = self.ui.dockWidget_image
        else:
            return
        if state != dockWidget.isVisible():
            dockWidget.setVisible(state)
        self.update_actionReset_View_State()

    @QtCore.pyqtSlot()
    def resetView(self):
        if self.ui.dockWidget_text.isFloating():
            self.ui.dockWidget_text.setFloating(False)
        if self.ui.dockWidget_image.isFloating():
            self.ui.dockWidget_image.setFloating(False)
        self.splitDockWidget(self.ui.dockWidget_text, self.ui.dockWidget_image, Qt.Orientation.Horizontal)
        self.resizeDocks([self.ui.dockWidget_text, self.ui.dockWidget_image],
                         [self.ui.dockWidget_text.maximumWidth(), self.ui.dockWidget_image.maximumWidth()],
                         Qt.Orientation.Horizontal)

    @QtCore.pyqtSlot()
    def fontChanged(self):
        font = self.ui.fontComboBox.currentFont()
        font.setPointSize(self.ui.fontSpinBox.value())
        self.ui.textEdit.setFont(font)

    @QtCore.pyqtSlot()
    def openColorDialog(self, color: QColor = None):
        if color is None:
            color = QColorDialog.getColor(initial=self.textEdit_backgroundColor, parent=self,
                                          title="Pick background color")

        if color.isValid():
            self.textEdit_backgroundColor = color
            self.ui.textEdit.setStyleSheet("background-color: %s; color: %s" % (color.name(),
                                                                                colorComplement(color).name()))
            self.ui.pushButton_colorPicker.setStyleSheet("background-color: %s;" % color.name())

    def update_actionReset_View_State(self):
        self.ui.actionReset_View.setEnabled(self.ui.actionText_Editor_Widget.isChecked() or
                                            self.ui.actionImage_Viewer_Widget.isChecked())

    @QtCore.pyqtSlot()
    def erase(self):
        self.ui.textEdit.clear()

    def convert_worker(self, text: str, **kwargs):
        text = taag(text).target
        return TextAnimator(text=text, background=self.textEdit_backgroundColor.getRgb()[:-1],
                            font_name=self.ui.fontComboBox.currentFont().family(),
                            font_size=self.ui.fontSpinBox.value())

    def convert_result(self, text_animator: TextAnimator):
        err = text_animator.get_error()
        if err:
            QMessageBox.warning(self, 'Convert Error', err)
        else:
            self.prepare(text_animator)
        self.ui.actionSave.setEnabled(True)
        self.ui.actionSave_as.setEnabled(True)
        self.ui.actionSave_toolbar.setEnabled(True)

    @QtCore.pyqtSlot()
    def convert(self):
        text = self.ui.textEdit.toPlainText()
        if text:
            if self.is_changed(text):
                self.wait()
                worker = Worker(self.convert_worker, text)
                worker.signals.result.connect(self.convert_result)
                worker.signals.finished.connect(lambda: self.wait(False))
                self.threadpool.start(worker)
            else:
                QMessageBox.warning(self, 'Convert Error', 'No changes has been made to re-convert!')
        else:
            QMessageBox.warning(self, 'Convert Error', 'No text has been entered to get animated!')

    @QtCore.pyqtSlot()
    def save(self, new_file: bool = False) -> bool:
        title = 'Save As' if new_file else 'Save'
        if self.svgAnimator is not None and self.svgAnimator.text_animator is not None:
            if not new_file and self.file_name:
                file_name = self.file_name
            else:
                file_name, _ = QFileDialog.getSaveFileName(self, caption=title,
                                                           directory=self.directory,
                                                           filter='TextAnimator File (*.svg)')
            if file_name:
                self.directory = os.path.dirname(file_name)
                file_handle = None
                try:
                    import src.environment as env
                    if os.path.exists(env.text_animator.file_name):
                        shutil.move(env.text_animator.file_name, file_name)
                    else:
                        file_handle = open(file_name, 'w')
                        env.text_animator.doc_main.writexml(file_handle)
                        file_handle.close()
                    env.text_animator.file_name = file_name
                    env.text_animator.from_file = True
                    self.file_name = file_name
                    self.update_title()
                    return True
                except Exception as e:
                    try:
                        file_handle.close()
                    except:
                        pass
                    QMessageBox.warning(self, '%s Error' % title, 'Failed to save in %s file; more info: %s'
                                        % (file_name, str(e)))
        else:
            QMessageBox.warning(self, '%s Error' % title, 'Nothing is available to be saved!')
        return False

    def open_worker(self, file_name: str, **kwargs):
        return TextAnimator(file_name=file_name)

    def open_result(self, text_animator: TextAnimator, file_name: str):
        err = text_animator.get_error()
        if err:
            QMessageBox.warning(self, 'Open Error', err)
        else:
            self.prepare(text_animator, file_name)

    @QtCore.pyqtSlot()
    def open(self):
        if self.check_existing():
            file_name, _ = QFileDialog.getOpenFileName(self, caption='Open', directory=self.directory,
                                                       filter='TextAnimator File (*.svg)')
            if file_name:
                self.wait()
                self.directory = os.path.dirname(file_name)
                worker = Worker(self.open_worker, file_name)
                worker.signals.result.connect(lambda text_animator: self.open_result(text_animator, file_name))
                worker.signals.finished.connect(lambda: self.wait(False))
                self.threadpool.start(worker)

    def prepare(self, text_animator: typing.Union[TextAnimator, None], file_name: str = ''):
        import src.environment as env
        if env.text_animator is not None:
            if not file_name and env.text_animator.from_file:
                self.file_name = env.text_animator.file_name
            del env.text_animator
        env.text_animator = text_animator
        if file_name:
            self.file_name = file_name
        if env.text_animator is None:
            self.file_name = ''
        self.update_title()
        if file_name:
            self.ui.fontComboBox.setCurrentFont(QFont(env.text_animator.kwargs_output['font_name']))
            self.ui.fontSpinBox.setValue(env.text_animator.kwargs_output['font_size'])
            self.openColorDialog(QColor(*svgColorToTuple(env.text_animator.kwargs_output['background'], 'background')))
            self.ui.textEdit.setText(env.text_animator.kwargs_output['text'])
        if self.svgAnimator is None:
            if env.text_animator is not None:
                self.svgAnimator = SvgAnimator(self.svgWidget, env.text_animator)
        else:
            self.svgAnimator.reset(env.text_animator)

    @QtCore.pyqtSlot()
    def new(self):
        if self.check_existing():
            self.prepare(None)
            self.ui.fontComboBox.setCurrentFont(QFont(self.font_name))
            self.ui.fontSpinBox.setValue(self.font_size)
            self.openColorDialog(self.background)
            self.ui.textEdit.clear()
            self.svgWidget.hide()

    def check_existing(self) -> bool:
        import src.environment as env
        if self.file_name:
            import src.environment as env
            if env.text_animator.file_name != self.file_name:
                ans = QMessageBox.question(self, 'Save Question', 'Do you want to save the changes in the %s file?'
                                           % self.file_name)
                if ans == QMessageBox.Yes:
                    return self.save()
        elif self.svgAnimator is not None and env.text_animator is not None:
            ans = QMessageBox.question(self, 'Save Question', 'Do you want to save the current results in a new file?')
            if ans == QMessageBox.Yes:
                return self.save()
        return True

    def is_changed(self, text: str) -> bool:
        import src.environment as env
        if env.text_animator is not None and self.svgAnimator is not None:
            background = 'rgb(%d, %d, %d)' % self.textEdit_backgroundColor.getRgb()[:-1]
            return ((env.text_animator.kwargs_output['text'] != text)
                    or (env.text_animator.kwargs_output['background'] != background)
                    or (env.text_animator.kwargs_output['font_name'] != self.ui.fontComboBox.currentFont().family())
                    or (env.text_animator.kwargs_output['font_size'] != self.ui.fontSpinBox.value()))
        return True

    def update_title(self):
        if self.file_name:
            import src.environment as env
            title = 'TextAnimator - %s' % os.path.basename(self.file_name)
            if env.text_animator is not None and env.text_animator.file_name != self.file_name:
                title += '*'
                self.ui.actionSave.setEnabled(True)
                self.ui.actionSave_toolbar.setEnabled(True)
            else:
                self.ui.actionSave.setEnabled(False)
                self.ui.actionSave_toolbar.setEnabled(False)
            self.ui.actionSave_as.setEnabled(True)
            self.setWindowTitle(title)
            self.setToolTip(self.file_name)
        else:
            self.setWindowTitle('TextAnimator')
            self.setToolTip('')
            self.ui.actionSave.setEnabled(False)
            self.ui.actionSave_as.setEnabled(False)
            self.ui.actionSave_toolbar.setEnabled(False)

    @QtCore.pyqtSlot()
    def about(self):
        mb = QMessageBox(QMessageBox.NoIcon, 'About', '', QMessageBox.Ok, self)
        mb.setTextFormat(Qt.RichText)
        mb.setText('<p align="center"><a href="https://github.com/bornalgo/TextAnimator">'
                   'TextAnimator</a><br><br>Version 2023.1<br><br><br>Copyright © 2023 <i><b>bornalgo</b></i></p>')
        mb.setIconPixmap(self.windowIcon().pixmap(QSize(80, 80)))
        mb.exec_()

    def wait(self, do_wait: bool = True):
        self.progress.setVisible(do_wait)
        self.setEnabled(not do_wait)
