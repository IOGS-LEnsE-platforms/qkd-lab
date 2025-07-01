'''
These objects are the workers that conduct in-real-time actions in the interface. They are linked to a thread in
the main controller.
The three workers correspond to three acquisition modes:
 - live mode : A single CPC's real-time value is displayed on a line graph
 - correlation mode : two channels of the digital correlator are compared and the result of the correlation is displayed
   in a histogram display
 - single channel mode : the emitter's (Alice) and receiver's (Bob) signals are compared one-to-one around the
   correlator's expected value. the presence or absence of a signal is detected and stored.
'''

import sys, os
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QObject

sys.path.append(os.path.abspath("."))
import time

from models.aurea_htdc import AureaHTDC

class CorrelationWorker(QObject):

    sample_recieved = pyqtSignal(list)
    acquisition_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.htdc = self.parent.htdc
        self._running = True

        self.iDev = self.parent.iDev

    def run(self):
        if self.htdc.nSampleToRecover == -1:
            acquisition_proceeding = True
        else:
            acquisition_proceeding = self.htdc.nSampleRecovered < self.htdc.nSampleToRecover
        while self._running and acquisition_proceeding:
            sample = self.htdc.getOneShotCorrelation(self.iDev)
            self.sample_recieved.emit(f"correlation={sample}")
            if self.htdc.nSampleToRecover != -1:
                acquisition_proceeding = self.htdc.nSampleRecovered < self.htdc.nSampleToRecover
        self.acquisition_finished.emit("finished")
        self._running = False

    def stop(self):
        self._running = False

    def save_data_in_file(self, data, file):
        tag_0, time_0 = self.convert_tag_time(data)
        f = open(file, "w")
        print("Saving data : " + file)
        f.write("%Time Tag\n")
        for i in range(len(tag_0)):
            f.write('%s\t%s\n' % (time_0[i], tag_0[i]))

        f.close()

    def convert_tag_time(self, buffer):
        '''
        XXXXXXXXYYYYY -> XXXXXXXX + 000YYYYY
                           time       tag
        '''
        tag_ = []
        time_ = []
        TDC_res = 0.013  # en ns
        for el in buffer:
            tag_.append((el >> 32) & 0xffffffff)
            time_.append(round((el & 0xffffffff) * TDC_res, 3))
        return tag_, time_


class TimeTaggingWorker(QObject):

    sample_recieved = pyqtSignal(str)
    acquisition_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.htdc = self.parent.htdc
        self._running = True

        self.CH_BOB = [1, 2, 4, 8]

        self.iDev = self.parent.iDev

        self.iDev = 0

    def run(self):
        try:
            if self.htdc.nSampleToRecover == -1:
                acquisition_proceeding = True
            else:
                acquisition_proceeding = self.htdc.nSampleRecovered < self.htdc.nSampleToRecover

            while self._running and acquisition_proceeding:
                for iCh in self.CH_BOB:
                    sample = self.htdc.getOneShotTimeTagging(self.iDev, iCh)
                    if sample:
                        self.sample_recieved.emit((sample, iCh))
                    else:
                        print(f"No new sample on channel {iCh}")
                if self.htdc.nSampleToRecover != -1:
                    acquisition_proceeding = self.htdc.nSampleRecovered < self.htdc.nSampleToRecover
                time.sleep(0.01)

        except Exception as e:
            print(f"Exception in worker run: {e}")
        finally:
            self.acquisition_finished.emit("finished")
            self._running = False

    def stop(self):
        self._running = False

    def save_data_in_file(self, data, file):
        tag_0, time_0 = self.convert_tag_time(data)
        f = open(file, "w")
        print("Saving data : " + file)
        f.write("%Time Tag\n")
        for i in range(len(tag_0)):
            f.write('%s\t%s\n' % (time_0[i], tag_0[i]))

        f.close()

    def convert_tag_time(self, buffer):
        '''
        XXXXXXXXYYYYY -> XXXXXXXX + 000YYYYY
                           time       tag
        '''
        tag_ = []
        time_ = []
        TDC_res = 0.013  # en ns
        for el in buffer:
            tag_.append((el >> 32) & 0xffffffff)
            time_.append(round((el & 0xffffffff) * TDC_res, 3))
        return tag_, time_