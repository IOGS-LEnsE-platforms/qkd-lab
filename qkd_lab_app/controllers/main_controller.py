from PyQt6.QtCore import QThread, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication, QVBoxLayout
import sys, os

sys.path.append(os.path.abspath(".."))

from models.workers import *
from models.config_dict import ConfigDict
from views.main_view import MainView

class MainController(QWidget):

    update_progress = pyqtSignal(float, int)
    update_graphs = pyqtSignal(list, int)
    run_back = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.config_dict = ConfigDict(os.path.dirname(os.path.abspath("."))+ r"\assets")
        self.default_params = self.config_dict.default_params
        self.serial_dict = self.config_dict.serial_dict

        self.thread = QThread(self)
        if __name__ == "__main__":
            self.main_view = MainView(self)
        else:
            self.main_view = self.parent.main_view

        self.main_view.timetagging.connect(self.timetagging_action)
        self.main_view.correlation.connect(self.start_correlation)

        self.frequency = 2000000
        self.N_SAMPLE = 10000
        self.res = 0.013

        if "TDC Internal Frequency" in self.default_params.keys():
            self.frequency = int(self.default_params["TDC Internal Frequency"])
        if "Number of Samples" in self.default_params.keys():
            self.N_SAMPLE = int(self.default_params["Number of Samples"])
        if "TDC Time Resolution" in self.default_params.keys():
            self.res = float(self.default_params["TDC Time Resolution"])

        self.MAX_DELAY = int(1e09 / self.frequency)

        self.path = os.path.dirname(os.path.abspath(".")) + r"\models\test.txt"

        print(self.path)

        self.CH_BOB = [1, 2, 4, 8]

        self.cpc = AureaCPC(self)
        self.iDev_dict = self.cpc.iDev_dict
        self.index_dict = {}
        self.cpc_iDev = []

        self.htdc = AureaHTDC(self)

        self.find_devices_dict()

        self.htdc_iDev = 0

        self.worker = None

        self.main_view.show()

        self.update_progress.connect(self.main_view.update_timetagging_progress)
        self.update_graphs.connect(self.main_view.update_data)

    def start_correlation(self):
        self.main_view.clear()
        self.main_view.setTo_histogram()
        if self.worker is not None:
            self.worker.stop()

        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        #self.thread = QThread()
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
        self.main_view.clear()
        self.main_view.setTo_histogram()
        QApplication.processEvents()
        if self.worker is not None:
            self.worker.stop()

        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.worker = TimeTaggingWorker(self)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action, Qt.ConnectionType.QueuedConnection)
        self.worker.acquisition_finished.connect(self.save_timetagging_data, Qt.ConnectionType.QueuedConnection)

        self.thread.start()

    def stop_timetagging(self):
        if isinstance(self.worker, TimeTaggingWorker):
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()

    def start_live(self):
        self.init_cpc()
        self.main_view.clear()
        self.main_view.setTo_graph()
        QApplication.processEvents()
        if self.worker is not None:
            self.worker.stop()

        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.worker = liveWorker(self)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action, Qt.ConnectionType.QueuedConnection)
        self.worker.acquisition_finished.connect(self.stop_live, Qt.ConnectionType.QueuedConnection)

        self.thread.start()

    def stop_live(self):
        if isinstance(self.worker, liveWorker):
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()

    def data_action(self, event):
        if type(event) == list:
            pass
            #self.update_data(event_list[1], 0)
        elif event[0] == "time tagging":
            #print(event)
            print("graphs update called")
            self.update_graphs.emit(event[1], int(event[2]))
            print("progress update called")
            self.update_progress.emit(event[3], int(event[2]))
            self.run_back.emit("run")
        elif event[0] == "live":
            print("graphs update called")
            self.update_graphs.emit(event[1], int(event[2]))

    def timetagging_action(self, event):
        if event == "start":
            self.start_timetagging()
        elif event == "stop":
            self.stop_timetagging()

    def save_timetagging_data(self):
        self.worker.save_data_in_file(self.worker.data, self.path)

    def update_data(self, data, iCh):
        self.main_view.update_data(data, iCh)
        #QApplication.processEvents()

    def find_devices_dict(self):
        '''dictionaries functions:
        serial_dict = {i : serial#} (given by config)
        iDev_dict = {available_serial# : iDev} (given by cpc)
        devices_dict = {i : available_serial#} (combination of both)
        index_dict = {i : iDev}
        '''
        devices_dict = {}
        for i in self.serial_dict.keys():
            device = self.serial_dict[i]
            if device in self.iDev_dict.keys():
                devices_dict[i] = device
                self.index_dict[i] = self.iDev_dict[device]
        print(self.serial_dict)
        print(devices_dict)
        self.main_view.update_devices(devices_dict, self.serial_dict)

    def order_cpc_displays(self, list_indexes):
        '''This function takes in the result stack from the checkbox array (free_cpc_view) and turns it into a iDev
        stack that is usable by the cpc in order to know what acquisition must be done
        '''
        self.cpc_iDev = []
        for i in list_indexes:
            self.cpc_iDev.append(self.index_dict[i])

    def init_cpc(self):
        self.cpc = AureaCPC(self)
        self.iDev_dict = self.cpc.iDev_dict
        self.find_devices_dict()

    def live_action(self, event): #Must be defined in MainView's parent!
        self.main_view.clear()
        if event[0] == "start":
            self.start_live()
        if event[0] == "checkbox":
            self.order_cpc_displays(event[1])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainController()
    sys.exit(app.exec())