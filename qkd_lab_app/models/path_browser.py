import sys

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QWidget, QApplication


class PathBrowser(QWidget):

    file_extracted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.dialog = None
        self.name = ''
        self.path = ''

        if __name__ == '__main__':
            self.chose_file('C:')

    def connect_read(self, signal):
        signal.connect(self.chose_file)

    def chose_file(self, initial_dir):
        """Action performed when a destination file must be chosen"""
        self.dialog = QFileDialog()
        self.dialog.setDirectory(initial_dir)
        self.dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        self.dialog.fileSelected.connect(self.file_selected)
        self.dialog.show()

    def connect_write(self, signal):
        signal.connect(self.write_file)

    def write_file(self, event, initial_dir):
        """Action performed when a destination file must be created, the event MUST be of the form event=message"""
        source, message = event
        if source == "browse":
            self.dialog = QFileDialog()
            self.dialog.setFileMode(QFileDialog.FileMode.Directory)
            self.dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
            self.dialog.setDirectory(initial_dir)
            self.dialog.fileSelected.connect(self.folder_selected)
            self.dialog.show()

        elif source == "name":
            if message != '':
                self.name = message
                self.file_extracted.emit(self.path + r'/' + self.name + '.txt')

    def folder_selected(self, directory):
        self.path = directory
        self.file_extracted.emit(self.path + r'/' + self.name + '.txt')

    def file_selected(self, directory):
        self.path = directory
        self.file_extracted.emit(directory)

    def close(self):
        if self.dialog is not None:
            self.dialog.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    P = PathBrowser()
    P.show()
    sys.exit(app.exec())