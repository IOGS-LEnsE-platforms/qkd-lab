# -*- coding: utf-8 -*-

"""
Created on Wed Jun 25 11:34:14 2025

@author: CRYPTO_B
"""
import matplotlib.pyplot as plt
import numpy as np
import sys, os

sys.path.append(os.path.abspath(".."))

from aurea_cpc import AureaCPC
from aurea_htdc import AureaHTDC
from views.histo_display import HistogramDisplayWidget

def log_default_params():
    default_params = {}
    config = os.path.dirname(os.path.abspath(".")) + r"\config.txt"
    with open(config, 'r') as default:
        for ligne in default:
            print(f"ligne = {ligne}")
            if str(ligne).startswith('%') or str(ligne).startswith('#'):
                continue
            else:
                param = str(ligne).split(';')
                if len(param) == 2:
                    default_params[param[0].strip()] = param[1].strip()
    return default_params

class processModel():
    def __init__(self):
        self.frequency = 10000000
        self.N_SAMPLE = 20000000
        self.MAX_DELAY = int(1e09/self.frequency)
        self.histogram = HistogramDisplayWidget(self)
        #self.histogram.show()
        
        #self.cpc = AureaCPC
        self.htdc = AureaHTDC(self)
        
        self.res = 0.1#float(default_params["HTDC_RES"])
        print(self.res)
        
        self.fichier = os.path.dirname(os.path.abspath(__file__)) + r"\test.txt"
        self.delays = []
        
        
        """self.delays = self.open_data()
        #print(self.delays)
        self.tracer_histogramme(self.delays)
        corr = self.filter_noise(self.delays)
        print(corr[0])
        self.tracer_histogramme(corr[1])
        plt.show()"""
        
        
    def open_data(self):
        delays = []
        with open(self.fichier, 'r') as f:
            for ligne in f:
                # Ignorer les lignes d'en-tête
                if ligne.startswith('%'):
                    continue
                # Ajouter les valeurs numériques à la liste
                try:
                    delays.append(float(ligne.strip()))
                except ValueError:
                    pass  # Ignorer les lignes qui ne peuvent pas être converties en float
        return delays
        
    def tracer_histogramme(self, delays):
        plt.figure(figsize=(10, 6))
        plt.hist(delays, bins=int(self.MAX_DELAY), range=(0, self.MAX_DELAY), edgecolor='black')
        plt.xlabel("Delay [ns]")
        plt.ylabel("Number of events")
        plt.title("Cross corrleation")
    
    def filter_noise(self, delays):
        '''extracts the spike in the histogram (list of delays) and returns its delay value
        and the new histogram'''
        delays_cor = np.array(delays.copy())
        #delays_cor[delays_cor<100]
        index_dict = {}
        for delay in delays_cor:
            if not int(delay/self.res) in index_dict.keys():
                index_dict[int(delay/self.res)] = 1
            else:
                index_dict[int(delay/self.res)] += 1
        maximums_list = []
        histo_list = []
        values = index_dict.values()
        if len(values) != 0:
            delay_maximum = max(values)
            print(delay_maximum)
        for delay in index_dict.keys():
            if index_dict[delay] == delay_maximum and delay_maximum > 1:
                maximums_list.append(delay*self.res)#, [delay*self.res for i in range(delay_maximum)]
        for element in maximums_list:
            histo_list += [element] * delay_maximum
        return maximums_list, histo_list
    
    def update_histogram(self, data):
        self.histogram.update_data(data)

    
if __name__ == "__main__":
    default_params = log_default_params()
    print(default_params)
    processModel()