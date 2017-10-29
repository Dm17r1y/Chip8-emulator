#!/usr/bin/python3

from PyQt5.QtCore import Qt


class Controller:

    def __init__(self):
        self._return_value = None

    def get_key_code(self):
        return self._return_value

    def set_key_code(self, key):
        codes = {
            Qt.Key_0: 0,
            Qt.Key_1: 1,
            Qt.Key_2: 2,
            Qt.Key_3: 3,
            Qt.Key_Q: 4,
            Qt.Key_W: 5,
            Qt.Key_E: 6,
            Qt.Key_R: 7,
            Qt.Key_A: 8,
            Qt.Key_S: 9,
            Qt.Key_D: 10,
            Qt.Key_F: 11,
            Qt.Key_Z: 12,
            Qt.Key_X: 13,
            Qt.Key_C: 14,
            Qt.Key_V: 15
        }
        if key in codes:
            self._return_value = codes[key]

    def release_key(self):
        self._return_value = None
