import threading

from animal import PredatorGroup, Lion, Group, Zebra, Hyena


class Game:
    def __init__(self):
        self.lions = []
        self.hyenas = []
        self.zebras = []
        self.winner = False
        self.winner_id = None
        self.board = None
        self.group_id = 0
        self.animal_id = 0

    def incc_group_id(self):
        g_id = self.group_id
        self.group_id = g_id+1
        return g_id
    def incc_animal_id(self):
        a_id = self.animal_id
        self.animal_id = a_id+1
        return a_id
    def create_animal(self,animal_type,group,x,y):
        animal = animal_type(self.incc_animal_id(),group,self.board,self.winner)
        self.board.spawn_animal(x,y,animal)
        group.animals.append(animal)


    def start(self):

        print("Tamaño de tablero personalizado? (y/n)")
        c = "n"  # input()
        if c == 'y':
            print("Altura:")
            h = int(input())
            print("Ancho: ")
            w = int(input())
            self.board = Board(h, w)
        elif c == 'n':
            h = 4
            w = 4
            self.board = Board(h, w)
        else:
            print("Saliendo del programa...")
            exit()




        lion_group1 = PredatorGroup(self.incc_group_id())
        self.lions.append(lion_group1)
        positions = [(0,0),(1,0),(0,1)]
        for p in positions:
            self.create_animal(Lion,lion_group1,p[0],p[1])

        hyena_group1 = PredatorGroup(self.incc_group_id())
        self.hyenas.append(hyena_group1)
        positions = [(3, 0), (3, 1), (3, 2)]
        for p in positions:
            self.create_animal(Hyena, hyena_group1, p[0], p[1])

        zebra_group1 = Group(self.incc_group_id())
        self.zebras.append(zebra_group1)
        positions = [(2, 0), (2, 1), (2, 2)]
        for p in positions:
            self.create_animal(Zebra,zebra_group1, p[0], p[1])




        for t in self.lions[0].animals:
            t.start()
        for t in self.hyenas[0].animals:
            t.start()
        for t in self.zebras[0].animals:
            t.start()
        for t in self.lions[0].animals:
            t.join()
        for t in self.hyenas[0].animals:
            t.join()
        for t in self.zebras[0].animals:
            t.join()




class Board:
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self.board = [[Square(j,i) for j in range(w)] for i in range(h)]
        for x in range(w):
            for y in range(h):
                self.board[y][x].adjacent_squares = self.adjacent_squares(x,y)

    def is_square_empty(self,x, y):
        return self.board[y][x].animal is None
    def adjacent_squares(self,x,y):
        if not(0<=x<self.w) or not(0<=y<self.h):
            return []
        adjacent_squares = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (i == 0 and j == 0):
                    x2 = x + j
                    y2 = y + i
                    if 0 <= x2 < self.w and 0 <= y2 < self.h:
                        adjacent_squares.append(self.board[y2][x2])
        return adjacent_squares
    def spawn_animal(self, x, y, a):
        self.board[y][x].animal = a
        a.x = x
        a.y = y

    def __str__(self):
        out = ""
        for i in range(self.h):
            line = ""
            for j in range (self.w):
                line += str(self.board[i][j])
                if j != self.w:
                    line += " "
            out += line
            if i != self.h:
                out += "\n"
        return out


class Square:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.adjacent_squares = []
        self.animal = None
        self.lock = threading.Lock()

    def is_empty(self):
        return self.animal is None
    def set_animal(self, a):
        if self.animal is None:
            self.animal = a
            return True
        return False
    def is_group_adjacent(self,animal,group):
        for s in self.adjacent_squares:
            if s.animal is not None and s.animal != animal and s.animal.group == group:
                return True
        return False

    def __str__(self):
        if self.animal is not None:
            if isinstance(self.animal,Lion):
                return "L"
            elif isinstance(self.animal,Zebra):
                return "Z"
            elif isinstance(self.animal,Hyena):
                return "H"
        else:
            return "."



if __name__ == "__main__":
    game = Game()
    game.start()