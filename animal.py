import random
import threading
from time import sleep


class Animal(threading.Thread):
    def __init__(self, a_id, group, board, winner):
        super().__init__(group)
        self.a_id = a_id
        self.group = group
        self.board = board
        self.winner = winner
        self.x = None
        self.y = None
        self.speed = 0
        self.rest_time = 0
        self.adjacent_squares = []

    def update_adjacent_squares(self):
        self.adjacent_squares = self.board.adjacent_squares(self.x,self.y)


    def inspect(self):
        possible_squares = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (i == 0 and j == 0):
                    x = self.x + j
                    y = self.y + i
                    if 0 <= x < self.board.w and 0 <= y < self.board.h and self.board.is_square_empty(x, y):
                        possible_squares.append((x,y))
        if len(possible_squares) == 0:
            return False

    def move(self):
        #   Buscar donde moverse
        dest_in_group = []
        dest_out_group = []
        for s in self.adjacent_squares:
            if s.is_empty():
                if s.is_group_adjacent(self,self.group,self.board.adjacent_squares(s.x,s.y)):
                    dest_in_group.append(s)
                else:
                    dest_out_group.append(s)
        if len(dest_out_group) == 0 and len(dest_in_group) == 0:
            print(f"{self.a_id} no se puede mover")
            return False

        #   Decidir donde moverse
        possible_destinations = None
        if len(dest_out_group) == 0:
            possible_destinations = dest_in_group
            print(f"{self.a_id} se mueve dentro del grupo")
        elif len(dest_in_group) == 0:
            possible_destinations = dest_out_group
            print(f"{self.a_id} se mueve fuera del grupo")
        else:
            r = random.random()
            if r > 0.7:
                print(f"{self.a_id} se mueve fuera del grupo")
                possible_destinations = dest_out_group
            else:
                print(f"{self.a_id} se mueve dentro del grupo")
                possible_destinations = dest_in_group

        r = random.randint(0,len(possible_destinations)-1)
        dest = possible_destinations[r]

        #   Realizar movimiento
        print(f"{self.a_id} quiere lock({dest.x},{dest.y})")
        dest.lock.acquire()
        print(f"{self.a_id} tiene lock({dest.x},{dest.y})")
        moved = dest.set_animal(self)
        if moved:
            self.board.board[self.y][self.x].animal = None
            self.x = dest.x
            self.y = dest.y
            self.update_adjacent_squares()
            #actualizar manada
            print(self.board)
        print(f"{self.a_id} suelta lock({dest.x},{dest.y})")
        dest.lock.release()


    def rest(self):
        pass

class Predator(Animal):
    def hunt(self):
        pass

    def can_hunt(self):
        pass

class Prey(Animal):
    def __init__(self, a_id, group, board, winner):
        super().__init__(a_id, group, board, winner)
        self.hunted = False

class Lion(Predator):
    def __init__(self, a_id, group, board, winner):
        super().__init__(a_id, group, board, winner)
        self.speed = 0.2

    def run(self):
        x = 10
        while not self.winner and x > 0:
            self.move()
            sleep(self.speed)
            x -= 1

class Hyena(Predator, Prey):
    pass
class Zebra(Prey):
    pass

class Group:
    def __init__(self, g_id):
        self.g_id = g_id
        self.animals = []

class PredatorGroup(Group):
    def __init__(self, id):
        super().__init__(id)
        self.hunts = 0