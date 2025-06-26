# -*- coding: utf-8 -*-

"""
Created on Wed Jun 25 11:34:14 2025

@author: CRYPTO_B
"""
import matplotlib.pyplot as plt
import numpy as np
import sys, os

from aurea_cpc import AureaCPC
from aurea_htdc import AureaHTDC

def log_default_params():
    default_params = {}
    config = os.path.dirname(os.path.abspath(".")) + r"\config.txt"
    with open(config, 'r') as config:
        for ligne in config:
            if str(ligne).startswith('%') or str(ligne).startswith('#'):
                continue
            else:
                param = str(ligne).split(';')
                default_params[param[0]] = param[1]
    return default_params

class processModel():
    def __init__(self):
        #self.cpc = AureaCPC
        #self.htdc = AureaHTDC()
        
        self.res = default_params["HTDC_RES"]
        
        self.fichier = os.path.dirname(os.path.abspath(__file__)) + r"\test.txt"
        self.delays = []
         
        self.delays = self.open_data()
        print(self.delays)
        self.tracer_histogramme(self.delays)
        corr = self.filter_noise(self.delays)
        print(corr[0])
        self.tracer_histogramme(corr[1])
        plt.show()
        
        
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
        plt.hist(delays, bins=int((1000)/0.1), range=(0, 1000), edgecolor='black')
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
        print(index_dict)
        delay_maximum = max(index_dict.values())
        for delay in index_dict.keys():
            if index_dict[delay] == delay_maximum:
                return delay*self.res, [delay*self.res for i in range(delay_maximum)]
        return None, None
    
if __name__ == "__main__":
    default_params = log_default_params()
    print(default_params)
    processModel()