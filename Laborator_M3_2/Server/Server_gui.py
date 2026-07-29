from PyQt5 import QtCore, QtGui, QtWidgets
import socket
import rsa_library
import _pickle as cPickle
import os
import threading
import sys, time


HOST = 'localhost'
PORT = 12346

stop_thread = False

flag = 1
flag_low = 0

unlockCar = 0xfd02

server_socket = None
server = None

public_key = None
private_key = None

server_created_flag = False

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        global server
        global public_key
        global private_key
        global server_created_flag
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600,500)
        MainWindow.setWindowTitle('Server')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
    
        self.centralwidget.setStyleSheet("background-color:white;")
        
        # Start server button
        self.server_start = QtWidgets.QPushButton(MainWindow)
        self.server_start .setText("Start server")
        self.server_start .setStyleSheet("font: bold; font-size: 15px;")
        self.server_start .setGeometry(QtCore.QRect(200, 170, 200, 41))
        self.server_start.clicked.connect(self.start_server)

        # Start server label
        self.server_label = QtWidgets.QLabel(self.centralwidget)
        self.server_label.setGeometry(QtCore.QRect(200, 210, 200, 40))
        self.server_label.setStyleSheet("font:bold;font-size: 15px;qproperty-alignment: AlignCenter;")

        # Key button
        self.key = QtWidgets.QPushButton(self.centralwidget)
        self.key.setGeometry(QtCore.QRect(225,270,150,150))
        keyImage = QtGui.QIcon('./key.png')
        self.key.setIcon(keyImage)
        self.key.setIconSize(QtCore.QSize(80,80))
        self.key.clicked.connect(self.send_key_data)
        self.key.setEnabled(False)

        # Unlock
        self.unlock = QtWidgets.QLabel(self.centralwidget)
        self.unlock.setGeometry(QtCore.QRect(225,430,150,20))
        self.unlock.setText("Unlock the car!")
        self.unlock.setStyleSheet("font:bold;font-size: 15px;qproperty-alignment: AlignCenter;")

        # Dashboard image
        self.dashboard_label = QtWidgets.QLabel(self.centralwidget)
        self.dashboard_label.setGeometry(QtCore.QRect(120, 280,360,180))
        dashboard = QtGui.QImage(QtGui.QImageReader('./dashboard.png').read())
        self.dashboard_label.setPixmap(QtGui.QPixmap(dashboard))
        self.dashboard_label.setVisible(False)

        # Airgab image label
        self.airbag_label = QtWidgets.QLabel(self.centralwidget)
        self.airbag_label.setGeometry(QtCore.QRect(290,365,30,30))
        airbag_image = QtGui.QPixmap("./airbag.png")
        airbag_image = airbag_image.scaled(30,30, QtCore.Qt.KeepAspectRatio)
        self.airbag_label.setPixmap(QtGui.QPixmap(airbag_image))
        self.airbag_label.setVisible(False)

        # Ecu defect label
        self.ecu_defect_label = QtWidgets.QLabel(self.centralwidget)
        self.ecu_defect_label.setGeometry(QtCore.QRect(280,365,40,30))
        self.ecu_defect_label.setStyleSheet("font:bold;font-size:12px;color:red")
        self.ecu_defect_label.setVisible(False)
        
        # Continental image
        self.conti_label = QtWidgets.QLabel(self.centralwidget)
        self.conti_label.setGeometry(QtCore.QRect(110, 30, 400, 100))
        continental = QtGui.QImage(QtGui.QImageReader('./rsz_conti.png').read())
        self.conti_label.setPixmap(QtGui.QPixmap(continental))
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()

    
############################### EXERCISE 5 ###############################
    def start_server(self):
        global server
        global public_key
        global private_key
        global server_created_flag

        # Resetarea interfeței
        self.key.setEnabled(False)
        self.airbag_label.setVisible(False)
        self.ecu_defect_label.clear()
        self.ecu_defect_label.setVisible(False)
        self.dashboard_label.setVisible(False)
        self.key.setVisible(True)
        self.unlock.setVisible(True)

        # Pornim thread-ul care va actualiza imaginile
        self.images()

        # Informăm utilizatorul că serverul așteaptă clientul
        self.server_label.setText("Waiting for client...")
        self.server_start.setEnabled(False)

        # Actualizează interfața înainte ca accept() să înceapă așteptarea
        QtWidgets.QApplication.processEvents()

        try:
            # Creăm socketul TCP al serverului
            server_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            # Permite reutilizarea portului după repornirea aplicației
            server_socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            # Asociem serverul cu adresa localhost și portul 12346
            server_socket.bind((HOST, PORT))

            # Serverul începe să asculte după un client
            server_socket.listen(1)

            print("Server started")
            print("Waiting for client...")

            # Programul așteaptă aici conectarea clientului
            server, client_address = server_socket.accept()

            print("Client connected:", client_address)

            # Marcăm faptul că serverul este pornit și clientul este conectat
            server_created_flag = True

            # Generăm cheile RSA
            public_key, private_key = rsa_library.generate_keypair(
                277,
                239
            )

            print("Public key:", public_key)
            print("Private key:", private_key)

            # Punem cele două chei într-un singur tuplu
            keys = (public_key, private_key)

            # Transformăm cheile în bytes și le trimitem clientului
            server.sendall(cPickle.dumps(keys))

            # Pornim threadul care va asculta mesajele clientului
            self.recv_messages()

            # Actualizăm interfața după conectare
            self.server_label.setText("Client connected")
            self.key.setEnabled(True)

        except OSError as error:
            print("Server error:", error)

            server_created_flag = False

            self.server_label.setText("Server error")
            self.server_start.setEnabled(True)
            self.key.setEnabled(False)

############################### EXERCISE 6 ###############################   
    def send_key_data(self):
        global server
        global public_key

        # Criptăm comanda de deblocare folosind cheia publică
        encrypted_unlock_car = rsa_library.encrypt(
            public_key,
            unlockCar
        )

        # Transformăm numărul criptat în bytes și îl trimitem clientului
        server.sendall(
            cPickle.dumps(encrypted_unlock_car)
        )

        print("Unlock command sent")
        print("Original message:", hex(unlockCar))
        print("Encrypted message:", encrypted_unlock_car)

        # După apăsarea cheii, afișăm dashboard-ul
        self.dashboard_label.setVisible(True)
        self.unlock.setVisible(False)
        self.key.setVisible(False)

############################### EXERCISE 7 ###############################   
    def recv_messages(self):
        self.stop_event = threading.Event()
        self.c_thread=threading.Thread(target=self.recv_messages_handler, args=(self.stop_event,))
        self.c_thread.start()

    def recv_messages_handler(self,stop_event):
        global server_created_flag
        global stop_thread
        global flag
        global flag_low
        global server
        global private_key

        while (
                server_created_flag
                and not stop_event.is_set()
                and stop_thread == False
        ):
            try:
                # Primim mesajul criptat de la client
                received_data = server.recv(4096)

                # Dacă nu mai primim date, clientul s-a deconectat
                if not received_data:
                    print("Client disconnected")
                    server_created_flag = False
                    break

                # Transformăm bytes înapoi într-un obiect Python
                encrypted_message = cPickle.loads(received_data)

                # Decriptăm mesajul folosind cheia privată
                decrypted_message = rsa_library.decrypt(
                    private_key,
                    encrypted_message
                )

                print("Encrypted message received:", encrypted_message)
                print("Decrypted message:", hex(decrypted_message))

                # Verificăm dacă LOW este 0x01
                flag_low = rsa_library.low_check(decrypted_message)

                # Verificăm dacă HIGH este complementul lui LOW
                flag = rsa_library.number_check(decrypted_message)

                print("LOW check:", flag_low)
                print("HIGH check:", flag)

                # LOW invalid are prioritate
                if flag_low == False:
                    response = "Low corruption"

                # LOW este bun, dar HIGH este invalid
                elif flag == False:
                    response = "High corruption"

                # Ambele condiții sunt corecte
                else:
                    response = "Airbag on"

                # Trimitem rezultatul înapoi clientului
                server.sendall(cPickle.dumps(response))

                print("Response sent:", response)

            except (
                    ConnectionResetError,
                    ConnectionAbortedError,
                    OSError
            ) as error:
                print("Connection error:", error)
                server_created_flag = False
                break

            except (
                    cPickle.UnpicklingError,
                    EOFError,
                    TypeError,
                    ValueError
            ) as error:
                print("Invalid received data:", error)


##############################################################     
    def images(self):
        self.c_thread1=threading.Thread(name='images',target=self.images_handler)
        self.c_thread1.start()

    def images_handler(self):
        global flag
        global flag_low
        global stop_thread 

        while stop_thread == False:
            if flag_low == True and flag == True:
                self.ecu_defect_label.setVisible(False)
                self.airbag_label.setVisible(True)
            elif flag_low == True and flag == False:
                self.airbag_label.setVisible(False)
                self.ecu_defect_label.setVisible(True)
                self.ecu_defect_label.setText('  ECU\nDefect')
            elif flag_low == False and flag == False:
                self.airbag_label.setVisible(False)
                self.ecu_defect_label.setVisible(True)
                self.ecu_defect_label.setText('  ECU\nDefect')

            time.sleep(0.05)
        
class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self,event):
        global stop_thread
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)        

        if result == QtWidgets.QMessageBox.Yes:
            stop_thread = True
            event.accept()
        elif result == QtWidgets.QMessageBox.No:
            event.ignore()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

def kill_proc_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()

def main():
    global server_created_flag
    import sys
    global app
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.center()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

me = os.getpid()
kill_proc_tree(me)
    

