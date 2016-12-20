#!/usr/bin/env python
from itertools import repeat
from random import randint, choice

class Boat(object):
    def __init__(self, name, symbol, length):
        self.length = length
        self.x = 0
        self.y = 0
        self.isHorizontal = False
        self.hits = list(repeat(True, length))
        self.name = name
        self.symbol = symbol

    def isHit(self, position):
        return not self.hits[position]

    def markHit(self, position):
        self.hits[position] = False

    def isSunk(self):
        return not any(self.hits)

    def __repr__(self):
        return "{} (length {}) at ({}, {})".format(
            self.name, self.length, self.x, self.y)

class Carrier(Boat):
    def __init__(self):
        super(Carrier, self).__init__("Carrier", "C", 5)

class Battleship(Boat):
    def __init__(self):
        super(Battleship, self).__init__("Battleship", "B", 4)

class Cruiser(Boat):
    def __init__(self):
        super(Cruiser, self).__init__("Cruiser", "c", 3)

class Submarine(Boat):
    def __init__(self):
        super(Submarine, self).__init__("Submarine", "S", 3)

class Destroyer(Boat):
    def __init__(self):
        super(Destroyer, self).__init__("Destroyer", "D", 2)


class Board(object):
    def __init__(self, width = 16, height = 16, isPublic = False):
        self.width = min(width, 16)
        self.height = min(height, 16)
        self.boats = []
        self.misses = []
        self.isPublic = isPublic
        self.showMisses = True
        self.place(Carrier())
        self.place(Battleship())
        self.place(Cruiser())
        self.place(Submarine())
        self.place(Destroyer())

    def place(self, boat):
        while True:
            boat.x = randint(0, self.width - 1)
            boat.y = randint(0, self.height - 1)
            boat.isHorizontal = choice((True, False))
            if self.isOutOfBounds(self.boatCoordinate(boat, boat.length - 1)):
                continue
            overlaps = False
            for x in range(boat.length):
                if self.isHit(self.boatCoordinate(boat, x)) is not None:
                    overlaps = True
                    break
            if overlaps is True:
                continue
            break

        self.boats.append(boat)

    def isHit(self, point):
        for boat in self.boats:
            for x in range(boat.length):
                if self.boatCoordinate(boat, x) == point:
                    return (boat, x)
        return None

    def isOutOfBounds(self, point):
        return (point[0] < 0 or
            point[0] >= self.width or
            point[1] < 0 or
            point[1] >= self.width)

    def boatCoordinate(self, boat, position):
        if boat.isHorizontal:
            return (boat.x + position, boat.y)
        return (boat.x, boat.y + position)

    def gameOver(self):
        for boat in self.boats:
            if not boat.isSunk():
                return False
        return True

    def shoot(self, x, y):
        result = self.isHit((x, y))
        if result is not None:
            (boat, position) = result
            boat.markHit(position)
            return True
        else:
            self.misses.append((x, y))
            return False

    def __repr__(self):
        result = "  0 1 2 3 4 5 6 7 8 9 A B C D E F\n"
        for y in range(self.height):
            result += "{0:X}".format(y)
            for x in range(self.width):
                result += " "
                hitCheck = self.isHit((x, y))
                if hitCheck is not None:
                    isHit = hitCheck[0].isHit(hitCheck[1])
                    if isHit is True:
                        result += "X"
                    elif self.isPublic is True:
                        result += hitCheck[0].symbol
                    else:
                        result += "*"
                else:
                    if self.showMisses is True and (x, y) in self.misses:
                        result += "."
                    else:
                        result += "*"
            result += "\n"
        return result

class Game(object):
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player1Board = Board(isPublic = self.player1.showPieces)
        self.player1.setDimensions(
            self.player1Board.width, self.player1Board.height)
        self.player2 = player2
        self.player2Board = Board(isPublic = self.player2.showPieces)
        self.player2.setDimensions(
            self.player2Board.width, self.player2Board.height)

    def play(self):
        while not (self.player1Board.gameOver() or self.player2Board.gameOver()):
            print self
            (x, y) = self.player1.getMove()
            result = self.player2Board.shoot(x, y)
            self.reportMove(self.player1.name, x, y, result)
            if self.player2Board.gameOver():
                print "{} WINS".format(self.player1.name)
            else:
                (x, y) = self.player2.getMove()
                result = self.player1Board.shoot(x, y)
                self.reportMove(self.player2.name, x, y, result)
                if self.player1Board.gameOver():
                    print "{} WINS".format(self.player2.name)

    def reportMove(self, prefix, x, y, result):
        output = "{} fires ({}, {}): ".format(prefix, x, y)
        if result is True:
            output += "HIT"
        else:
            output += "MISS"
        print output

    def __repr__(self):
        result = "{:^34}    {:^34}\n".format(
            self.player1.name, self.player2.name)
        player1 = str(self.player1Board).split("\n")
        player2 = str(self.player2Board).split("\n")
        for x in range(len(player1)):
            result += player1[x] + "     " + player2[x] + "\n"
        return result

class Human(object):
    def __init__(self):
        self.name = "Human Player"
        self.showPieces = True

    def setDimensions(self, boardWidth, boardHeight):
        pass

    def getMove(self):
        move = ""
        while move == "":
            try:
                move = int(input("Your move: "))
            except NameError:
                print "Invalid move."
            else:
                if move > 255:
                    print "Invalid move."
                    move = ""
        hex = "{0:02X}".format(move)
        x = int(hex[0], 16)
        y = int(hex[1], 16)
        return (x, y)

class Computer(object):
    def __init__(self):
        self.name = "Computer"
        self.showPieces = False
        self.boardWidth = 0
        self.boardHeight = 0

    def setDimensions(self, boardWidth, boardHeight):
        self.boardWidth = boardWidth
        self.boardHeight = boardHeight

    def getMove(self):
        x = randint(0, self.boardWidth - 1)
        y = randint(0, self.boardHeight - 1)
        return (x, y)

if __name__ == '__main__':
    game = Game(Human(), Computer())
    try:
        game.play()
    except KeyboardInterrupt:
        exit

