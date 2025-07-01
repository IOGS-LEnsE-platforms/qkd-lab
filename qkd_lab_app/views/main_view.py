import sys, os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGridLayout, QHBoxLayout, QStackedWidget

sys.path.append(os.path.abspath(".."))

from views.free_cpc_view import FreeCPCView
from views.correlation_view import CorrelationView
from views.histogram_display_widget import HistogramDisplayWidget
from views.graph_view import GraphView
from views.title_view import TitleView
from views.timetagging_view import TimeTaggingView

class DisplayView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()

        self.MAX_DELAY = 100  # A modifier
        self.res = 0.013 # A modifier

        self.histogram = HistogramDisplayWidget(self)
        self.graph = GraphView(self)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.graph)
        self.stack.addWidget(self.histogram)
        self.stack.setCurrentIndex(0)

        self.layout.addWidget(self.stack)
        self.setLayout(self.layout)

    def update_data(self, new_data):
        index = self.stack.currentIndex()
        if index == 0:
            self.graph.update_plot(new_data)
        if index == 1:
            self.histogram.update_data(new_data)

    def set_index(self, index):
        self.stack.setCurrentIndex(index)


class TopWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()

        self.title = TitleView(self)
        self.free_cpc = FreeCPCView(self)

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
        self.top_widget = TopWidget(self)
        self.correlation_view = CorrelationView(self)
        self.time_tagging_view = TimeTaggingView(self)

        self.top_widget.setMaximumWidth(300)
        self.correlation_view.setMaximumWidth(300)
        self.time_tagging_view.setMaximumWidth(300)

        self.controls_layout.addWidget(self.top_widget)
        self.controls_layout.addWidget(self.correlation_view)
        self.controls_layout.addWidget(self.time_tagging_view)


        ### Events
        self.timetagging = self.time_tagging_view.timetagging
        self.correlation = self.correlation_view.correlation

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
        |  0     | 1      |
        |        |        |
        |--------|--------|
        |  2     | 3      |
        |        |        |
        |--------|--------|
        '''
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

    def update_timetagging_progress(self, value, iCh):
        self.timetagging.update_progress(value, iCh)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainView()
    window.show()
    sys.exit(app.exec())