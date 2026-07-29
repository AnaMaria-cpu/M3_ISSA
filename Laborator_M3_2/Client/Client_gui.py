from PyQt5 import QtCore, QtGui, QtWidgets
import socket
import rsa_library
import _pickle as cPickle
import os
import threading
import sys, time
import rsa_library


HOST = 'localhost'
PORT = 12346
stop_thread = False


airbag_on = 0xfe01
corrupted_low = 0x5732
corrupted_high = 0x5701



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600,500)
        MainWindow.setWindowTitle('Client')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        MainWindow.setCentralWidget(self.centralwidget)

        self.centralwidget.setStyleSheet("background-color:white;")
        
        # Start client button
        self.client_start = QtWidgets.QPushButton(MainWindow)
        self.client_start .setText("Connect client")
        self.client_start .setStyleSheet("font: bold; font-size: 15px;")
        self.client_start .setGeometry(QtCore.QRect(200, 170, 200, 40))
        self.client_start.clicked.connect(self.start_client)

        self.client_label = QtWidgets.QLabel(self.centralwidget)
        self.client_label.setGeometry(QtCore.QRect(320, 170, 205, 41))
        self.client_label.setStyleSheet("font:bold;font-size: 15px;")

        # Connected label
        self.connected_label = QtWidgets.QLabel(self.centralwidget)
        self.connected_label.setGeometry(QtCore.QRect(200, 210,200 , 40))
        self.connected_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Airbag on
        self.airbag = QtWidgets.QPushButton(MainWindow)
        self.airbag.setText("Airbag on")
        self.airbag.setStyleSheet("font: bold; font-size: 15px;")
        self.airbag.setGeometry(QtCore.QRect(70,260,211,41))
        self.airbag.clicked.connect(self.send_on_data)
        self.airbag.setEnabled(False)

        # Airbag on label
        self.airbag_on_label = QtWidgets.QLabel(self.centralwidget)
        self.airbag_on_label.setGeometry(QtCore.QRect(300, 260,200 , 40))
        self.airbag_on_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Corrupted low
        self.corrupted_low = QtWidgets.QPushButton(MainWindow)
        self.corrupted_low.setText("Corrupted low")
        self.corrupted_low.setStyleSheet("font: bold; font-size: 15px;")
        self.corrupted_low.setGeometry(QtCore.QRect(70,330,211,41))
        self.corrupted_low.clicked.connect(self.send_corrupted_low)
        self.corrupted_low.setEnabled(False)

        # Corrupted low label
        self.corrupted_low_label = QtWidgets.QLabel(self.centralwidget)
        self.corrupted_low_label.setGeometry(QtCore.QRect(300, 330,200 , 40))
        self.corrupted_low_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")
        
        # Corrupted high
        self.corrupted_high = QtWidgets.QPushButton(MainWindow)
        self.corrupted_high.setText("Corrupted high")
        self.corrupted_high.setStyleSheet("font: bold; font-size: 15px;")
        self.corrupted_high.setGeometry(QtCore.QRect(70,400,211,41))
        self.corrupted_high.clicked.connect(self.send_corrupted_high)
        self.corrupted_high.setEnabled(False)

        # Corrupted high label
        self.corrupted_high_label = QtWidgets.QLabel(self.centralwidget)
        self.corrupted_high_label.setGeometry(QtCore.QRect(300, 400,200 , 40))
        self.corrupted_high_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")
     
        # Continental image
        self.conti_label = QtWidgets.QLabel(self.centralwidget)
        self.conti_label.setGeometry(QtCore.QRect(110, 30, 400, 100))
        continental = QtGui.QImage(QtGui.QImageReader('./rsz_conti.png').read())
        self.conti_label.setPixmap(QtGui.QPixmap(continental))
    
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()


############################### EXERCISE 5 ###############################
    def start_client(self):
      self.corrupted_low_label.clear()
      self.airbag_on_label.clear()
      self.corrupted_high_label.clear()
      self.airbag.setEnabled(False)
      self.corrupted_high.setEnabled(False)
      self.corrupted_low.setEnabled(False)
      ''' complete with necesarry code '''

          
############################### EXERCISE 8 ###############################
    def recv_messages(self):
        self.stop_event = threading.Event()
        self.c_thread=threading.Thread(target=self.recv_handler, args=(self.stop_event,))
        self.c_thread.start()

    def recv_handler(self,stop_event):
        global stop_thread
        while not stop_event.isSet() and stop_thread == False:
            ''' complete with necesarry code '''

############################### EXERCISE 9 ###############################              
    def send_on_data(self):
        pass
        ''' complete with necesarry code '''
############################### EXERCISE 10 ###############################     
    def send_corrupted_low(self):
        pass
        ''' complete with necesarry code '''

############################### EXERCISE 11 ###############################      
    def send_corrupted_high(self):
        pass
        ''' complete with necesarry code '''
      
        
def kill_proc_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()
        
class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self,event):
        global stop_thread
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)        

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
            stop_thread = True
        elif result == QtWidgets.QMessageBox.No:
            event.ignore()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
    


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.center()
    sys.exit(app.exec_())
