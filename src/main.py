import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from src.gui.main_window import MainWindow
from src.core.tools import strftime
import tempfile
import logging
import src.environment as env
env.logger = logging.getLogger(__name__)


def handleException(exc_type, exc_value, exc_traceback):
    from traceback import format_exception
    exc_list: list = format_exception(exc_type, exc_value, exc_traceback)
    msg = ''
    for exc in exc_list:
        if not exc.startswith('Traceback'):
            msg += exc
    QMessageBox.critical(env.window, 'System Error', msg)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    return


if __name__ == '__main__':
    env.app = QApplication(sys.argv)
    env.window = MainWindow()
    sys.excepthook = handleException
    handler = logging.StreamHandler(stream=tempfile.NamedTemporaryFile(prefix='ba-TextAnimator-%s' % strftime(),
                                                                       suffix='.log'))
    env.logger.addHandler(handler)
    env.window.show()
    sys.exit(env.app.exec_())
