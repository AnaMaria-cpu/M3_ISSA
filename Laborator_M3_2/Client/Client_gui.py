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
        global client
        global public_key
        global private_key

        self.corrupted_low_label.clear()
        self.airbag_on_label.clear()
        self.corrupted_high_label.clear()

        self.airbag.setEnabled(False)
        self.corrupted_high.setEnabled(False)
        self.corrupted_low.setEnabled(False)

        try:
            # Creăm socketul TCP al clientului
            client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            # Ne conectăm la server
            client.connect((HOST, PORT))

            # Primim cheile RSA trimise de server
            received_data = client.recv(4096)

            # Transformăm bytes înapoi în obiect Python
            public_key, private_key = cPickle.loads(received_data)

            print("Client connected")
            print("Public key received:", public_key)
            print("Private key received:", private_key)

            self.connected_label.setText("Connected to server")
            self.client_start.setEnabled(False)

            # Ascultăm mesajele trimise ulterior de server
            self.recv_messages()

        except ConnectionRefusedError:
            self.connected_label.setText("Server not started")
            print("Connection refused. Start the server first.")

        except Exception as error:
            self.connected_label.setText("Connection error")
            print("Client error:", error)

          
############################### EXERCISE 8 ###############################
    def recv_messages(self):
        self.stop_event = threading.Event()
        self.c_thread=threading.Thread(target=self.recv_handler, args=(self.stop_event,))
        self.c_thread.start()

    def recv_handler(self,stop_event):
        global stop_thread
        global client
        global private_key

        while not stop_event.is_set() and not stop_thread :
            try:
                # Așteptăm date de la server
                received_data = client.recv(4096)

                # Dacă nu mai sunt date, serverul s-a deconectat
                if not received_data:
                    print("Server disconnected")
                    self.connected_label.setText("Server disconnected")
                    break

                # Transformăm datele primite din bytes în obiect Python
                received_message = cPickle.loads(received_data)

                print("Message received from server:", received_message)

                # Mesajele de tip int sunt comenzi RSA criptate
                if isinstance(received_message, int):
                    decrypted_message = rsa_library.decrypt(
                        private_key,
                        received_message
                    )

                    print(
                        "Decrypted server message:",
                        hex(decrypted_message)
                    )

                    # Comanda 0xfd02 înseamnă deblocarea mașinii
                    if decrypted_message == 0xfd02:
                        self.airbag.setEnabled(True)
                        self.corrupted_low.setEnabled(True)
                        self.corrupted_high.setEnabled(True)

                        self.connected_label.setText("Car unlocked")

                # Răspuns pentru comanda Airbag on
                elif received_message == "Airbag on":
                    self.airbag_on_label.setText("Airbag is on")

                # Răspuns pentru LOW invalid
                elif received_message == "Low corruption":
                    self.corrupted_low_label.setText("Low corruption")

                # Răspuns pentru HIGH invalid
                elif received_message == "High corruption":
                    self.corrupted_high_label.setText("High corruption")

                else:
                    print("Unknown server response:", received_message)

            except (
                    ConnectionResetError,
                    ConnectionAbortedError,
                    OSError
            ) as error:
                print("Connection error:", error)
                self.connected_label.setText("Connection lost")
                break

            except (
                    cPickle.UnpicklingError,
                    EOFError,
                    TypeError,
                    ValueError
            ) as error:
                print("Invalid data received:", error)

############################### EXERCISE 9 ###############################              
    def send_on_data(self):
        global client
        global public_key

        try:
            # Criptăm valoarea 0xfe01
            encrypted_message = rsa_library.encrypt(
                public_key,
                airbag_on
            )

            # Trimitem numărul criptat serverului
            client.sendall(
                cPickle.dumps(encrypted_message)
            )

            self.airbag_on_label.setText("Waiting...")

            print("Airbag command sent")
            print("Original:", hex(airbag_on))
            print("Encrypted:", encrypted_message)

        except OSError as error:
            self.airbag_on_label.setText("Send error")
            print("Error sending Airbag command:", error)
############################### EXERCISE 10 ###############################     
    def send_corrupted_low(self):
        global client
        global public_key

        try:
            # Criptăm valoarea coruptă în partea LOW
            encrypted_message = rsa_library.encrypt(
                public_key,
                corrupted_low
            )

            # Trimitem numărul criptat serverului
            client.sendall(
                cPickle.dumps(encrypted_message)
            )

            self.corrupted_low_label.setText("Waiting...")

            print("Corrupted LOW command sent")
            print("Original:", hex(corrupted_low))
            print("Encrypted:", encrypted_message)

        except OSError as error:
            self.corrupted_low_label.setText("Send error")
            print("Error sending corrupted LOW:", error)

############################### EXERCISE 11 ###############################      
    def send_corrupted_high(self):
        global client
        global public_key

        try:
            # Criptăm valoarea coruptă în partea HIGH
            encrypted_message = rsa_library.encrypt(
                public_key,
                corrupted_high
            )

            # Trimitem numărul criptat serverului
            client.sendall(
                cPickle.dumps(encrypted_message)
            )

            self.corrupted_high_label.setText("Waiting...")

            print("Corrupted HIGH command sent")
            print("Original:", hex(corrupted_high))
            print("Encrypted:", encrypted_message)

        except OSError as error:
            self.corrupted_high_label.setText("Send error")
            print("Error sending corrupted HIGH:", error)
      
        
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
