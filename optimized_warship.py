# -*- coding: utf-8 -*-
#!/usr/bin/env python

# Form implementation generated from reading ui file 'D:\QT\warship.ui'
#
# Created: Mon Aug 18 19:54:35 2014
# by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from random import randint
from random import choice
import string

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Board(object):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    WATER = 'O'
    MISSED = 'x'
    TARGETED = 'X'
    NEARBY_WATER = 'W'
    SHIP = 'S'

    DEFAULT_FLEET = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
    _occupied_territory = set()
    fleet = []

    OFFSETS = {UP: (1, 0),
               DOWN: (-1, 0),
               LEFT: (0, 1),
               RIGHT: (0, -1)}

    def __init__(self, size=10, ships=None):
        self.BOARD_SIZE = size
        self._board = [[self.WATER] * size for dummy in range(size)]
        self.ships = ships if ships else self._generate_ships(self.DEFAULT_FLEET)
        self.HEADER = string.ascii_uppercase[:self.BOARD_SIZE]

    def _random_row(self):
        return randint(0, self.BOARD_SIZE - 1)

    def _random_col(self):
        return randint(0, self.BOARD_SIZE - 1)

    def _is_on_board(self, some_point):
        x_coord, y_coord = some_point
        return 0 <= x_coord < self.BOARD_SIZE and 0 <= y_coord < self.BOARD_SIZE

    def _locate_ship(self, start, size, direction):
        start_x, start_y = start
        offset_x, offset_y = self.OFFSETS[direction]
        end_point = (start_x + offset_x * (size - 1), start_y + offset_y * (size - 1))
        if self._is_on_board(end_point):
            return tuple((start_x + offset_x * index, start_y + offset_y * index) for index in range(size))

    def _place_ship_on_board(self, ship_size):
        possible_layout = {}
        while not possible_layout:
            ship_nose = self._random_row(), self._random_col()
            if ship_nose in self._occupied_territory:
                continue
            for direction in self.OFFSETS:
                ship_layout = self._locate_ship(ship_nose, ship_size, direction)
                if ship_layout and not set(ship_layout) & self._occupied_territory:
                    possible_layout[direction] = ship_layout
        dir_choice = choice(possible_layout.keys())
        ship = possible_layout[dir_choice]
        self._occupied_territory.update(self._get_ship_square(ship))
        return ship

    def _generate_ships(self, fleet_amount):
        genereted_ships = []
        for ship_size in fleet_amount:
            ship = self._place_ship_on_board(ship_size)
            genereted_ships.append(ship)
            self.fleet.extend(ship)
        return genereted_ships

    def is_ship_alive(self, ship):
        for part in ship:
            if self.get_point_value(part) != self.TARGETED:
                return True
        return False

    def set_point_to(self, point, value):
        x_coord, y_coord = point
        self._board[y_coord][x_coord] = value

    def get_point_value(self, point):
        x_coord, y_coord = point
        return self._board[y_coord][x_coord]

    def mark_as_dead(self, ship):
        self.ships.remove(ship)
        water = self.get_nearby_water(ship)
        for point in water:
            self.set_point_to(point, self.MISSED)

    def get_nearby_water(self, ship):
        return self._get_ship_square(ship, is_ship_exluded=True)

    def _get_ship_square(self, ship, is_ship_exluded=False):
        sorted_ship = sorted(ship)
        pt_x, pt_y = sorted_ship[0][0] - 1, sorted_ship[0][1] - 1
        horizontal_layout = sorted_ship[0][1] == sorted_ship[1][1] if len(sorted_ship) > 1 else True
        if horizontal_layout:
            range_y = range(3); range_x = range(2 + len(sorted_ship))
        else:
            range_x = range(3); range_y = range(2 + len(sorted_ship))
        square = set((pt_x + x, pt_y + y) for x in range_x for y in range_y if self._is_on_board((pt_x + x, pt_y + y)))
        if is_ship_exluded:
            square.difference_update(ship)
        return square

    def reset_board(self, ships=None):
        self._board = [[self.WATER] * self.BOARD_SIZE for dummy in range(self.BOARD_SIZE)]
        self.ships = ships if ships else self._generate_ships(self.DEFAULT_FLEET)


class WarshipWindow(object):
    WINDOW_NAME = "Warship"
    LETTERS = "ABCDEFGHIJ"
    NUMBERS = range(1, 11)

    _buttons = {}
    _my_turn = True

    def __init__(self, parent=None, size=10):
        if parent:
            parent.setObjectName(_fromUtf8(self.WINDOW_NAME))
            parent.resize(551, 371)
            parent.setAutoFillBackground(True)
            parent.setWindowTitle(_translate(self.WINDOW_NAME, self.WINDOW_NAME, None))

        self.GRID_SEIZE = size
        self._board = Board(size)
        self._letters = [0 for dummy_x in range(self.GRID_SEIZE)]
        self._numbers = [0 for dummy_x in range(self.GRID_SEIZE)]
        self.window = QtGui.QWidget(parent)
        self.window.setGeometry(QtCore.QRect(20, 20, 280, 281))
        self.window.setObjectName(_fromUtf8("widget"))

        self.gridLayout = QtGui.QGridLayout(self.window)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("GRID"))

        self._label_font = QtGui.QFont()
        self._label_font.setPointSize(12)

        self._btn_font = QtGui.QFont()
        self._btn_font.setPointSize(12)
        self._btn_font.setBold(True)

        self._btn_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self._btn_size = QtCore.QSize(20, 20)

        for idx_x in range(self.GRID_SEIZE):
            # adding Letter Labels
            letter = QtGui.QLabel(self.window)
            letter.setFont(self._label_font)
            letter.setAlignment(QtCore.Qt.AlignCenter)
            letter.setObjectName(_fromUtf8("label_x" + str(idx_x)))
            letter.setText(_translate(self.WINDOW_NAME, self.LETTERS[idx_x], None))
            self._letters[idx_x] = letter
            self.gridLayout.addWidget(letter, 0, idx_x + 1)
            # adding Number labels
            number = QtGui.QLabel(self.window)
            number.setFont(self._label_font)
            number.setAlignment(QtCore.Qt.AlignCenter)
            number.setObjectName(_fromUtf8("label_y" + str(idx_x)))
            number.setText(_translate(self.WINDOW_NAME, str(self.NUMBERS[idx_x]), None))
            self._numbers[idx_x] = number
            self.gridLayout.addWidget(number, idx_x + 1, 0)
            for idx_y in range(self.GRID_SEIZE):
                # adding buttons
                button = QtGui.QPushButton(self.window)
                button.setProperty("class", "game-board.normal")
                button.setFont(self._btn_font)
                button.setMinimumSize(self._btn_size)
                button.setMaximumSize(self._btn_size)
                button.connect(button, QtCore.SIGNAL('clicked()'), self.strike)
                button.setObjectName(_fromUtf8("pushButton_{0}X{1}".format(idx_x, idx_y)))
                self._buttons[(idx_x, idx_y)] = button
                self.gridLayout.addWidget(button, idx_y + 1, idx_x + 1)

        if parent:
            QtCore.QMetaObject.connectSlotsByName(parent)

    def get_point(self, button):
        name = str(button.objectName())
        point = tuple(int(x) for x in name.split('_')[1].split('X'))
        return point

    def set_hit(self, button):
        button.setProperty("class", "hit")
        button.style().unpolish(button)
        button.style().polish(button)
        button.update()
        button.setText("X")
        button.setEnabled(False)

    def set_missed(self, button):
        button.setProperty("class", "missed")
        button.style().unpolish(button)
        button.style().polish(button)
        button.update()
        button.setText(u"\u2022")
        button.setEnabled(False)

    def reveal_ship(self, ship):
        water = self._board.get_nearby_water(ship)
        for point in water:
            button = self._buttons[point]
            self.set_missed(button)

    def strike(self):
        if self._my_turn:
            sender = self.window.sender()
            guess_point = self.get_point(sender)
            if guess_point in self._board.fleet:
                self.set_hit(sender)
                self._board.set_point_to(guess_point, self._board.TARGETED)
                self._board.fleet.remove(guess_point)
                is_finished = False
                for ship in self._board.ships:
                    if not self._board.is_ship_alive(ship):
                        print "Congratulations! Ship is sunk!"
                        self._board.mark_as_dead(ship)
                        self.reveal_ship(ship)
                        is_finished = True
                        break
                if not is_finished:
                    print "Congratulations! Ship is targeted!"
            else:
                self.set_missed(sender)
                self._board.set_point_to(guess_point, self._board.MISSED)
                print "You missed my battleship!"


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    form = QtGui.QWidget()
    form.setStyleSheet(open("styles.css").read())
    ui = WarshipWindow(form)
    form.show()
    sys.exit(app.exec_())