import sys

from PyQt4 import QtGui, QtCore

from xplan import XPlan
from excel import Excel

# Import the interface class
import xplanUI


class XplanTool(QtGui.QDialog, xplanUI.Ui_Dialog):
    def __init__(self, parent=None):
        super(XplanTool, self).__init__(parent)
        self.setupUi(self)

    def btn_excel_clicked(self):
        self.pushButton_excel.setEnabled(False)
        p = XPlan()
        if p.load_zip():
            x = Excel()
            p.extract_objects()
            p.generate_obj_file()
            x.generate_xls_file(p.get_xplan_object())
        print '[Complete]'
        self.pushButton_excel.setEnabled(True)

    def btn_zip_clicked(self):
        self.pushButton_zip.setEnabled(False)
        p = XPlan()
        x = Excel()
        p.generate_zip_file(x.get_xplan_object())
        print '[Complete]'
        self.pushButton_zip.setEnabled(True)

    def main(self):
        self.show()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    xplantool = XplanTool()
    xplantool.main()
    app.exec_()