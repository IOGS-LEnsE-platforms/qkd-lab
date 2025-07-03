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
from models.aurea_cpc import AureaCPC

class CorrelationWorker(QObject):

    sample_recieved = pyqtSignal(list)
    acquisition_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.htdc = self.parent.htdc
        self._running = True
        self.finished = False

        self.iDev = self.parent.htdc_iDev

        self.CH_BOB = self.parent.CH_BOB

    def run(self):
        self.finished = False
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
        self.finished = True

    def stop(self):
        try:
            self.parent.run_back.disconnect()
        except TypeError:
            pass
        if not self._running:
            self.finished = True
        self._running = False
        while not self.finished:
            time.sleep(0.001)

    def save_data_in_file(self, data, file):
        tag_0, time_0 = self.convert_tag_time(data)
        f = open(file, "w")
        print("Saving data : " + file)
        f.write("Time Tag\n")
        for i in range(len(tag_0)):
            f.write('%s\t%s\n' % (time_0[i], tag_0[i]))

        f.close()

    def convert_tag_time(self, buffer):
        tag_ = []
        time_ = []
        TDC_res = 0.013  # en ns
        for el in buffer:
            tag_.append((el >> 32) & 0xffffffff)
            time_.append(round((el & 0xffffffff) * TDC_res, 3))
        return tag_, time_


class TimeTaggingWorker(QObject):

    sample_recieved = pyqtSignal(tuple)
    acquisition_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.htdc = self.parent.htdc
        self._running = True

        self.CH_BOB = self.parent.CH_BOB
        self.blocked = False
        self.finished = False
        self.stopping = False

        self.iDev = self.parent.htdc_iDev

        self.iDev = 0
        self.data = [[],[],[],[]]
        self.htdc_overload = 1000
        try:
            self.htdc_overload = self.parent.htdc_overload
        except Exception as e:
            print(f"\033[31m{type(self.parent)} has no attribute 'htdc_overload'\033[0m")

        self.init_channels()
        self.parent.run_back.connect(self.loop)

    def loop(self):
        self.blocked = False

    def run(self):
        try:
            self.finished = False
            acquisition_proceeding = True
            for iCh in self.CH_BOB:
                self.sample_recieved.emit(([], iCh, 0))
                if self.htdc.nSampleToRecover[iCh] == -1:
                    acquisition_proceeding &= True
                else:
                    acquisition_proceeding &= self.htdc.nSampleRecovered[iCh] < self.htdc.nSampleToRecover[iCh]

            while self._running and acquisition_proceeding:
                for i, iCh in enumerate(self.CH_BOB):
                    sample = self.htdc.getOneShotTimeTagging(self.iDev, iCh)
                    if sample:
                        if len(sample) > self.htdc_overload:
                            sample = sample[:self.htdc_overload]
                        self.sample_recieved.emit(("time tagging", sample, i, self.htdc.nSampleRecovered[iCh]/self.htdc.nSampleToRecover[iCh]))

                        self.blocked = True
                        while self.blocked and self._running:
                            time.sleep(0.1)

                        self.data[i] += sample
                    else:
                        print(f"No new sample on channel {iCh}")
                acquisition_proceeding = True
                for iCh in self.CH_BOB:
                    if self.htdc.nSampleToRecover[iCh] != -1:
                        acquisition_proceeding &= self.htdc.nSampleRecovered[iCh] < self.htdc.nSampleToRecover[iCh]
                #time.sleep(0.01)

            if not self.stopping:
                self.acquisition_finished.emit("finished")
            self.finished = True
            self.stop()

        except Exception as e:
            print(f"\033[31mException in worker run: {e}\033[0m")
        finally:
            if not self.stopping:
                self.acquisition_finished.emit("finished")
            self.finished = True
            self.stop()

    def stop(self):
        try:
            self.parent.run_back.disconnect()
        except TypeError:
            pass
        print("stopping timetagging")
        self.stopping = True
        if not self._running:
            self.finished = True
        self._running = False
        while not self.finished:
            print("not finished")
            time.sleep(0.001)

    def save_data_in_file(self, data, path):
        #print(self.data)
        self._running = True
        print("writing")
        tag_ = []
        time_ = []
        for i in range(4):
            timetag = self.convert_tag_time(data[i])
            tag_ += [timetag[0]]
            time_ += [timetag[1]]

        f = open(path, "w")
        print("Saving data : " + path)
        f.write("%" + "Time\tTag\t"*4 + "\n")
        for i in range(max(len(tag_[0]), len(tag_[1]), len(tag_[2]), len(tag_[3]))):
            for j in range(4):
                if i >= len(tag_[j]):
                    f.write('-\t-\t')
                else:
                    f.write('%s\t%s\t' % (time_[j][i], tag_[j][i]))
            f.write('\n')

        f.close()
        self._running = False
        self.finished = True

    def convert_tag_time(self, buffer):
        tag_ = []
        time_ = []
        TDC_res = 0.013  # en ns
        for el in buffer:
            tag_.append((el >> 32) & 0xffffffff)
            time_.append(round((el & 0xffffffff) * TDC_res, 3))
        return tag_, time_

    def init_channels(self):
        for iCh in self.CH_BOB:
            self.htdc.ready_channel_timetagging(self.iDev, iCh)


class liveWorker(QObject):

    sample_recieved = pyqtSignal(tuple)
    acquisition_finished = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.cpc = self.parent.cpc
        self.cpc_iDev = self.parent.cpc_iDev

        self._running = True
        self.blocked = False
        self.finished = False

        self.init_channels()
        self.parent.run_back.connect(self.loop)

    def loop(self):
        self.blocked = False

    def run(self):
        try:
            self.finished = False
            while self._running:
                for i, iDev in enumerate(self.cpc_iDev):
                    _, cnt = self.cpc.getData(iDev)
                    self.sample_recieved.emit(("live", [cnt], i))

                    self.blocked = True
                    while self.blocked and self._running:
                        time.sleep(0.001)
                time.sleep(0.01)
            self.finished = True
            #self.acquisition_finished.emit("finished")
        except Exception as e:
            print(f"\033[31mException in worker run: {e}\033[0m")
        finally:
            self._running = False
            self.acquisition_finished.emit("finished")

    def stop(self):
        print("stopping live")
        try:
            self.parent.run_back.disconnect()
        except TypeError:
            pass

        if not self._running:
            self.finished = True
        self._running = False
        self.cpc.closeDevices()
        while not self.finished:
            time.sleep(0.001)

    def init_channels(self):
        self.cpc.ready_devices()