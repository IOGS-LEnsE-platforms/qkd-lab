from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication, QVBoxLayout
import sys, os

sys.path.append(os.path.abspath(".."))

from models.process_model import ProcessModel
from views.histogram_display_widget import HistogramDisplayWidget


class MainController(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent