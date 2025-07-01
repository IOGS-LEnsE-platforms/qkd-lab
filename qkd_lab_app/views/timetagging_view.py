from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QProgressBar, QSlider, QApplication,
    QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
if __name__ == '__main__':
    import sys, os


class TimeTaggingView(QWidget):

    timetagging = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()

        self.start_timetagging = QPushButton("Start Timetagging")
        self.start_timetagging.clicked.connect(self.update_action)

        self.progress_label = []
        self.progress_bars = []
        self.bar_layouts = []

        self.layout.addWidget(self.start_timetagging)

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
        self.timetagging.emit("timetagging")