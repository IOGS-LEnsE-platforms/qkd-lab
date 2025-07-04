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

    sample_recieved = pyqtSignal(tuple)
    acquisition_finished = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.timetag_dict = {}
        self.res = 0.013
        self.freq = 20000
        if self.parent is not None:
            self.res = self.parent.res
            #self.freq = self.parent.frequency

        self._running = True
        self.blocked = False
        self.finished = False

        self.path_bob = self.parent.PATH_BOB
        self.path_alice = self.parent.PATH_ALICE
        self.i_alice = self.parent.i_alice

        self.len1, self.len2 = self.concatenate(self.path_bob, self.path_alice)

        self.parent.run_back.connect(self.loop)

    def loop(self, event):
        self.blocked = False

    def extract_data(self, path):
        self.finished = False
        timetag_dict = {}
        try:
            with open(path, 'r') as file:
                print('opened')
                for line in file:
                    if str(line).startswith('%') or str(line).startswith('#'):
                        if '|' in line:
                            inlets = line.split('|')
                            for i in range(len(inlets) - 2):
                                timetag_dict[i] = [[], []]
                        else:
                            continue
                    else:
                        if '   ' in line:
                            param = str(line).split('   ')
                        elif '\t' in line:
                            param = str(line).split('\t')
                        if '' in param:
                            param.remove('')
                        for i in range(len(param)//2):
                            if not i in timetag_dict:
                                timetag_dict[i] = [[], []]
                            tag = param[2*i].strip()
                            time = param[2*i+1].strip()
                            if time != '-':
                                timetag_dict[i][0].append(int(tag))
                                timetag_dict[i][1].append(float(time))
            self.timetag_dict = timetag_dict
        except Exception as e:
            print(f"\033[31mException in CorrelationWorker.extract_data : {e}, chose another file\033[0m")
        self.finished = True
        return timetag_dict

    def concatenate(self, path1, path2):
        self.finished = False
        len1 = 0
        len2 = 0
        try:
            timetag_dict1 = self.extract_data(path1)
            key_max = max(timetag_dict1.keys())
            timetag_dict2 = self.extract_data(path2)
            len1 = len(timetag_dict1)
            len2 = len(timetag_dict2)
            for i in timetag_dict2.keys():
                timetag_dict1[i + key_max + 1] = timetag_dict2[i].copy()
            self.timetag_dict = timetag_dict1
        except Exception as e:
            print(e)
        self.finished = True
        return len1, len2

    def get_data(self, i_bob, i_alice):
        self.finished = False
        cor_data = []
        first_tag = 0
        try:
            tag_bob = self.timetag_dict[i_bob][0]
            tag_alice = self.timetag_dict[i_alice][0]
            time_bob = self.timetag_dict[i_bob][1]
            time_alice = self.timetag_dict[i_alice][1]
            for j, tag in enumerate(tag_bob):
                i = first_tag
                tag2 = -1
                if len(tag_alice) > 0:
                    tag2 = tag_alice[i]
                while tag+1 >= tag2 and i<len(tag_alice) - 1:
                    if tag<=tag2:
                        cross_cor_time = (tag2 - tag)*1e9/self.freq + (time_alice[i] - time_bob[j])/self.res
                        if 0<= cross_cor_time <= 1e9/self.freq:
                            cor_data.append(round(cross_cor_time, 3))
                    else:
                        first_tag = i
                    i += 1
                    tag2 = tag_alice[i]
                if not self._running:
                    break
        except Exception as e:
            print(f"\033[31mException in CorrelationWorker.run : {e} \033[0m")
        self.finished = True
        return cor_data

    def run(self):
        self.finished = False
        try:
            for i_bob in range(4):
                cor_data = self.get_data(i_bob, self.len1 + self.i_alice)
                print(cor_data, i_bob)
                self.sample_recieved.emit(("correlation", cor_data, i_bob))
                self.blocked = True
                while self.blocked:
                    time.sleep(0.001)
                if not self._running:
                    break
            self.finished = True
        except Exception as e:
            self.finished = True

    def stop(self):
        print("stopping correlation")
        try:
            self.parent.run_back.disconnect()
        except TypeError:
            pass

        if not self._running:
            self.finished = True
        self._running = False
        while not self.finished:
            time.sleep(0.001)


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
            print(f"\033[31mException in worker run: {e}, the data will not be saved\033[0m")
        finally:
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
        f.write("%" + "tag   time   "*4 + "\n")
        for i in range(max(len(tag_[0]), len(tag_[1]), len(tag_[2]), len(tag_[3]))):
            for j in range(4):
                if i >= len(tag_[j]):
                    f.write('-\t-\t')
                else:
                    f.write('%s\t%s\t' % (tag_[j][i], time_[j][i]))
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

    def stop(self):
        print("stopping live")
        try:
            self.parent.run_back.disconnect()
        except TypeError:
            pass

        if not self._running:
            self.finished = True
        self._running = False
        while not self.finished:
            time.sleep(0.001)
        self.cpc.closeDevices()

    def init_channels(self):
        self.cpc.ready_devices()