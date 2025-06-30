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
        self.res = 0.013 #self.parent.res
        self.hist_dict = {}#{self.MIN_DELAY/self.res:0.001, self.MAX_DELAY/self.res:0.001}

        self.figure = Figure(figsize=(5, 4))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(self.title)

        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot_histogram()
        #self.update_data([1*self.res, 3*self.res+0.001])

    """def plot_histogram(self):
        self.ax.clear()
        self.ax.bar(self.bin_centers, self.hist_counts, width=(self.bin_edges[1]-self.bin_edges[0]), color='black', align='center')
        #self.ax.set_title(self.title)
        self.canvas.draw()

    def update_data(self, new_data):
        filtered = [x for x in new_data if self.MIN_DELAY <= x <= self.MAX_DELAY]
        bin_indices = np.searchsorted(self.bin_edges, filtered, side='right') - 1
        for i in bin_indices:
            if 0 <= i < self.bins:
                self.hist_counts[i] += 1
        self.plot_histogram()
        QApplication.processEvents()"""

    def plot_histogram(self):
        self.ax.clear()
        x = [t*self.res for t in self.hist_dict.keys()]
        y = [value for value in self.hist_dict.values()]

        self.ax.bar(x, y, width = self.MAX_DELAY*self.res/5, color='black', align='center')
        self.ax.set_title(self.title)
        self.canvas.draw()
        QApplication.processEvents()

    def update_data(self, new_data):
        '''Takes in the set of new TIME values and updates the histogram by searching the nearest bin in a range of res/2'''
        for x in new_data:
            x = int(x/self.res)
            #in_dict = False

            if x in self.hist_dict.keys():
                self.hist_dict[x] += 1
            else:
                self.hist_dict[x] = 1

            """for k in self.hist_dict.keys():
                if abs(x-k) <= 1/2:
                    self.hist_dict[k] += 1
                    in_dict = True
                    break
            
            if not in_dict:
                self.hist_dict[x] += 1"""
        self.plot_histogram()


    
    def change_title(self, title):
        self.title = title

    def clear(self):
        self.data = []
        self.ax.clear()

    def find_maximum(self):
        i_max = max(self.hist_dict.values())
        k_max = 0
        new_dict = {0: 0.001, self.MAX_DELAY / self.res: 0.001}
        for k in self.hist_dict.keys():
            if self.hist_dict[k] == i_max:
                new_dict[k] = i_max
        self.hist_dict = new_dict
        self.plot_histogram()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HistogramDisplayWidget()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())