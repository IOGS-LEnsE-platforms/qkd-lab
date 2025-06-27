# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 11:27:54 2025

@author: CRYPTO_B
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 10:56:27 2025

@author: CRYPTO_B
"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class HistogramDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        
        self.data = []
        
        self.title = 'title_histogram'

        self.hist_dict = {}
        
        ### Paramètres de l'histogramme
        self.MIN_DELAY = 0
        self.MAX_DELAY = self.parent.MAX_DELAY
        self.res = self.parent.res
        self.bins = int((self.MAX_DELAY - self.MIN_DELAY) / self.res)#self.parent.Npoints

        self.bin_edges = np.linspace(self.MIN_DELAY, self.MAX_DELAY, self.bins + 1)
        self.hist_counts = np.zeros(self.bins, dtype=int)
        self.bin_centers = (self.bin_edges[:-1] + self.bin_edges[1:]) / 2

        self.figure = Figure(figsize=(5, 4))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(self.title)

        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot_histogram()

    def plot_histogram(self):
        self.ax.clear()
        self.ax.bar(self.bin_centers, self.hist_counts, width=(self.bin_edges[1]-self.bin_edges[0]), color='black', align='center')
        self.ax.set_title(self.title)
        self.canvas.draw()

    def update_data(self, new_data):
        filtered = [x for x in new_data if self.MIN_DELAY <= x <= self.MAX_DELAY]
        bin_indices = np.searchsorted(self.bin_edges, filtered, side='right') - 1
        for i in bin_indices:
            if 0 <= i < self.bins:
                self.hist_counts[i] += 1
        self.plot_histogram()
        QApplication.processEvents()
    
    def change_title(self, title):
        self.title = title

    def clear(self):
        self.data = []
        self.ax.clear()

    def find_maximum(self):
        i_max = self.hist_counts.argmax()
        cor_max = self.hist_counts.max()
        self.hist_counts = np.zeros(self.bins, dtype=int)
        self.hist_counts[i_max] = cor_max
        self.plot_histogram()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HistogramDisplayWidget()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())