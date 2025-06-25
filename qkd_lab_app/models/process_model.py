# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 11:34:14 2025

@author: CRYPTO_B
"""
from aurea_cpc import AureaCPC
import aurea_htdc as AureaHTDC

class processModel():
    def __init__(self):
        self.cpc = AureaCPC()
        self.htdc = AureaHTDC()
    
    def filter_noise(self, delays):
        '''extracts the spike in the histogram (list of delays) and returns its delay value
        and the new histogram'''
        delays_cor = np.array(delays.copy())
        delays_cor[delays_cor<100]
        index_dict = {}
        for delay in delays_cor:
            if not delay in index_dict.keys():
                index_dict[delay] = 1
            else:
                index_dict[delay] += 1
        delay_maximum = max(index_dict.values())
        for delay in index_dict.keys():
            if index_dict[delay] == delay_maximum:
                return delay, [delay for i in range(delay_maximum)]
        return None, None