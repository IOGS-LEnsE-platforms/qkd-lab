from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QProgressBar, QSlider, QApplication,
    QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
if __name__ == '__main__':
    import sys, os


class FreeCPCView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        MAX_TIMESPAN = 5000
        MIN_TIMESPAN = 10
        INI_TIMESPAN = 500

        self.devices_list = ['2', '3', '4', '5', '6', '7']

        self.layout = QVBoxLayout()

        self.title = QLabel("free_cpc_title")

        self.index_layout = QHBoxLayout()
        self.device_index_label = QLabel(f"Device index : ")
        self.index_layout.addWidget(self.device_index_label)

        self.combo_box = QComboBox()
        self.combo_box.addItems(self.devices_list)
        self.index_layout.addWidget(self.combo_box)
        self.combo_box.currentIndexChanged.connect(self.update_action)

        self.spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.timespan_label = QLabel(f"Graph time span (ns) : {INI_TIMESPAN}")

        self.timespan_slider = QSlider(Qt.Orientation.Horizontal)
        self.timespan_slider.setMinimum(MIN_TIMESPAN)
        self.timespan_slider.setMaximum(MAX_TIMESPAN)
        self.timespan_slider.setValue(INI_TIMESPAN)
        self.timespan_slider.valueChanged.connect(self.slider_action)

        self.start_live = QPushButton("Start Live")

        self.layout.addWidget(self.title)
        self.layout.addLayout(self.index_layout)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.timespan_label)
        self.layout.addWidget(self.timespan_slider)

        self.setLayout(self.layout)

    def find_devices_list(self, indexes, devices_dict):
        self.devices_list = []
        for i in indexes:
            self.devices_list.append(str(i) + ':' + str(devices_dict[i]))
        self.combo_box.clear()
        self.combo_box.addItems(self.devices_list)

    def slider_action(self):
        self.timespan_label.setText(f"Graph time span (ns) : {self.timespan_slider.value()}")

    def update_action(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FreeCPCView()
    window.show()
    sys.exit(app.exec())