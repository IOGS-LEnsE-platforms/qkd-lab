import sys
from multiprocessing.process import parent_process

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class GraphView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()

        self.title = 'graph_title'

        self.counting_rate = 1
        self.data = [0, 3, 5, 7, 2, 4, 3]
        self.x = []

        self.MAX_INDEX = 10

        self.figure = Figure(figsize=(5, 4))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(self.title)

        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        self.update_plot([])

    def display_plot(self):
        self.ax.clear()
        self.ax.plot(self.x, self.data, color = 'r')
        self.ax.set_title(self.title)
        self.ax.set_ylabel("counts")
        self.ax.set_xlabel("delay(ns)")
        self.canvas.draw()
        QApplication.processEvents()

    def update_plot(self, new_data):
        if new_data is None:
            pass
        elif type(new_data) == list:
            self.data += new_data
        else:
            self.data.append(new_data)

        if len(self.data) > self.MAX_INDEX:
            self.data = self.data[-self.MAX_INDEX:]
        self.x = np.linspace(0, len(self.data), len(self.data))
        self.display_plot()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphView()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())