import sys
import logging

from PyQt4 import QtGui, QtCore

from xplan import XPlan
from excel import Excel

# Import the interface class
import xplanUI

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s') # include timestamp


class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        self.function(*self.args, **self.kwargs)
        return


class XplanTool(QtGui.QDialog, xplanUI.Ui_Dialog):
    def __init__(self, parent=None):
        super(XplanTool, self).__init__(parent)
        self.setupUi(self)
        QtCore.QObject.connect(self, QtCore.SIGNAL("enable_input()"), self.enable_input)

    def generate_excel(self):
        p = XPlan()
        if p.load_zip():
            x = Excel()
            p.extract_objects()
            p.generate_obj_file()
            x.generate_xls_file(p.get_xplan_object())
        logging.info("[Complete]\n\n")
        self.emit(QtCore.SIGNAL('enable_input()'))

    def generate_zip(self):
        p = XPlan()
        x = Excel()
        p.generate_zip_file(x.get_xplan_object())
        logging.info("[Complete]\n\n")
        self.emit(QtCore.SIGNAL('enable_input()'))

    def enable_input(self):
        self.pushButton_excel.setEnabled(True)
        self.pushButton_zip.setEnabled(True)

    def disable_input(self):
        self.pushButton_excel.setEnabled(False)
        self.pushButton_zip.setEnabled(False)

    def btn_excel_clicked(self):
        self.disable_input()
        self.genericThread = GenericThread(self.generate_excel)
        self.genericThread.start()

    def btn_zip_clicked(self):
        self.disable_input()
        self.genericThread = GenericThread(self.generate_zip)
        self.genericThread.start()

    def main(self):
        self.show()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    xplantool = XplanTool()
    xplantool.main()
    app.exec_()