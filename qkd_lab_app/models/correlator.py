from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton

import sys, os
sys.path.append(os.path.abspath(".."))

from views.histogram_display_widget import HistogramDisplayWidget

class Correlator(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.timetag_dict = {}
        self.res = 0.013
        self.freq = 20000
        if self.parent is not None:
            self.res = self.parent.res
            self.freq = self.parent.frequency

        if __name__ == "__main__":
            path = r'C:\Users\CRYPTO_B\Documents\GitHub\qkd-lab\qkd_lab_app\models\test.txt'
            self.timetag_dict = self.extract_data(path)
            self.layout = QHBoxLayout()
            self.data_button = QPushButton('Extract Data')
            self.data_button.clicked.connect(self.button_action)
            self.layout.addWidget(self.data_button)
            self.histogram = HistogramDisplayWidget()
            self.layout.addWidget(self.histogram)

            self.setLayout(self.layout)

    def extract_data(self, path):
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
            print(f"\033[31mException in Correlator : {e}, chose another file\033[0m")
        return timetag_dict

    def concatenate(self, path1, path2):
        timetag_dict1 = self.extract_data(path1)
        timetag_dict2 = self.extract_data(path2)
        key_max = max(timetag_dict1.keys())
        for i in timetag_dict2.keys():
            timetag_dict1[i+key_max] = timetag_dict2[i].copy()
        self.timetag_dict = timetag_dict1
        return timetag_dict1

    def find_cor_data(self, i_bob, i_alice):
        cor_data = []
        first_tag = 0
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
                    time = (tag2 - tag)*1e9/self.freq + (time_alice[i] - time_bob[j])/self.res
                    if 0<= time <= 1e9/self.freq:
                        cor_data.append(round(time, 3))
                else:
                    first_tag = i
                i += 1
                tag2 = tag_alice[i]
        return cor_data

    def button_action(self):
        cor_data = self.find_cor_data(1, 2)
        print(cor_data)
        self.histogram.update_data(cor_data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    C = Correlator()
    C.show()
    sys.exit(app.exec())