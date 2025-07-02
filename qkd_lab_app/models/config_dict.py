from PyQt6.QtCore import QObject

class ConfigDict():
    def __init__(self, path):
        super().__init__()
        self.default_params = {}
        self.log_default_params(path)

        self.numberOfCPCs = 7
        if "Number of CPCs" in self.default_params:
            self.numberOfCPCs = int(self.default_params["Number of CPCs"])
        self.serial_dict = self.get_CPC_serial_numbers()

    def log_default_params(self, path):
        config = path + r"\config.txt"
        with open(config, 'r') as default:
            for ligne in default:
                if str(ligne).startswith('%') or str(ligne).startswith('#'):
                    continue
                else:
                    param = str(ligne).split(';')
                    if len(param) == 2:
                        self.default_params[param[0].strip()] = param[1].strip()

    def get_CPC_serial_numbers(self):
        serial_numbers = {}
        for i in range(self.numberOfCPCs):
            if "CPC_" + str(i+1) in self.default_params.keys():
                serial_numbers[i+1] = self.default_params["CPC_" + str(i+1)]
        return serial_numbers