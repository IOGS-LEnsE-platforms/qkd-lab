from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QProgressBar, QSlider, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu import translate

if __name__ == '__main__':
    import sys, os

from lensepy.css import *


class CorrelationView(QWidget):

    correlation = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()

        self.title = QLabel('correlation_title')

        self.Nmatch_label = QLabel(f'number_of_time_matches : {0}')

        self.start_cor_button = QPushButton('Start Correlation')
        self.start_cor_button.setStyleSheet(unactived_button)
        self.start_cor_button.setFixedHeight(BUTTON_HEIGHT)
        self.start_cor_button.clicked.connect(self.start_action)

        self.cor_bar = QProgressBar()
        self.cor_bar.setMaximum(100)
        self.cor_bar.setMinimum(0)
        self.cor_bar.setValue(0)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.start_cor_button)

        self.setLayout(self.layout)

    def start_action(self):
        sender = self.sender()
        if sender == self.start_cor_button:
            self.correlation.emit("correlation")

    def setEnabled(self, value):
        self.start_cor_button.setEnabled(value)
        if value:
            self.start_cor_button.setStyleSheet(unactived_button)
        else:
            self.start_cor_button.setStyleSheet(disabled_button)

class TDCParamsView(QWidget):

    params = pyqtSignal(tuple)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()

        MAX_FREQUENCY = 10000000
        MIN_FREQUENCY = 10000
        FREQ_INI_VALUE = 100000

        MIN_N_SAMPLE = 10
        MAX_N_SAMPLE = 30000
        N_SAMPLE_INI = 10000

        self.title = QLabel('tdc_params_title')

        self.freq_layout = QVBoxLayout()
        self.freq_label = QLabel(f'frequency : {FREQ_INI_VALUE} Hz')

        self.freq_slider_layout = QHBoxLayout()
        self.freq_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_slider.setMinimum(MIN_FREQUENCY)
        self.freq_slider.setMaximum(MAX_FREQUENCY)
        self.freq_slider.setValue(FREQ_INI_VALUE)
        self.freq_slider.valueChanged.connect(self.slider_action)

        self.freq_button = QPushButton('Confirm')
        self.freq_button.setStyleSheet(unactived_button)
        self.freq_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.freq_button.clicked.connect(self.slider_action)

        self.freq_slider_layout.addWidget(self.freq_slider)
        self.freq_slider_layout.addWidget(self.freq_button)

        self.freq_layout.addWidget(self.freq_label)
        self.freq_layout.addLayout(self.freq_slider_layout)

        self.Nsample_layout = QVBoxLayout()
        self.Nsample_label = QLabel(f'number_of_samples : {N_SAMPLE_INI}')

        self.Nsample_slider = QSlider(Qt.Orientation.Horizontal)
        self.Nsample_slider.setMinimum(MIN_N_SAMPLE)
        self.Nsample_slider.setMaximum(MAX_N_SAMPLE)
        self.Nsample_slider.setValue(N_SAMPLE_INI)
        self.Nsample_slider.valueChanged.connect(self.slider_action)

        self.Nsample_layout.addWidget(self.Nsample_label)
        self.Nsample_layout.addWidget(self.Nsample_slider)

        self.cor_bar = QProgressBar()
        self.cor_bar.setMaximum(100)
        self.cor_bar.setMinimum(0)
        self.cor_bar.setValue(0)

        self.layout.addWidget(self.title)
        self.layout.addLayout(self.freq_layout)
        self.layout.addLayout(self.Nsample_layout)

        self.setLayout(self.layout)

    def slider_action(self):
        sender = self.sender()
        if sender == self.freq_slider:
            self.freq_label.setText(f'frequency : {self.freq_slider.value()} Hz')
        elif sender == self.Nsample_slider:
            self.Nsample_label.setText(f'number_of_samples : {self.Nsample_slider.value()}')
        elif sender == self.freq_button:
            self.params.emit((self.freq_slider.value(), self.Nsample_slider.value()))

    def update_progress(self, value):
        self.cor_bar.setValue(int(value * 100))

    def setEnabled(self, value):
        self.Nsample_slider.setEnabled(value)
        self.freq_slider.setEnabled(value)
        self.freq_button.setEnabled(value)
        if value:
            self.freq_button.setStyleSheet(unactived_button)
        else:
            self.freq_button.setStyleSheet(disabled_button)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CorrelationView()
    window.show()
    sys.exit(app.exec())