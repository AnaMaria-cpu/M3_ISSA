# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
import socket
import threading
import sys

HOST = "localhost"
PORT = 5005

client = None
connected = False
diag_mode = 0
stop_thread = False

# The flag stores the state that will be sent on the next click.
# First click changes False -> True and sends S=1 (green).
led0_flag = False
led1_flag = False
led2_flag = False
led3_flag = False

LED_GREEN_STYLE = "background-color: green; border-radius: 12px;"
LED_RED_STYLE = "background-color: red; border-radius: 12px;"


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(658, 500)
        MainWindow.setMinimumSize(QtCore.QSize(658, 500))
        MainWindow.setMaximumSize(QtCore.QSize(658, 500))
        MainWindow.setWindowTitle("Client")

        self.logo_img = QtGui.QPixmap("./rsz_conti.png")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.logo = QtWidgets.QLabel(self.centralwidget)
        self.logo.setGeometry(QtCore.QRect(150, 20, 400, 100))
        self.logo.setObjectName("logo")

        self.connected_msg = QtWidgets.QLabel(self.centralwidget)
        self.connected_msg.setGeometry(QtCore.QRect(260, 175, 150, 30))
        self.connected_msg.setObjectName("connected_msg")
        self.connected_msg.setStyleSheet("font: bold; color: green")
        self.connected_msg.setAlignment(QtCore.Qt.AlignCenter)

        self.not_diag_mode = QtWidgets.QLabel(self.centralwidget)
        self.not_diag_mode.setGeometry(QtCore.QRect(260, 187, 150, 30))
        self.not_diag_mode.setObjectName("not_diag_mode")
        self.not_diag_mode.setStyleSheet("font: bold; color: red")
        self.not_diag_mode.setAlignment(QtCore.Qt.AlignCenter)
        self.not_diag_mode.setVisible(False)

        self.diagMode = QtWidgets.QPushButton(self.centralwidget)
        self.diagMode.setGeometry(QtCore.QRect(185, 210, 131, 41))
        self.diagMode.setObjectName("diagMode")
        self.diagMode.clicked.connect(self.diag)
        self.diagMode.setEnabled(False)

        self.diagMode_off = QtWidgets.QPushButton(self.centralwidget)
        self.diagMode_off.setGeometry(QtCore.QRect(325, 210, 131, 41))
        self.diagMode_off.setObjectName("diagMode_off")
        self.diagMode_off.setEnabled(False)
        self.diagMode_off.clicked.connect(self.stop_diag)

        self.set_led0 = QtWidgets.QPushButton(self.centralwidget)
        self.set_led0.setGeometry(QtCore.QRect(30, 310, 81, 31))
        self.set_led0.clicked.connect(self.set_led0_flags)

        self.set_led1 = QtWidgets.QPushButton(self.centralwidget)
        self.set_led1.setGeometry(QtCore.QRect(30, 350, 81, 31))
        self.set_led1.clicked.connect(self.set_led1_flags)

        self.set_led2 = QtWidgets.QPushButton(self.centralwidget)
        self.set_led2.setGeometry(QtCore.QRect(30, 390, 81, 31))
        self.set_led2.clicked.connect(self.set_led2_flags)

        self.set_led3 = QtWidgets.QPushButton(self.centralwidget)
        self.set_led3.setGeometry(QtCore.QRect(30, 430, 81, 31))
        self.set_led3.clicked.connect(self.set_led3_flags)

        self.led0_state = QtWidgets.QLabel(self.centralwidget)
        self.led0_state.setGeometry(QtCore.QRect(140, 313, 25, 25))
        self.led0_state.setVisible(False)

        self.led1_state = QtWidgets.QLabel(self.centralwidget)
        self.led1_state.setGeometry(QtCore.QRect(140, 353, 25, 25))
        self.led1_state.setVisible(False)

        self.led2_state = QtWidgets.QLabel(self.centralwidget)
        self.led2_state.setGeometry(QtCore.QRect(140, 393, 25, 25))
        self.led2_state.setVisible(False)

        self.led3_state = QtWidgets.QLabel(self.centralwidget)
        self.led3_state.setGeometry(QtCore.QRect(140, 433, 25, 25))
        self.led3_state.setVisible(False)

        self.set_led_title = QtWidgets.QLabel(self.centralwidget)
        self.set_led_title.setGeometry(QtCore.QRect(75, 270, 92, 21))
        self.set_led_title.setObjectName("set_led_title")
        self.set_led_title.setStyleSheet("font: bold; font-size: 11px;")

        self.read_dtc_title = QtWidgets.QLabel(self.centralwidget)
        self.read_dtc_title.setGeometry(QtCore.QRect(470, 270, 101, 20))
        self.read_dtc_title.setObjectName("read_dtc_title")
        self.read_dtc_title.setStyleSheet("font: bold; font-size: 11px;")

        self.dtc1 = QtWidgets.QPushButton(self.centralwidget)
        self.dtc1.setGeometry(QtCore.QRect(460, 310, 81, 31))
        self.dtc1.clicked.connect(lambda: self.get_dtc_state("01"))

        self.dtc2 = QtWidgets.QPushButton(self.centralwidget)
        self.dtc2.setGeometry(QtCore.QRect(460, 350, 81, 31))
        self.dtc2.clicked.connect(lambda: self.get_dtc_state("02"))

        self.dtc3 = QtWidgets.QPushButton(self.centralwidget)
        self.dtc3.setGeometry(QtCore.QRect(460, 390, 81, 31))
        self.dtc3.clicked.connect(lambda: self.get_dtc_state("03"))

        self.dtc4 = QtWidgets.QPushButton(self.centralwidget)
        self.dtc4.setGeometry(QtCore.QRect(460, 430, 81, 31))
        self.dtc4.clicked.connect(lambda: self.get_dtc_state("04"))

        self.dtc1_state = QtWidgets.QLabel(self.centralwidget)
        self.dtc1_state.setGeometry(QtCore.QRect(555, 315, 85, 20))
        self.dtc1_state.setText("Unknown")
        self.dtc1_state.setStyleSheet("font: bold; color: blue")

        self.dtc2_state = QtWidgets.QLabel(self.centralwidget)
        self.dtc2_state.setGeometry(QtCore.QRect(555, 355, 85, 20))
        self.dtc2_state.setText("Unknown")
        self.dtc2_state.setStyleSheet("font: bold; color: blue")

        self.dtc3_state = QtWidgets.QLabel(self.centralwidget)
        self.dtc3_state.setGeometry(QtCore.QRect(555, 395, 85, 20))
        self.dtc3_state.setText("Unknown")
        self.dtc3_state.setStyleSheet("font: bold; color: blue")

        self.dtc4_state = QtWidgets.QLabel(self.centralwidget)
        self.dtc4_state.setGeometry(QtCore.QRect(555, 435, 85, 20))
        self.dtc4_state.setText("Unknown")
        self.dtc4_state.setStyleSheet("font: bold; color: blue")

        self.connect = QtWidgets.QPushButton(self.centralwidget)
        self.connect.setGeometry(QtCore.QRect(260, 130, 131, 51))
        self.connect.setObjectName("connect")
        self.connect.clicked.connect(self.start_client)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 658, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self._set_operation_buttons_enabled(False)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Client"))
        self.logo.setPixmap(self.logo_img)
        self.connected_msg.setText(_translate("MainWindow", ""))
        self.not_diag_mode.setText(_translate("MainWindow", "NOT IN DIAG MODE"))
        self.diagMode.setText(_translate("MainWindow", "Enter Diag Mode"))
        self.diagMode_off.setText(_translate("MainWindow", "Stop Diag Mode"))
        self.set_led0.setText(_translate("MainWindow", "Set LED0"))
        self.set_led1.setText(_translate("MainWindow", "Set LED1"))
        self.set_led2.setText(_translate("MainWindow", "Set LED2"))
        self.set_led3.setText(_translate("MainWindow", "Set LED3"))
        self.set_led_title.setText(_translate("MainWindow", "SET LED STATES"))
        self.read_dtc_title.setText(_translate("MainWindow", "READ DTC STATES"))
        self.dtc1.setText(_translate("MainWindow", "Read DTC1"))
        self.dtc2.setText(_translate("MainWindow", "Read DTC2"))
        self.dtc3.setText(_translate("MainWindow", "Read DTC3"))
        self.dtc4.setText(_translate("MainWindow", "Read DTC4"))
        self.connect.setText(_translate("MainWindow", "CONNECT"))

    ############################### EXERCISE 0 ###############################
    def start_client(self):
        global client
        global connected
        global diag_mode
        global led0_flag, led1_flag, led2_flag, led3_flag

        diag_mode = 0
        led0_flag = led1_flag = led2_flag = led3_flag = False

        self.diagMode.setEnabled(False)
        self.diagMode_off.setEnabled(False)
        self._set_operation_buttons_enabled(False)
        self.not_diag_mode.setVisible(False)

        self.dtc1_state.setText("Unknown")
        self.dtc1_state.setStyleSheet("font: bold; color: blue;")
        self.dtc2_state.setText("Unknown")
        self.dtc2_state.setStyleSheet("font: bold; color: blue;")
        self.dtc3_state.setText("Unknown")
        self.dtc3_state.setStyleSheet("font: bold; color: blue;")
        self.dtc4_state.setText("Unknown")
        self.dtc4_state.setStyleSheet("font: bold; color: blue;")

        self.set_led0.setText("Set LED0")
        self.set_led1.setText("Set LED1")
        self.set_led2.setText("Set LED2")
        self.set_led3.setText("Set LED3")

        self.led0_state.setVisible(False)
        self.led1_state.setVisible(False)
        self.led2_state.setVisible(False)
        self.led3_state.setVisible(False)

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, PORT))
            connected = True

            self.connected_msg.setText("CONNECTED")
            self.connected_msg.setStyleSheet("font: bold; color: green")
            self.connect.setEnabled(False)
            self.diagMode.setEnabled(True)
            # In normal mode the buttons remain clickable, but requests are blocked
            # by the diag_mode check and the warning label is shown.
            self._set_operation_buttons_enabled(True)

            print(f"Connected to server {HOST}:{PORT}")
            self.recv_messages()

        except (ConnectionRefusedError, OSError) as error:
            connected = False
            self.connected_msg.setText("FAILED")
            self.connected_msg.setStyleSheet("font: bold; color: red")
            self.connect.setEnabled(True)
            print("Client connection error:", error)

    ############################### EXERCISE 1 ###############################
    def recv_handler(self, stop_event):
        global connected
        global diag_mode
        global stop_thread

        receive_buffer = ""

        while connected and not stop_event.is_set() and not stop_thread:
            try:
                received_bytes = client.recv(1024)

                if not received_bytes:
                    connected = False
                    self.connected_msg.setText("DISCONNECTED")
                    self.connected_msg.setStyleSheet("font: bold; color: red")
                    break

                receive_buffer += received_bytes.decode("utf-8")

                while "\n" in receive_buffer:
                    data_recv, receive_buffer = receive_buffer.split("\n", 1)
                    data_recv = data_recv.strip()

                    if not data_recv:
                        continue

                    print("Client received:", data_recv)

                    if data_recv == "DIAG_ON":
                        diag_mode = 1
                        self._update_diag_ui(True)

                    elif data_recv == "DIAG_OFF":
                        diag_mode = 0
                        self._update_diag_ui(False)

                    elif data_recv == "NOT_DIAG":
                        self._show_not_diag()

                    elif data_recv.startswith("0x6201"):
                        self.set_dtc1_state(data_recv)
                    elif data_recv.startswith("0x6202"):
                        self.set_dtc2_state(data_recv)
                    elif data_recv.startswith("0x6203"):
                        self.set_dtc3_state(data_recv)
                    elif data_recv.startswith("0x6204"):
                        self.set_dtc4_state(data_recv)

                    elif data_recv.startswith("0x6E00"):
                        self.set_led0_label(data_recv)
                    elif data_recv.startswith("0x6E01"):
                        self.set_led1_label(data_recv)
                    elif data_recv.startswith("0x6E02"):
                        self.set_led2_label(data_recv)
                    elif data_recv.startswith("0x6E03"):
                        self.set_led3_label(data_recv)

            except (ConnectionResetError, ConnectionAbortedError, OSError) as error:
                connected = False
                print("Connection error:", error)
                self.connected_msg.setText("CONNECTION LOST")
                self.connected_msg.setStyleSheet("font: bold; color: red")
                break
            except UnicodeDecodeError as error:
                print("Invalid message encoding:", error)

    def recv_messages(self):
        self.stop_event = threading.Event()
        self.c_thread = threading.Thread(
            target=self.recv_handler,
            args=(self.stop_event,),
            daemon=True,
        )
        self.c_thread.start()

    def diag(self):
        global diag_mode

        if not connected:
            return

        diag_mode = 1
        self._send_message("0x3E01")
        self._update_diag_ui(True)

    def stop_diag(self):
        global diag_mode

        if not connected:
            return

        # The PDF writes 0x3E0; 0x3E00 is used as the complete command.
        diag_mode = 0
        self._send_message("0x3E00")
        self._update_diag_ui(False)

    def _send_message(self, message):
        if client is None:
            return

        client.sendall((message + "\n").encode("utf-8"))
        print("Client sent:", message)

    def _update_diag_ui(self, enabled):
        self.not_diag_mode.setVisible(False)
        self.diagMode.setEnabled(not enabled)
        self.diagMode_off.setEnabled(enabled)
        # The operations stay visible/clickable in normal mode; their functions
        # display NOT IN DIAG MODE instead of sending a request.
        self._set_operation_buttons_enabled(connected)

    def _set_operation_buttons_enabled(self, enabled):
        for button in (
            self.dtc1,
            self.dtc2,
            self.dtc3,
            self.dtc4,
            self.set_led0,
            self.set_led1,
            self.set_led2,
            self.set_led3,
        ):
            button.setEnabled(enabled)

    def _show_not_diag(self):
        self.not_diag_mode.setVisible(True)

    ############################### EXERCISE 3 ###############################
    def get_dtc_state(self, dtc_string):
        if diag_mode == 1:
            self.not_diag_mode.setVisible(False)
            self._send_message(f"0x22{dtc_string}")
        else:
            self._show_not_diag()

    def _set_dtc_state(self, label, data_recv):
        color_code = data_recv[6:]

        if color_code == "25500":
            label.setText("Active")
            label.setStyleSheet("font: bold; color: red;")
        elif color_code == "02550":
            label.setText("Inactive")
            label.setStyleSheet("font: bold; color: green;")
        else:
            label.setText("Unknown")
            label.setStyleSheet("font: bold; color: blue;")

    def set_dtc1_state(self, data_recv):
        self._set_dtc_state(self.dtc1_state, data_recv)

    def set_dtc2_state(self, data_recv):
        self._set_dtc_state(self.dtc2_state, data_recv)

    def set_dtc3_state(self, data_recv):
        self._set_dtc_state(self.dtc3_state, data_recv)

    def set_dtc4_state(self, data_recv):
        self._set_dtc_state(self.dtc4_state, data_recv)

    ############################### EXERCISE 4 ###############################
    def _set_led_label(self, label, data_recv):
        state = data_recv[-1]

        if state == "1":
            label.setStyleSheet(LED_GREEN_STYLE)
        elif state == "0":
            label.setStyleSheet(LED_RED_STYLE)
        else:
            return

        label.setVisible(True)

    def set_led0_label(self, data_recv):
        self._set_led_label(self.led0_state, data_recv)

    def set_led1_label(self, data_recv):
        self._set_led_label(self.led1_state, data_recv)

    def set_led2_label(self, data_recv):
        self._set_led_label(self.led2_state, data_recv)

    def set_led3_label(self, data_recv):
        self._set_led_label(self.led3_state, data_recv)

    def _send_led_state(self, led_number, state):
        if diag_mode == 1:
            self.not_diag_mode.setVisible(False)
            self._send_message(f"0x2E{led_number:02d}{int(state)}")
        else:
            self._show_not_diag()

    def set_led0_flags(self):
        global led0_flag
        if diag_mode != 1:
            self._show_not_diag()
            return
        led0_flag = not led0_flag
        self._send_led_state(0, led0_flag)

    def set_led1_flags(self):
        global led1_flag
        if diag_mode != 1:
            self._show_not_diag()
            return
        led1_flag = not led1_flag
        self._send_led_state(1, led1_flag)

    def set_led2_flags(self):
        global led2_flag
        if diag_mode != 1:
            self._show_not_diag()
            return
        led2_flag = not led2_flag
        self._send_led_state(2, led2_flag)

    def set_led3_flags(self):
        global led3_flag
        if diag_mode != 1:
            self._show_not_diag()
            return
        led3_flag = not led3_flag
        self._send_led_state(3, led3_flag)


class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        global stop_thread
        global client

        stop_thread = True
        if client is not None:
            try:
                client.close()
            except OSError:
                pass
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MyWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
