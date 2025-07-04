from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QProgressBar, QSlider, QApplication,
    QComboBox, QSpacerItem, QSizePolicy, QGridLayout, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
if __name__ == '__main__':
    import sys, os
from lensepy.css import *


class FreeCPCView(QWidget):

    live_signal = pyqtSignal(tuple)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        MAX_COUNTS = 5000000
        MIN_COUNTS = 10
        INI_COUNTS = 500
        if self.parent is not None:
            MIN_COUNTS = self.parent.min_graph_span
            MAX_COUNTS = self.parent.max_graph_span
            INI_COUNTS = self.parent.ini_graph_span

        self.devices_list = ['2', '3', '4', '5', '6', '7']
        self.stack = []
        self.available_indexes = []

        self.layout = QVBoxLayout()

        self.title = QLabel("free_cpc_title")

        self.index_layout = QHBoxLayout()
        self.device_index_label = QLabel(f"Available devices : ")
        self.index_layout.addWidget(self.device_index_label)

        self.combo_box = QComboBox()
        self.combo_box.addItems(self.devices_list)
        self.index_layout.addWidget(self.combo_box)

        self.checkboxes_layout = QGridLayout()
        self.checkboxes_layout.setRowStretch(0, 1)
        self.checkboxes_layout.setRowStretch(1, 1)
        self.checkboxes_layout.setColumnStretch(0, 1)
        self.checkboxes_layout.setColumnStretch(1, 1)
        self.checkboxes_layout.setColumnStretch(2, 1)

        self.checkbox_dict = {}
        self.mini_checkbox_layout = []
        for i in range(len(self.devices_list)):
            i = int(i)
            self.checkbox_dict[i] = QCheckBox()
            self.checkbox_dict[i].stateChanged.connect(self.update_checkbox_display)

            self.mini_checkbox_layout.append(QHBoxLayout())
            label = QLabel(self.devices_list[i])
            label.setMaximumWidth(30)
            self.mini_checkbox_layout[-1].addWidget(label)
            self.mini_checkbox_layout[-1].addWidget(self.checkbox_dict[i])
            self.checkboxes_layout.addLayout(self.mini_checkbox_layout[-1], i%2, i//2)

        self.spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.timespan_label = QLabel(f"Graph max counts : {INI_COUNTS}")

        self.timespan_slider = QSlider(Qt.Orientation.Horizontal)
        self.timespan_slider.setMinimum(MIN_COUNTS)
        self.timespan_slider.setMaximum(MAX_COUNTS)
        self.timespan_slider.setValue(INI_COUNTS)
        self.timespan_slider.valueChanged.connect(self.slider_action)

        self.start_live = QPushButton("Start Live")
        self.start_live.clicked.connect(self.update_action)
        self.start_live.setStyleSheet(unactived_button)
        self.start_live.setFixedHeight(BUTTON_HEIGHT)

        self.layout.addWidget(self.title)
        self.layout.addLayout(self.index_layout)
        self.layout.addLayout(self.checkboxes_layout)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.timespan_label)
        self.layout.addWidget(self.timespan_slider)
        self.layout.addWidget(self.start_live)

        self.setLayout(self.layout)

        self.init_checkbox_display({2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0})

    def find_devices_list(self, devices_dict):
        self.devices_list = []
        devices_list_text = []
        for i in devices_dict.keys():
            self.devices_list.append(str(i))
            devices_list_text.append(str(i) + ':' + str(devices_dict[i]))
        self.combo_box.clear()
        self.combo_box.addItems(devices_list_text)

    def slider_action(self):
        self.timespan_label.setText(f"Graph max counts : {self.timespan_slider.value()}")
        self.live_signal.emit(("graph span", self.timespan_slider.value()))

    def update_action(self):
        print("starting live")
        self.live_signal.emit(("start",))

    def init_checkbox_display(self, devices_dict):
        '''draws the checkbox layout from a dict of the form {i : serial_no}'''
        self.clear_layout(self.checkboxes_layout)

        self.checkbox_dict = {}
        self.mini_checkbox_layout = []
        self.available_indexes = []

        devices_list = list(devices_dict.keys())

        for i in range(len(devices_list)):
            device_index = int(devices_list[i])
            self.checkbox_dict[device_index] = QCheckBox()
            self.checkbox_dict[device_index].setEnabled(False)
            for j in self.devices_list:
                if device_index == int(j):
                    self.checkbox_dict[device_index].setEnabled(True)
                    self.available_indexes.append(device_index)
            self.checkbox_dict[device_index].stateChanged.connect(self.update_checkbox_display)

            mini_layout = QHBoxLayout()
            label = QLabel(str(devices_list[i]))
            label.setMaximumWidth(30)
            mini_layout.addWidget(label)
            mini_layout.addWidget(self.checkbox_dict[device_index])
            self.mini_checkbox_layout.append(mini_layout)
            self.checkboxes_layout.addLayout(mini_layout, i % 2, i // 2)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                child_layout = item.layout()
                if widget is not None:
                    widget.setParent(None)
                elif child_layout is not None:
                    self.clear_layout(child_layout)

    def update_checkbox_display(self):
        sender = self.sender()
        for i in self.checkbox_dict.keys():
            if sender == self.checkbox_dict[i] and not i in self.stack and self.checkbox_dict[i].isChecked():
                if len(self.stack) == 4:
                    index = self.stack.pop(0)
                    self.checkbox_dict[index].blockSignals(True)
                    self.checkbox_dict[index].setChecked(False)
                    self.checkbox_dict[index].blockSignals(False)
                self.stack.append(i)
                print(self.stack)
                self.live_signal.emit(("checkbox", self.stack))
                break
            elif sender == self.checkbox_dict[i] and not self.checkbox_dict[i].isChecked():
                if i in self.stack:
                    self.stack.remove(i)
                print(self.stack)
                self.live_signal.emit(("checkbox", self.stack))
                break

    def setEnabled(self, value:bool):
        if not value:
            for checkbox in self.checkbox_dict.values():
                checkbox.setEnabled(False)
        else:
            for i in self.available_indexes:
                self.checkbox_dict[i].setEnabled(True)
        self.timespan_slider.setEnabled(value)
        self.start_live.setEnabled(value)
        if value:
            self.start_live.setStyleSheet(unactived_button)
        else:
            self.start_live.setStyleSheet(disabled_button)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FreeCPCView()
    window.show()
    sys.exit(app.exec())