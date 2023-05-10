from logging import Logger
import typing
from src.gui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
from src.core.text_animator import TextAnimator

app: typing.Union[QApplication, None] = None
logger: typing.Union[Logger, None] = None
window: typing.Union[MainWindow, None] = None
text_animator: typing.Union[TextAnimator, None] = None
