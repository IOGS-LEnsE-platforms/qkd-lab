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

        self.main_view.timetagging.connect(self.timetagging_action)
        self.main_view.correlation.connect(self.start_correlation)

        self.frequency = 2000000
        self.N_SAMPLE = 20000
        self.MAX_DELAY = int(1e09 / self.frequency)
        self.res = 0.013
        self.path = os.path.dirname(os.path.abspath(".")) + r"\models\test.txt"

        print(self.path)

        self.htdc = AureaHTDC(self)

        self.iDev = 0

        self.worker = None

        self.main_view.show()

    def start_correlation(self):
        self.main_view.setTo_histogram()
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.thread = QThread()
        self.worker = CorrelationWorker(self)
        self.worker.moveToThread(self.thread)

        self.htdc.ready_channel_correlation(self.iDev)

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action)

        self.thread.start()

    def stop_correlation(self):
        if isinstance(self.worker, CorrelationWorker):
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()

    def start_timetagging(self):
        self.main_view.setTo_histogram()
        QApplication.processEvents()
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.worker = TimeTaggingWorker(self)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action)
        self.worker.acquisition_finished.connect(self.save_timetagging_data)

        self.thread.start()

    def stop_timetagging(self):
        if isinstance(self.worker, TimeTaggingWorker):
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()

    def data_action(self, event):
        if type(event) == list:
            pass
            #self.update_data(event_list[1], 0)
        elif type(event) == tuple:
            print(event)
            self.main_view.update_timetagging_progress(event[2], int(event[1]))
            self.update_data(event[0], int(event[1]))

    def timetagging_action(self, event):
        if event == "start":
            self.start_timetagging()
        elif event == "stop":
            self.stop_timetagging()

    def save_timetagging_data(self):
        self.worker.save_data_in_file(self.worker.data, self.path)

    def update_data(self, data, iCh):
        self.main_view.update_data(data, iCh)
        QApplication.processEvents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainController()
    sys.exit(app.exec())