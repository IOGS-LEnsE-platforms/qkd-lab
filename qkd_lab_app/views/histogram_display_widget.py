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
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class HistogramDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.data = []
        
        self.title = 'title_histogram'
        
        ### Paramètres de l'histogramme
        self.bins = 100
        self.MIN_DELAY = 0
        self.MAX_DELAY = 10
        

        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot_histogram()

    def plot_histogram(self):
        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.hist(self.data, bins=self.bins, range = (self.MIN_DELAY, self.MAX_DELAY), color='black')
        ax.set_title(self.title)
        self.canvas.draw()
        
    def update_data(self, new_data):
        # Ajoute des données à l'existante
        self.data = np.append(self.data, new_data)
        self.plot_histogram()
    
    def change_title(self, title):
        self.title = title
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HistogramDisplayWidget()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())