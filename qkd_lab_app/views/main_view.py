import sys, os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGridLayout, QHBoxLayout, QStackedWidget

sys.path.append(os.path.abspath(".."))

from views.free_cpc_view import FreeCPCView
from views.correlation_view import CorrelationView, TDCParamsView
from views.histogram_display_widget import HistogramDisplayWidget
from views.graph_view import GraphView
from views.title_view import TitleView
from views.timetagging_view import TimeTaggingView

class DisplayView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()

        self.histogram = HistogramDisplayWidget(self.parent)
        self.graph = GraphView(self.parent)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.graph)
        self.stack.addWidget(self.histogram)
        self.stack.setCurrentIndex(0)

        self.layout.addWidget(self.stack)
        self.setLayout(self.layout)

    def isGraph(self):
        index = self.stack.currentIndex()
        if index == 0:
            return True
        else:
            return False

    def update_data(self, new_data):
        index = self.stack.currentIndex()
        if index == 0:
            self.graph.update_plot(new_data)
        if index == 1:
            self.histogram.update_data(new_data)

    def clear(self):
        self.histogram.clear()
        self.graph.clear()

    def set_index(self, index):
        self.stack.setCurrentIndex(index)

    def set_title(self, title):
        print("in displayview")
        index = self.stack.currentIndex()
        if index == 0:
            self.graph.title = title
        if index == 1:
            self.histogram.title = title


class TopWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()

        self.title = TitleView(self)
        self.free_cpc = FreeCPCView(self.parent)

        self.free_cpc.live_signal.connect(self.parent.live_action)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.free_cpc)
        self.setLayout(self.layout)


class MainView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QHBoxLayout()

        self.controls_layout = QVBoxLayout()
        self.images_layout = QGridLayout()

        ###Affichage des graphes
        self.top_left_display = DisplayView(self.parent)
        self.top_right_display = DisplayView(self.parent)
        self.bottom_left_display = DisplayView(self.parent)
        self.bottom_right_display = DisplayView(self.parent)

        self.images_layout.setColumnStretch(0, 1)
        self.images_layout.setColumnStretch(1, 1)
        self.images_layout.setRowStretch(0, 1)
        self.images_layout.setRowStretch(1, 1)

        self.images_layout.addWidget(self.top_left_display)
        self.images_layout.addWidget(self.top_right_display)
        self.images_layout.addWidget(self.bottom_left_display)
        self.images_layout.addWidget(self.bottom_right_display)

        ###Contrôles
        self.top_widget = TopWidget(self.parent)
        self.tdc_params_view = TDCParamsView(self.parent)
        self.time_tagging_view = TimeTaggingView(self.parent)
        self.correlation_view = CorrelationView(self.parent)
        self.correlation_view.setEnabled(False)

        self.top_widget.setMaximumHeight(400)
        self.top_widget.setMaximumWidth(300)
        self.tdc_params_view.setMaximumWidth(300)
        self.correlation_view.setMaximumWidth(300)
        self.time_tagging_view.setMaximumWidth(300)

        self.controls_layout.addWidget(self.top_widget)
        self.controls_layout.addWidget(self.tdc_params_view)
        self.controls_layout.addWidget(self.time_tagging_view)
        self.controls_layout.addWidget(self.correlation_view)


        ### Events
        self.params = self.tdc_params_view.params
        self.timetagging = self.time_tagging_view.timetagging
        self.correlation = self.correlation_view.correlation
        self.file_signal = self.time_tagging_view.file_signal

        ### Mise en place du layout
        self.layout.addLayout(self.controls_layout)
        self.layout.addLayout(self.images_layout)

        self.setLayout(self.layout)

    def setTo_histogram(self):
        self.top_left_display.set_index(1)
        self.top_right_display.set_index(1)
        self.bottom_left_display.set_index(1)
        self.bottom_right_display.set_index(1)

    def setTo_graph(self):
        self.top_left_display.set_index(0)
        self.top_right_display.set_index(0)
        self.bottom_left_display.set_index(0)
        self.bottom_right_display.set_index(0)

    def update_data(self, new_data, index):
        '''This function allows for independent graph update. The selected graph is represented by an index 0-3
        |--------|--------|
        |  1     | 2      |
        |        |        |
        |--------|--------|
        |  4     | 8      |
        |        |        |
        |--------|--------|
        '''
        print("graphs update done")
        if index == 0:
            self.top_left_display.update_data(new_data)
        elif index == 1:
            self.top_right_display.update_data(new_data)
        elif index == 2:
            self.bottom_left_display.update_data(new_data)
        elif index == 3:
            self.bottom_right_display.update_data(new_data)

    def update_correlation_progress(self, value):
        self.correlation.update_progress(value)

    def update_timetagging_progress(self, value, i):
        self.time_tagging_view.update_progress(value, i)

    def update_devices(self, available_dict, all_dict):
        self.top_widget.free_cpc.find_devices_list(available_dict)
        self.top_widget.free_cpc.init_checkbox_display(all_dict)

    def clear(self):
        self.top_left_display.clear()
        self.top_right_display.clear()
        self.bottom_left_display.clear()
        self.bottom_right_display.clear()

    def set_span(self, index):
        self.top_left_display.graph.MAX_INDEX = index
        self.top_right_display.graph.MAX_INDEX = index
        self.bottom_left_display.graph.MAX_INDEX = index
        self.bottom_right_display.graph.MAX_INDEX = index

    def set_title(self, title, index):
        print("in main view")
        if index == 0:
            self.top_left_display.set_title(title)
        elif index == 1:
            self.top_right_display.set_title(title)
        elif index == 2:
            self.bottom_left_display.set_title(title)
        elif index == 3:
            self.bottom_right_display.set_title(title)

    def setEnabled(self, value):
        self.top_widget.free_cpc.setEnabled(value)
        self.tdc_params_view.setEnabled(value)
        self.time_tagging_view.setEnabled(value)
        self.correlation_view.setEnabled(value)

    def set_correlation_path(self, path, to_which:bool):
        '''to_which = True : bob, to_which = False, alice'''
        self.correlation_view.set_path(path, to_which)

    def enable_correlation(self, value):
        self.correlation_view.set_correlation_enabled(value)

    def set_timetag_dir(self, path):
        self.time_tagging_view.set_file_dir(path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainView()
    window.show()
    sys.exit(app.exec())