from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QProgressBar, QSlider, QApplication,
    QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy.css import *

if __name__ == '__main__':
    import sys, os


class TimeTaggingView(QWidget):

    timetagging = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()

        self.title = QLabel("time_tagging_title")
        self.layout.addWidget(self.title)

        self.start_timetagging = QPushButton("Start Timetagging")
        self.layout.addWidget(self.start_timetagging)
        self.start_timetagging.clicked.connect(self.update_action)
        self.start_timetagging.setStyleSheet(unactived_button)
        self.start_timetagging.setFixedHeight(BUTTON_HEIGHT)

        self.stop_timetagging = QPushButton("Stop Timetagging")
        self.layout.addWidget(self.stop_timetagging)
        self.stop_timetagging.clicked.connect(self.update_action)
        self.stop_timetagging.setStyleSheet(unactived_button)
        self.stop_timetagging.setFixedHeight(BUTTON_HEIGHT)

        self.progress_label = []
        self.progress_bars = []
        self.bar_layouts = []

        for i in range(4):
            self.bar_layouts.append(QHBoxLayout())

            self.progress_bars.append(QProgressBar())
            self.progress_bars[i].setRange(0, 100)
            self.progress_bars[i].setValue(0)

            self.progress_label.append(QLabel(f"Ch{i+1}"))

            self.bar_layouts[i].addWidget(self.progress_label[i])
            self.bar_layouts[i].addWidget(self.progress_bars[i])
            self.layout.addLayout(self.bar_layouts[i])

        self.setLayout(self.layout)

    def update_action(self):
        sender = self.sender()
        if sender == self.start_timetagging:
            self.timetagging.emit("start")
        elif sender == self.stop_timetagging:
            self.timetagging.emit("stop")

    def update_progress(self, value, i):
        """update progress bar corresponding to the chanel index with a value between 0 and 1"""
        print("progress update done")
        if value > 1:
            value = 1
        self.progress_bars[i].setValue(int(value * 100))

    def setEnabled(self, value:bool):
        self.start_timetagging.setEnabled(value)
        self.stop_timetagging.setEnabled(value)
        if value:
            self.start_timetagging.setStyleSheet(unactived_button)
            self.stop_timetagging.setStyleSheet(unactived_button)
        else:
            self.start_timetagging.setStyleSheet(disabled_button)
            self.stop_timetagging.setStyleSheet(disabled_button)