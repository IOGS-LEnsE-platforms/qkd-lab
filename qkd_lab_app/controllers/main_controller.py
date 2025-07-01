from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication, QVBoxLayout
import sys, os

sys.path.append(os.path.abspath(".."))

from models.workers import *
from views.main_view import MainView
import time

class MainController(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.thread = QThread(self)
        if __name__ == "__main__":
            self.main_view = MainView()
        else:
            self.main_view = self.parent.main_view

        self.main_view.timetagging.connect(self.start_timetagging)
        self.main_view.correlation.connect(self.start_correlation)

        self.frequency = 2000000
        self.N_SAMPLE = 20000
        self.MAX_DELAY = int(1e09 / self.frequency)
        self.res = 0.013

        self.htdc = AureaHTDC(self)

        self.iDev = 0

        self.worker = None

        self.main_view.show()

    def start_correlation(self):
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.worker = CorrelationWorker(self)
        self.worker.moveToThread(self.thread)

        self.htdc.ready_channel_correlation(self.iDev)

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action)
        self.main_view.setTo_histogram()
        self.thread.start()

    def start_timetagging(self):
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.htdc.ready_channel_timetagging(self.iDev)
        self.worker = TimeTaggingWorker(self)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action)
        self.main_view.setTo_histogram()
        self.thread.start()

    def data_action(self, event):
        event_list = event.split("=")
        if event_list[0] == "correlation":
            self.update_data(event_list[1], 0)
        elif event_list[0] == "time tagging":
            self.update_data(event_list[1], int(event_list[2]))

    def update_data(self, data, iCh):
        self.main_view.update_data(data, iCh)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainController()
    sys.exit(app.exec())