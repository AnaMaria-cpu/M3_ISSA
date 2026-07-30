#!/usr/bin/env python
from PyQt5 import QtCore, QtGui, QtWidgets
import socket
import threading
import sys

HOST = "localhost"
PORT = 5005

server_socket = None
conn = None
server_created_flag = False
diag_mode = False
stop_thread = False

# False = INACTIVE (green), True = ACTIVE (red)
dtc_states = [False, False, False, False]
all_dtc_active = False

GREEN_STYLE = "background-color: green; border-radius: 20px;"
RED_STYLE = "background-color: red; border-radius: 20px;"


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600, 800)
        MainWindow.setWindowTitle("Server")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: white;")
        MainWindow.setCentralWidget(self.centralwidget)

        # Start server button
        self.server_start = QtWidgets.QPushButton(MainWindow)
        self.server_start.setText("Start server")
        self.server_start.setStyleSheet("font: bold; font-size: 15px;")
        self.server_start.setGeometry(QtCore.QRect(200, 170, 200, 40))
        self.server_start.clicked.connect(self.start_server)

        # Set DTC1
        self.dtc1 = QtWidgets.QPushButton(MainWindow)
        self.dtc1.setText("Set DTC1 active")
        self.dtc1.setStyleSheet("font: bold; font-size: 15px;")
        self.dtc1.setGeometry(QtCore.QRect(70, 300, 200, 40))
        self.dtc1.clicked.connect(lambda: self.set_dtc1(7, 0.1))

        # Set DTC2
        self.dtc2 = QtWidgets.QPushButton(MainWindow)
        self.dtc2.setText("Set DTC2 active")
        self.dtc2.setStyleSheet("font: bold; font-size: 15px;")
        self.dtc2.setGeometry(QtCore.QRect(70, 370, 200, 40))
        self.dtc2.clicked.connect(lambda: self.set_dtc2(6, 0.1))

        # Set DTC3
        self.dtc3 = QtWidgets.QPushButton(MainWindow)
        self.dtc3.setText("Set DTC3 active")
        self.dtc3.setStyleSheet("font: bold; font-size: 15px;")
        self.dtc3.setGeometry(QtCore.QRect(70, 440, 200, 40))
        self.dtc3.clicked.connect(lambda: self.set_dtc3(5, 0.1))

        # Set DTC4
        self.dtc4 = QtWidgets.QPushButton(MainWindow)
        self.dtc4.setText("Set DTC4 active")
        self.dtc4.setStyleSheet("font: bold; font-size: 15px;")
        self.dtc4.setGeometry(QtCore.QRect(70, 510, 200, 40))
        self.dtc4.clicked.connect(lambda: self.set_dtc4(4, 0.1))

        # Four visual LEDs
        self.led1_state = QtWidgets.QLabel(MainWindow)
        self.led1_state.setGeometry(QtCore.QRect(330, 300, 40, 40))

        self.led2_state = QtWidgets.QLabel(MainWindow)
        self.led2_state.setGeometry(QtCore.QRect(330, 370, 40, 40))

        self.led3_state = QtWidgets.QLabel(MainWindow)
        self.led3_state.setGeometry(QtCore.QRect(330, 441, 40, 40))

        self.led4_state = QtWidgets.QLabel(MainWindow)
        self.led4_state.setGeometry(QtCore.QRect(330, 510, 40, 40))

        # Set all DTCs
        self.set_all_dtc = QtWidgets.QPushButton(MainWindow)
        self.set_all_dtc.setText("Set all DTC")
        self.set_all_dtc.setStyleSheet("font: bold; font-size: 15px;")
        self.set_all_dtc.setGeometry(QtCore.QRect(70, 580, 200, 40))
        self.set_all_dtc.clicked.connect(self.set_all)

        # Server state label
        self.server_label = QtWidgets.QLabel(self.centralwidget)
        self.server_label.setGeometry(QtCore.QRect(180, 210, 240, 40))
        self.server_label.setStyleSheet(
            "font: bold; font-size: 15px; qproperty-alignment: AlignCenter;"
        )

        # Logo
        self.conti_label = QtWidgets.QLabel(self.centralwidget)
        self.conti_label.setGeometry(QtCore.QRect(110, 30, 400, 100))
        self.conti_label.setStyleSheet("qproperty-alignment: AlignCenter;")
        continental = QtGui.QImage(QtGui.QImageReader("./rsz_conti.png").read())
        self.conti_label.setPixmap(QtGui.QPixmap(continental))

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()

    ############################### EXERCISE 0 ###############################
    def start_server(self):
        global dtc_states
        global all_dtc_active

        self.set_all_dtc.setText("Set all DTC")
        self.dtc1.setText("Set DTC1 active")
        self.dtc2.setText("Set DTC2 active")
        self.dtc3.setText("Set DTC3 active")
        self.dtc4.setText("Set DTC4 active")

        self.led1_state.setStyleSheet("")
        self.led2_state.setStyleSheet("")
        self.led3_state.setStyleSheet("")
        self.led4_state.setStyleSheet("")

        dtc_states = [False, False, False, False]
        all_dtc_active = False

        self.server_label.setText("Waiting for client...")
        self.server_start.setEnabled(False)

        # accept() is blocking, therefore it runs in a worker thread.
        threading.Thread(target=self._start_server_handler, daemon=True).start()

    def _start_server_handler(self):
        global server_socket
        global conn
        global server_created_flag

        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen(1)

            print(f"Server started on {HOST}:{PORT}")
            conn, client_address = server_socket.accept()
            server_created_flag = True

            print("Client connected:", client_address)
            self.server_label.setText("Client connected")
            self.recv()

        except OSError as error:
            server_created_flag = False
            print("Server error:", error)
            self.server_label.setText("Server error")
            self.server_start.setEnabled(True)

    ############################### EXERCISE 1 ###############################
    def recv_handler(self, stop_event):
        global conn
        global diag_mode
        global server_created_flag
        global stop_thread

        receive_buffer = ""

        while (
            server_created_flag
            and not stop_event.is_set()
            and not stop_thread
        ):
            try:
                received_bytes = conn.recv(1024)

                if not received_bytes:
                    print("Client disconnected")
                    server_created_flag = False
                    self.server_label.setText("Client disconnected")
                    break

                receive_buffer += received_bytes.decode("utf-8")

                # TCP is a byte stream, so one recv() can contain one or more commands.
                while "\n" in receive_buffer:
                    data, receive_buffer = receive_buffer.split("\n", 1)
                    data = data.strip()

                    if not data:
                        continue

                    print("Server received:", data)

                    if data == "0x3E01":
                        diag_mode = True
                        self._send_message("DIAG_ON")
                        print("Diagnostic mode ON")

                    # The PDF writes 0x3E0; 0x3E00 is the complete 2-byte form.
                    elif data in ("0x3E00", "0x3E0", "0x03E0"):
                        diag_mode = False
                        self._send_message("DIAG_OFF")
                        print("Diagnostic mode OFF")

                    elif not diag_mode:
                        self._send_message("NOT_DIAG")

                    elif data == "0x2201":
                        self.read_dtc1(data)
                    elif data == "0x2202":
                        self.read_dtc2(data)
                    elif data == "0x2203":
                        self.read_dtc3(data)
                    elif data == "0x2204":
                        self.read_dtc4(data)

                    elif data.startswith("0x2E00"):
                        self.set_led0(data)
                    elif data.startswith("0x2E01"):
                        self.set_led1(data)
                    elif data.startswith("0x2E02"):
                        self.set_led2(data)
                    elif data.startswith("0x2E03"):
                        self.set_led3(data)
                    else:
                        self._send_message("UNKNOWN_COMMAND")

            except (ConnectionResetError, ConnectionAbortedError, OSError) as error:
                print("Connection error:", error)
                server_created_flag = False
                self.server_label.setText("Connection lost")
                break
            except UnicodeDecodeError as error:
                print("Invalid message encoding:", error)

    def recv(self):
        self.stop_event = threading.Event()
        self.c_thread = threading.Thread(
            target=self.recv_handler,
            args=(self.stop_event,),
            daemon=True,
        )
        self.c_thread.start()

    def _send_message(self, message):
        global conn

        if conn is None:
            return

        conn.sendall((message + "\n").encode("utf-8"))
        print("Server sent:", message)

    ############################### EXERCISE 2 ###############################
    def _set_dtc(self, index):
        global dtc_states

        dtc_states[index] = not dtc_states[index]
        active = dtc_states[index]

        labels = [
            self.led1_state,
            self.led2_state,
            self.led3_state,
            self.led4_state,
        ]
        buttons = [self.dtc1, self.dtc2, self.dtc3, self.dtc4]

        labels[index].setStyleSheet(RED_STYLE if active else GREEN_STYLE)
        next_state = "inactive" if active else "active"
        buttons[index].setText(f"Set DTC{index + 1} {next_state}")

        print(f"DTC{index + 1} state:", "ACTIVE" if active else "INACTIVE")

    def set_dtc1(self, led, bright):
        self._set_dtc(0)

    def set_dtc2(self, led, bright):
        self._set_dtc(1)

    def set_dtc3(self, led, bright):
        self._set_dtc(2)

    def set_dtc4(self, led, bright):
        self._set_dtc(3)

    def set_all(self):
        global all_dtc_active
        global dtc_states

        all_dtc_active = not all_dtc_active
        dtc_states = [all_dtc_active] * 4

        labels = [
            self.led1_state,
            self.led2_state,
            self.led3_state,
            self.led4_state,
        ]
        buttons = [self.dtc1, self.dtc2, self.dtc3, self.dtc4]

        style = RED_STYLE if all_dtc_active else GREEN_STYLE
        next_state = "inactive" if all_dtc_active else "active"

        for index, label in enumerate(labels):
            label.setStyleSheet(style)
            buttons[index].setText(f"Set DTC{index + 1} {next_state}")

        self.set_all_dtc.setText(f"Set all DTC {next_state}")
        print("All DTC states:", "ACTIVE" if all_dtc_active else "INACTIVE")

    ############################### EXERCISE 3 ###############################
    def _read_dtc(self, index):
        # Diagram: 25500 = red/ACTIVE; 02550 = green/INACTIVE.
        color_code = "25500" if dtc_states[index] else "02550"
        response = f"0x62{index + 1:02d}{color_code}"
        self._send_message(response)

    def read_dtc1(self, data):
        self._read_dtc(0)

    def read_dtc2(self, data):
        self._read_dtc(1)

    def read_dtc3(self, data):
        self._read_dtc(2)

    def read_dtc4(self, data):
        self._read_dtc(3)

    ############################### EXERCISE 4 ###############################
    def _set_led(self, index, data):
        # Diagram: S=1 -> green; S=0 -> red.
        state = data[-1]

        if state not in ("0", "1"):
            self._send_message("INVALID_LED_STATE")
            return

        labels = [
            self.led1_state,
            self.led2_state,
            self.led3_state,
            self.led4_state,
        ]
        labels[index].setStyleSheet(GREEN_STYLE if state == "1" else RED_STYLE)

        response = f"0x6E{index:02d}{state}"
        self._send_message(response)

    def set_led0(self, data):
        self._set_led(0, data)

    def set_led1(self, data):
        self._set_led(1, data)

    def set_led2(self, data):
        self._set_led(2, data)

    def set_led3(self, data):
        self._set_led(3, data)


class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        global stop_thread
        global conn
        global server_socket

        result = QtWidgets.QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )

        if result == QtWidgets.QMessageBox.Yes:
            stop_thread = True

            for current_socket in (conn, server_socket):
                if current_socket is not None:
                    try:
                        current_socket.close()
                    except OSError:
                        pass

            event.accept()
        else:
            event.ignore()

    def center(self):
        frame_geometry = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(
            QtWidgets.QApplication.desktop().cursor().pos()
        )
        center_point = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MyWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)
    main_window.center()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
