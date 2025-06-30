# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 11:58:10 2025

@author: CRYPTO_B
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication, QVBoxLayout
import sys, os

sys.path.append(os.path.abspath(".."))

from models.process_model import ProcessModel
from views.histogram_display_widget import HistogramDisplayWidget

class correlationController(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.frequency = 5000000
        self.MAX_DELAY = int(1e09 / self.frequency)
        self.Npoints = 300 #Number of points on the histogram, avoids exceedingly long processes at low frequencies
        self.res = 0.02
        
        self.layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        
        self.model = ProcessModel(self)
        
        self.corr_button = QPushButton('lancer l\'acquisition')
        self.corr_button.clicked.connect(self.model.htdc.getCorrelation)
        
        self.stop_button = QPushButton('stopper l\'acquisition')
        self.stop_button.clicked.connect(self.stopAcquisition)
        
        self.histogram = HistogramDisplayWidget(self)
        
        self.left_layout.addWidget(self.corr_button)
        self.left_layout.addWidget(self.stop_button)
        
        self.layout.addLayout(self.left_layout)
        self.layout.addWidget(self.histogram)
        
        self.setLayout(self.layout)
        
    def update_data(self, data):
        self.histogram.update_data(data)

    def stopAcquisition(self):
        self.model.htdc.stopAcquisition()
        QApplication.processEvents()

    def display_maximum(self):
        self.histogram.find_maximum()

    def resizeEvent(self, event):
        QApplication.processEvents()

if __name__ == "__main__":
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = correlationController()
        window.show()
        sys.exit(app.exec())