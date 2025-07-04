from PyQt6.QtCore import QThread, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication, QVBoxLayout
import sys, os

sys.path.append(os.path.abspath(".."))

from models.workers import *
from models.path_browser import PathBrowser
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

        self.frequency = 2000000
        self.N_SAMPLE = 10000
        self.res = 0.013
        self.ini_path = os.path.dirname(os.path.abspath("."))

        if "TDC Internal Frequency" in self.default_params.keys():
            self.frequency = int(self.default_params["TDC Internal Frequency"])
        if "Number of Samples" in self.default_params.keys():
            self.N_SAMPLE = int(self.default_params["Number of Samples"])
        if "TDC Time Resolution" in self.default_params.keys():
            self.res = float(self.default_params["TDC Time Resolution"])
        if "Initial Graph Span" in self.default_params.keys():
            self.ini_graph_span = int(self.default_params["Initial Graph Span"])
        if "Maximum Graph Span" in self.default_params.keys():
            self.max_graph_span = int(self.default_params["Maximum Graph Span"])
        if "Minimum Graph Span" in self.default_params.keys():
            self.min_graph_span = int(self.default_params["Minimum Graph Span"])
        if "HTDC Overload" in self.default_params.keys():
            self.htdc_overload = int(self.default_params["HTDC Overload"])
        if "Initial File Path" in self.default_params.keys():
            self.ini_path = PathBrowser(self.default_params["Initial File Path"])
        if "Max Frequency" in self.default_params.keys():
            self.max_freq = int(self.default_params["Max Frequency"])
        if "Min Frequency" in self.default_params.keys():
            self.min_freq = int(self.default_params["Min Frequency"])
        if "Max Number Samples"  in self.default_params.keys():
            self.max_num_samples = int(self.default_params["Max Number Samples"])
        if "Min Number Samples" in self.default_params.keys():
            self.min_num_samples = int(self.default_params["Min Number Samples"])

        self.MAX_DELAY = int(1e09 / self.frequency)

        self.thread = QThread(self)
        if __name__ == "__main__":
            self.main_view = MainView(self)
        else:
            self.main_view = self.parent.main_view

        self.main_view.timetagging.connect(self.timetagging_action)
        self.main_view.correlation.connect(self.correlation_action)
        self.main_view.params.connect(self.change_tdc_params)

        self.path = os.path.dirname(os.path.abspath(".")) + r"\models\test.txt"

        print(self.path)

        self.CH_BOB = [1, 2, 4, 8]

        self.browser = PathBrowser(self)
        self.browser.file_extracted.connect(self.get_path)
        self.PATH_BOB = ''
        self.PATH_ALICE = ''
        self.i_alice = 0
        self.to_which = ''

        self.main_view.file_signal.connect(self.handle_files)

        self.cpc = AureaCPC(self)
        self.iDev_dict = self.cpc.iDev_dict
        self.index_dict = {}
        self.cpc_iDev = []

        self.htdc = AureaHTDC(self)

        self.find_devices_dict()

        self.htdc_iDev = 0

        self.worker = None

        self.main_view.showMaximized()

        self.update_progress.connect(self.main_view.update_timetagging_progress)
        self.update_graphs.connect(self.main_view.update_data)

    def start_correlation(self):
        self.main_view.setEnabled(False)
        if self.worker is not None:
            self.worker.stop()

        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.main_view.clear()
        self.main_view.setTo_histogram()
        self.main_view.clear()

        #self.thread = QThread()
        self.worker = CorrelationWorker(self)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action)

        self.thread.start()
        self.main_view.setEnabled(True)

    def stop_correlation(self):
        if isinstance(self.worker, CorrelationWorker):
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()

    def start_timetagging(self):
        self.main_view.setEnabled(False)
        if self.worker is not None:
            self.worker.stop()

        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        print("starting time tagging")
        self.main_view.clear()
        self.main_view.setTo_histogram()
        self.main_view.clear()
        QApplication.processEvents()

        self.worker = TimeTaggingWorker(self)
        self.main_view.clear()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action, Qt.ConnectionType.QueuedConnection)
        self.worker.acquisition_finished.connect(self.save_timetagging_data, Qt.ConnectionType.QueuedConnection)

        self.thread.start()
        self.main_view.setEnabled(True)

    def stop_timetagging(self):
        if isinstance(self.worker, TimeTaggingWorker):
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()

    def start_live(self):
        self.main_view.setEnabled(False)
        if self.worker is not None:
            self.worker.stop()

        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.main_view.clear()
        self.cpc = AureaCPC(self)
        self.main_view.setTo_graph()
        self.main_view.clear()
        QApplication.processEvents()
        print("view updated")

        self.worker = liveWorker(self)
        self.main_view.clear()
        print("worker initialized")

        self.worker.moveToThread(self.thread)
        print("connected to thread")

        self.thread.started.connect(self.worker.run)
        self.worker.sample_recieved.connect(self.data_action, Qt.ConnectionType.QueuedConnection)
        self.worker.acquisition_finished.connect(self.stop_live, Qt.ConnectionType.QueuedConnection)

        self.thread.start()
        self.main_view.setEnabled(True)

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
            print("live graphs update called")
            self.update_graphs.emit(event[1], int(event[2]))
            self.run_back.emit("run")
        elif event[0] == "correlation":
            self.update_graphs.emit(event[1], int(event[2]))
            self.run_back.emit("run")

    def timetagging_action(self, event):
        if event == "start":
            self.start_timetagging()
        elif event == "stop":
            self.stop_timetagging()

    def save_timetagging_data(self):
        self.PATH_BOB = self.path
        self.main_view.set_correlation_path(self.PATH_BOB, True)
        if self.PATH_BOB != '':
            self.main_view.enable_correlation(True)
        else:
            self.main_view.enable_correlation(False)
        self.worker.save_data_in_file(self.worker.data, self.path)
        self.worker.stop()

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
        for i, index in enumerate(list_indexes):
            self.cpc_iDev.append(self.index_dict[index])
            print("setting title")
            self.main_view.set_title("CPC " + str(index), i)

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
            if isinstance(self.worker, liveWorker):
                self.worker.cpc_iDev = self.cpc_iDev
        if event[0] == "graph span":
            self.main_view.set_span(event[1])

    def change_tdc_params(self, event):
        self.frequency = int(event[0])
        self.N_SAMPLE = int(event[1])
        self.htdc.N_SAMPLE = self.N_SAMPLE
        self.htdc.frequency = self.frequency
        self.htdc.setFrequency(self.htdc_iDev, self.frequency)

    def correlation_action(self, event):
        if event == "correlation":
            self.start_correlation()
        elif event == "browse bob":
            self.browser.close()
            self.to_which = 'bob'
            self.browser.chose_file(self.ini_path)
        elif event == "browse alice":
            self.browser.close()
            self.to_which = 'alice'
            self.browser.chose_file(self.ini_path)
        elif event == "CH1":
            self.i_alice = 0
        elif event == "CH2":
            self.i_alice = 1

    def handle_files(self, event):
        self.to_which = "timetagging"
        print(event)
        self.browser.write_file(event, self.ini_path)

    def get_path(self, event):
        if self.to_which == 'bob':
            self.PATH_BOB = event
            self.main_view.set_correlation_path(self.PATH_BOB, True)
        elif self.to_which == 'alice':
            self.PATH_ALICE = event
            self.main_view.set_correlation_path(self.PATH_ALICE, False)
        elif self.to_which == 'timetagging':
            self.path = event
            self.main_view.set_timetag_dir(event)
        if self.PATH_BOB != '':
            self.main_view.enable_correlation(True)
        else:
            self.main_view.enable_correlation(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainController()
    sys.exit(app.exec())