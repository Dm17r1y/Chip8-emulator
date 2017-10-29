#!/usr/bin/python3

from interpreter import Interpreter
from controller import Controller
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from display import Point
import os


class MainWindow(QtWidgets.QWidget):

    def __init__(self, game, speed):
        super().__init__()
        self.sound = QtMultimedia.QSound('beep.wav')
        self.controller = Controller()
        self.interpreter = Interpreter(game, self.controller, self.sound.play)
        self.display = Display(self)
        self.display.move(0, 0)
        self.display.resize(640, 320)
        self.resize(640, 320)
        self.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.main_loop)
        self.timer.start(10 - (speed / 10))

    def main_loop(self):
        self.interpreter.execute_next_command()
        if self.interpreter.need_redraw:
            self.display.repaint()
            self.interpreter.need_redraw = False
        self.interpreter.delay_timer.tick()
        self.interpreter.sound_timer.tick()

    def keyPressEvent(self, QKeyEvent):
        self.controller.set_key_code(QKeyEvent.key())

    def keyReleaseEvent(self, QKeyEvent):
        self.controller.release_key()


class Display(QtWidgets.QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.interpreter = parent.interpreter

    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        display = self.interpreter.display
        for x in range(display.WIDTH):
            for y in range(display.HEIGHT):
                point = display.get_pixel(Point(x, y))
                if point == 1:
                    painter.fillRect(x*10, y*10, 10, 10, QtGui.QColor("white"))
                else:
                    painter.fillRect(x*10, y*10, 10, 10, QtGui.QColor("black"))

class StartWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.resize(200, 100)

        vbox_layout = QtWidgets.QVBoxLayout()

        button = QtWidgets.QPushButton(self)
        button.setText("Start")
        button.resize(100, 50)
        button.clicked.connect(self.start_game)
        vbox_layout.addWidget(button)

        change_speed_label = QtWidgets.QLabel("Speed", self)
        vbox_layout.addWidget(change_speed_label)

        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setSliderPosition(85)
        vbox_layout.addWidget(self.sld)

        self.games = QtWidgets.QComboBox()
        game_list = [game for game in os.listdir("games")]
        self.games.addItems(game_list)
        vbox_layout.addWidget(self.games)

        vbox_layout.addStretch(1)
        self.setLayout(vbox_layout)
        self.show()

    def start_game(self, *args, **kwargs):
        self.window = MainWindow("games/" + self.games.currentText(),
                                 self.sld.value())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = StartWindow()
    sys.exit(app.exec_())
