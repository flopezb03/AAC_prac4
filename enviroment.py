import queue
import random
import threading
import time

from animal import PredatorGroup, Lion, Group, Zebra, Hyena


class Game:
    def __init__(self):
        self.all_threads = []
        self.lions = []
        self.hyenas = []
        self.zebras = []
        self.winner = threading.Event()
        self.winner_group = None
        self.winner_lock = threading.Lock()
        self.board = None
        self.group_id = 0
        self.animal_id = 0
        self.events = queue.Queue()

    def incc_group_id(self):
        g_id = self.group_id
        self.group_id += 1
        return g_id
    def incc_animal_id(self):
        a_id = self.animal_id
        self.animal_id += 1
        return a_id
    def init_groups_type(self, animal_type, num_animals, min_size, max_size):
        # Array de int, cada uno representa el tamaño de un grupo
        animal_groups_sizes = [1]
        animal_count = 1
        while animal_count < num_animals:
            r = random.randint(min_size, max_size)
            if animal_count + r > num_animals:
                r = num_animals - animal_count
            animal_groups_sizes.append(r)
            animal_count += r

        # Array de grupos de animal_type
        out = []
        for num in animal_groups_sizes:
            if animal_type is Zebra:
                group = Group(self.incc_group_id())
            else:
                group = PredatorGroup(self.incc_group_id())
            out.append(group)
            for i in range(num):
                a = animal_type(self.incc_animal_id(), group, self.board, self.winner, self.set_winner_group, self.events)
                group.animals.append(a)
                self.all_threads.append(a)
        return out



    def create_animal(self,animal_type,group,x,y):
        self.board.board[y][x].lock.acquire()
        animal = animal_type(self.incc_animal_id(), group, self.board, self.winner, self.set_winner_group, self.events)
        self.board.spawn_animal(x,y,animal)
        group.animals.append(animal)
        self.board.board[y][x].lock.release()
        return animal

    def set_winner_group(self,group):
        with self.winner_lock:
            self.winner.set()
            self.winner_group = group
            #print("--------------------------------- GANADOR ----------------------------------------------")

    def event_listener(self):
        while not self.winner.is_set():
            event,animal = self.events.get()
            if self.winner.is_set() and event == "Spawn Zebra":
                #print("------------------------------------------------ SPAWN ZEBRA --------------------------------------------------------------")
                #   Crear nueva cebra
                group = animal.group
                x, y = random.randint(0, self.board.w - 1), random.randint(0, self.board.h - 1)
                while not self.board.is_square_empty(x, y):  # Buscar un lugar vacío
                    x, y = random.randint(0, self.board.w - 1), random.randint(0, self.board.h - 1)

                t = self.create_animal(Zebra, group, x, y)
                self.all_threads.append(t)
                t.start()                                                                   #   Falta hacer join

    def init_groups(self, num_lions):
        num_hyenas = num_lions*3
        num_zebras = num_lions*6

        self.lions = self.init_groups_type(Lion,num_lions,5,15)
        self.hyenas = self.init_groups_type(Hyena, num_hyenas, 10, 20)
        self.zebras = self.init_groups_type(Zebra, num_zebras, 7, 30)

    def init_spawn(self):
        g_queue = queue.Queue()
        for i in range(max(len(self.lions), len(self.hyenas), len(self.zebras))):
            if i < len(self.lions):
                g_queue.put(self.lions[i])
            if i < len(self.hyenas):
                g_queue.put(self.hyenas[i])
            if i < len(self.zebras):
                g_queue.put(self.zebras[i])

        x = 0
        y = 0
        while not g_queue.empty():
            g = g_queue.get()
            if self.board.w - x > len(g.animals):   # Si el grupo cabe en la fila y -> meto el grupo en la fila y, despues actualizo x
                for i in range(len(g.animals)):
                    self.board.spawn_animal(x+i,y,g.animals[i])
                x += len(g.animals) +1
            else:                                   # Si no, actualizo y++ y x=0, y meto el grupo
                y += 2
                x = 0
                for i in range(len(g.animals)):
                    self.board.spawn_animal(x+i,y,g.animals[i])
                x += len(g.animals) +1


    def start(self):

        print("Tamaño de tablero personalizado? (y/n)")
        c = "n"
        if c == 'y':
            print("Altura:")
            h = int(input())
            print("Ancho: ")
            w = int(input())
            self.board = Board(h, w)
        elif c == 'n':
            h = 30
            w = 30
            self.board = Board(h, w)
        else:
            print("Saliendo del programa...")
            exit()
        print("Numero de animales personalizado? (y/n)")
        c = "n"
        if c == 'y':
            print("Introduce numero de leones:")
            num_lions = input()
        elif c == 'n':
            num_lions = int((h * w * 0.3) / 10)
        else:
            print("Saliendo del programa...")
            exit()


        self.init_groups(num_lions)
        self.init_spawn()

        print("--- ESTADO INICIAL DEL TABLERO ---")
        print(self.board)

        listener_thread = threading.Thread(target=self.event_listener)
        listener_thread.start()
        for t in self.all_threads:
            t.start()
        for t in self.all_threads:
            t.join()
        listener_thread.join()



        print(f"Ganador g_id: {self.winner_group.g_id}")



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