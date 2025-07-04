from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QProgressBar, QSlider, QApplication, \
    QLineEdit, QCheckBox
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

        self.correlation_enabled = False

        self.title = QLabel('correlation_title')

        self.Nmatch_label = QLabel(f'number_of_time_matches : {0}')

        self.start_cor_button = QPushButton('Start Correlation')
        self.start_cor_button.setStyleSheet(unactived_button)
        self.start_cor_button.setFixedHeight(BUTTON_HEIGHT)
        self.start_cor_button.clicked.connect(self.start_action)

        self.bob_layout = QVBoxLayout()
        self.bob_title = QLabel('bob_title')
        self.bob_title.setStyleSheet(styleH2)

        self.bob_sub_layout = QHBoxLayout()
        self.bob_path_edit = QLineEdit()
        self.bob_path_edit.setEnabled(False)
        self.bob_browse = QPushButton('Browse')
        self.bob_browse.setStyleSheet(unactived_button)
        self.bob_browse.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.bob_browse.clicked.connect(self.file_action)

        self.bob_sub_layout.addWidget(QLabel('Path : '))
        self.bob_sub_layout.addWidget(self.bob_path_edit)
        self.bob_sub_layout.addWidget(self.bob_browse)

        self.bob_layout.addWidget(self.bob_title)
        self.bob_layout.addLayout(self.bob_sub_layout)

        self.alice_layout = QVBoxLayout()
        self.alice_title = QLabel('alice_title')
        self.alice_title.setStyleSheet(styleH2)

        self.alice_sub_layout = QHBoxLayout()
        self.alice_path_edit = QLineEdit()
        self.alice_path_edit.setEnabled(False)
        self.alice_browse = QPushButton('Browse')
        self.alice_browse.setStyleSheet(unactived_button)
        self.alice_browse.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.alice_browse.clicked.connect(self.file_action)

        self.alice_sub_layout.addWidget(QLabel('Path : '))
        self.alice_sub_layout.addWidget(self.alice_path_edit)
        self.alice_sub_layout.addWidget(self.alice_browse)

        self.alice_checkbox_layout = QHBoxLayout()
        self.alice_ch1_checkbox = QCheckBox()
        self.alice_ch1_checkbox.stateChanged.connect(self.checkbox_action)
        self.alice_ch1_checkbox.blockSignals(True)
        self.alice_ch1_checkbox.setChecked(True)
        self.alice_ch1_checkbox.blockSignals(False)
        self.alice_ch1_label = QLabel("CH1 : ")
        self.alice_ch2_checkbox = QCheckBox()
        self.alice_ch2_checkbox.stateChanged.connect(self.checkbox_action)
        self.alice_ch2_label = QLabel("CH2 : ")

        self.alice_checkbox_layout.addWidget(self.alice_ch1_label)
        self.alice_checkbox_layout.addWidget(self.alice_ch1_checkbox)
        self.alice_checkbox_layout.addWidget(self.alice_ch2_label)
        self.alice_checkbox_layout.addWidget(self.alice_ch2_checkbox)

        self.alice_layout.addWidget(self.alice_title)
        self.alice_layout.addLayout(self.alice_sub_layout)
        self.alice_layout.addLayout(self.alice_checkbox_layout)

        self.layout.addWidget(self.title)
        self.layout.addLayout(self.bob_layout)
        self.layout.addLayout(self.alice_layout)
        self.layout.addWidget(self.start_cor_button)

        self.setLayout(self.layout)

    def start_action(self):
        sender = self.sender()
        if sender == self.start_cor_button:
            self.correlation.emit("correlation")

    def checkbox_action(self):
        sender = self.sender()
        if sender == self.alice_ch1_checkbox:
            if self.alice_ch1_checkbox.isChecked():
                self.alice_ch2_checkbox.blockSignals(True)
                self.alice_ch2_checkbox.setChecked(False)
                self.alice_ch2_checkbox.blockSignals(False)
            self.correlation.emit('CH1')
        elif sender == self.alice_ch2_checkbox:
            if self.alice_ch2_checkbox.isChecked():
                self.alice_ch1_checkbox.blockSignals(True)
                self.alice_ch1_checkbox.setChecked(False)
                self.alice_ch1_checkbox.blockSignals(False)
            self.correlation.emit('CH2')

    def file_action(self):
        sender = self.sender()
        if sender == self.bob_browse:
            self.correlation.emit("browse bob")
        if sender == self.alice_browse:
            self.correlation.emit("browse alice")

    def set_path(self, path:str, to_which:bool):
        '''to_which = True : bob, to_which = False, alice'''
        if to_which:
            self.bob_path_edit.setText(path)
        else:
            self.alice_path_edit.setText(path)

    def setEnabled(self, value):
        self.alice_ch1_checkbox.setEnabled(value)
        self.alice_ch2_checkbox.setEnabled(value)
        self.alice_browse.setEnabled(value)
        self.bob_browse.setEnabled(value)
        if self.correlation_enabled:
            self.start_cor_button.setEnabled(value)
            if value:
                self.start_cor_button.setStyleSheet(unactived_button)
            else:
                self.start_cor_button.setStyleSheet(disabled_button)
        else:
            self.start_cor_button.setEnabled(False)
            self.start_cor_button.setStyleSheet(disabled_button)

    def set_correlation_enabled(self, value):
        self.correlation_enabled = value
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

        MAX_FREQUENCY = self.parent.max_freq
        MIN_FREQUENCY = self.parent.min_freq
        FREQ_INI_VALUE = self.parent.frequency

        MIN_N_SAMPLE = self.parent.min_num_samples
        MAX_N_SAMPLE = self.parent.max_num_samples
        N_SAMPLE_INI = self.parent.N_SAMPLE

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