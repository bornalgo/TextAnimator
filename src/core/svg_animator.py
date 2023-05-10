from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QTimer, Qt
from src.core.text_animator import TextAnimator


class SvgAnimator:
    def __init__(self, svgWidget: QSvgWidget, text_animator: TextAnimator):
        self.svgWidget = svgWidget
        self.text_animator = text_animator
        self.paths = [path for path in self.text_animator.doc.getElementsByTagName('path')]
        self.i_path = 0
        self.n_paths = len(self.paths)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(100)
        self.wait_timer = QTimer()
        self.wait_timer.timeout.connect(self.waitTimerEvent)

    def reset(self, text_animator: TextAnimator = None):
        self.timer.stop()
        self.wait_timer.stop()
        if text_animator is not None:
            self.text_animator = text_animator
            self.paths = [path for path in self.text_animator.doc.getElementsByTagName('path')]
            self.i_path = 0
            self.n_paths = len(self.paths)
            self.timer.start(100)
        else:
            self.text_animator = None
            self.svgWidget.hide()

    def timerEvent(self):
        if self.i_path < self.n_paths:
            self.paths[self.i_path].setAttribute('fill', self.text_animator.kwargs_output['font_color'])
            self.svgWidget.load(bytearray(self.text_animator.doc.toxml(), encoding='utf-8'))
            self.svgWidget.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
            if self.svgWidget.isHidden():
                self.svgWidget.show()
            self.i_path += 1
        elif not self.wait_timer.isActive():
            self.wait_timer.start(5000)

    def waitTimerEvent(self):
        if self.wait_timer.isActive():
            for path in self.paths:
                path.setAttribute('fill', self.text_animator.kwargs_output['background'])
            self.svgWidget.load(bytearray(self.text_animator.doc.toxml(), encoding='utf-8'))
            self.svgWidget.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
            if self.svgWidget.isHidden():
                self.svgWidget.show()
            self.i_path = 0
            self.wait_timer.stop()


