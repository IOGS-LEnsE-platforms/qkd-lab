from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication, QVBoxLayout
import sys, os

sys.path.append(os.path.abspath(".."))

from models.workers import *
from views.main_view import MainView

class MainController(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.thread = QThread(self)
        self.main_view = self.parent.main_view

        self.worker = None

    def start_correlation(self):
        self.worker = CorrelationWorker(self)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action)
        self.main_view.setTo_histogram()
        self.thread.start()

    def start_timetagging(self):
        self.worker = SingleChannelWorker(self)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action)
        self.main_view.setTo_histogram()
        self.thread.start()

    def data_action(self, event):
        event_list = event.split("=")
        if event_list[0] == "correlation":
            pass
        elif event_list[0] == "time tagging":
            pass