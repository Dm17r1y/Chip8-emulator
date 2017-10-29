#!/usr/bin/python3

from interpreter import Interpreter
from controller import Controller
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from display import Point
import datetime
import re
import os


class MainWindow(QtWidgets.QWidget):

    def __init__(self, game, speed, sprites, state=None):
        super().__init__()
        self.game = game
        self.sound = QtMultimedia.QSound('beep.wav')
        self.controller = Controller()

        path = os.path.join("games", game)
        self.interpreter = Interpreter(path, self.controller, sprites,
                                       self.sound.play)
        if state is not None:
            self.interpreter.load_state(state)

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

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F4:
            self.save_game()
        else:
            self.controller.set_key_code(event.key())

    def keyReleaseEvent(self, event):
        self.controller.release_key()

    def save_game(self):
        interpreter_state = self.interpreter.serialize_state()
        path = os.path.join("saves", self.game  + "#"
                            + datetime.datetime.now()
                            .strftime('%Y-%m-%d %H:%M:%S'))
        with open(path, "wb") as f:
            f.write(self.game.encode())
            f.write(b'\n')
            f.write(interpreter_state)

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
        self.move(100, 100)

        vbox_layout = QtWidgets.QVBoxLayout()

        start_button = QtWidgets.QPushButton(self)
        start_button.setText("Start")
        start_button.clicked.connect(self.start_game)
        vbox_layout.addWidget(start_button)

        change_speed_label = QtWidgets.QLabel("Speed", self)
        vbox_layout.addWidget(change_speed_label)

        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setSliderPosition(85)
        vbox_layout.addWidget(self.sld)

        self.games = QtWidgets.QComboBox()
        game_list = [game for game in os.listdir("games")]
        self.games.addItems(game_list)
        vbox_layout.addWidget(self.games)

        sprites_label = QtWidgets.QLabel("Sprites:", self)
        vbox_layout.addWidget(sprites_label)

        self.sprites = QtWidgets.QComboBox()
        sprite_list = [sprite for sprite in os.listdir("sprites")]
        self.sprites.addItems(sprite_list)
        vbox_layout.addWidget(self.sprites)

        load_button = QtWidgets.QPushButton(self)
        load_button.setText("Load game")
        load_button.clicked.connect(self.load_game)
        vbox_layout.addWidget(load_button)

        vbox_layout.addStretch(1)
        self.setLayout(vbox_layout)
        self.show()


    def start_game(self, *args, **kwargs):
        path = os.path.join("sprites" , self.sprites.currentText())
        with open(path, "rb") as f:
            sprites = [byte for byte in f.read()]

        if len(sprites) != 80:
            raise Exception("Sprites length must be 80 bytes")

        game = self.games.currentText()
        speed = self.sld.value()
        self.window = MainWindow(game, speed, sprites)

    def load_game(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "load save",
                                                     "saves")[0]
        if file != '':
            with open(file, "rb") as f:
                data = f.read()
                match = re.match(rb"(.*?)\n", data)
                game = match.group(1).decode()
                speed = self.sld.value()
                sprites = self.sprites.currentText()
                state = data[match.end():]
                self.window = MainWindow(game, speed, sprites, state)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = StartWindow()
    sys.exit(app.exec_())
