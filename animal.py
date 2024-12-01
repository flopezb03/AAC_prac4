import random
import threading
from time import sleep


class Animal(threading.Thread):
    def __init__(self, a_id, group, board, winner, game):
        super().__init__()
        self.a_id = a_id
        self.group = group
        self.board = board
        self.winner = winner
        self.game = game
        self.x = None
        self.y = None
        self.speed = 5
        self.rest_time = 5

    def move(self):
        self.board.board[self.y][self.x].lock.acquire()
        if isinstance(self,Prey) and self.hunted == True:
            self.board.board[self.y][self.x].lock.release()
            return False

        #   Buscar donde moverse
        dest_in_group = []
        dest_out_group = []
        for s in self.board.board[self.y][self.x].adjacent_squares:
            if s.is_empty():
                if s.is_group_adjacent(self,self.group):
                    dest_in_group.append(s)
                else:
                    dest_out_group.append(s)
        if len(dest_out_group) == 0 and len(dest_in_group) == 0:
            self.board.board[self.y][self.x].lock.release()
            return False

        #   Decidir donde moverse
        possible_destinations = None
        if len(dest_out_group) == 0:
            possible_destinations = dest_in_group
        elif len(dest_in_group) == 0:
            possible_destinations = dest_out_group
        else:
            r = random.random()
            if r > 0.7:
                possible_destinations = dest_out_group
            else:
                possible_destinations = dest_in_group

        r = random.randint(0,len(possible_destinations)-1)
        dest = possible_destinations[r]

        #   Realizar movimiento
        dest.lock.acquire()
        moved = dest.set_animal(self)
        if moved:
            self.board.board[self.y][self.x].animal = None
            x_aux = self.x
            self.x = dest.x
            y_aux = self.y
            self.y = dest.y
        dest.lock.release()
        if moved:
            self.board.board[y_aux][x_aux].lock.release()
        else:
            self.board.board[self.y][self.x].lock.release()
        return moved


    def rest(self):
        sleep(self.rest_time)

class Predator(Animal):
    def hunt(self):
        self.board.board[self.y][self.x].lock.acquire()
        if isinstance(self,Prey) and self.hunted == True:
            self.board.board[self.y][self.x].lock.release()
            return False

        #   Buscar que cazar
        possible_preys = []
        for s in self.board.board[self.y][self.x].adjacent_squares:
            if not s.is_empty() and self.can_hunt(s):
                possible_preys.append(s)
        if len(possible_preys) == 0:
            self.board.board[self.y][self.x].lock.release()
            return False

        #   Decidir que cazar
        r = random.randint(0,len(possible_preys)-1)
        prey = possible_preys[r]

        #   Realizar caza
        prey.lock.acquire()
        hunt = not prey.is_empty() and self.can_hunt(prey)
        if hunt:
            if not self.winner.is_set():
                if isinstance(self,Lion):
                    c = "Leon"
                else:
                    c = "Hiena"
                if isinstance(prey.animal,Hyena):
                    p = "Hiena"
                else:
                    p = "Cebra"
                print(f"{c} {self.a_id} en la posicion ({self.x},{self.y}) ha cazado a {p} {prey.animal.a_id} en la posicion ({prey.animal.x},{prey.animal.y})")

            prey_type = prey.animal.__class__
            prey.animal.hunted = True
            prey.animal = self
            self.board.board[self.y][self.x].animal = None
            x_aux = self.x
            self.x = prey.x
            y_aux = self.y
            self.y = prey.y

            self.group.lock.acquire()
            if isinstance(self,Lion) and prey_type is Hyena:
                self.group.hunts += 2
            else:
                self.group.hunts += 1
            if self.group.hunts >= 20 and not self.winner.is_set():
                self.game.set_winner_group(self.group)
            self.group.lock.release()

        prey.lock.release()
        if hunt:
            self.board.board[y_aux][x_aux].lock.release()
        else:
            self.board.board[self.y][self.x].lock.release()
        return hunt

    def can_hunt(self, prey):
        pass

class Prey(Animal):
    def __init__(self, a_id, group, board, winner, game):
        super().__init__(a_id, group, board, winner, game)
        self.hunted = False

class Lion(Predator):
    def __init__(self, a_id, group, board, winner, game):
        super().__init__(a_id, group, board, winner, game)
        self.speed = 0.5 +self.group.speed+random.uniform(0,0.4)
        self.rest_time = 5+self.group.rest_time+random.uniform(0,2)

    def can_hunt(self, prey):
        if isinstance(prey.animal,Zebra):
            return True
        elif isinstance(prey.animal,Hyena):
            allies = 0
            hyenas = 0
            for s in self.board.board[self.y][self.x].adjacent_squares:
                if isinstance(s.animal,Lion):
                    allies += 1
            for s in prey.adjacent_squares:
                if isinstance(s.animal,Hyena):
                    hyenas +=1
            return allies >= hyenas
        else:
            return False

    def run(self):
        while not self.winner.is_set():
            if not self.hunt():
                if not self.move():
                    self.rest()
            sleep(self.speed)

class Hyena(Predator, Prey):
    def __init__(self, a_id, group, board, winner, game):
        super().__init__(a_id, group, board, winner, game)
        self.speed = 3.9+self.group.speed+random.uniform(0,0.5)
        self.rest_time = 2+self.group.rest_time+random.uniform(0,0.5)

    def can_hunt(self, prey):
        if isinstance(prey.animal,Zebra):
            allies = 0
            zebras = 0
            for s in self.board.board[self.y][self.x].adjacent_squares:
                if isinstance(s.animal,Hyena):
                    allies += 1
            for s in prey.adjacent_squares:
                if isinstance(s.animal,Zebra):
                    zebras +=1
            return allies >= zebras
        else:
            return False

    def run(self):
        while not self.hunted and not self.winner.is_set():
            if not self.hunt():
                if not self.move():
                    self.rest()
            sleep(self.speed)

        if self.hunted:
            self.group.lock.acquire()
            self.group.animals.remove(self)
            self.group.lock.release()

class Zebra(Prey):
    def __init__(self, a_id, group, board, winner, game):
        super().__init__(a_id, group, board, winner, game)
        self.speed = 2+self.group.speed+random.uniform(0,0.8)
        self.rest_time = 0.5+self.group.rest_time+random.uniform(0,0.1)

    def run(self):
        while not self.hunted and not self.winner.is_set():
            if not self.move():
                self.rest()
            sleep(self.speed)

        if self.hunted:
            self.game.spawn_zebra(self.group)
            self.group.lock.acquire()
            self.group.animals.remove(self)
            self.group.lock.release()



class Group:
    def __init__(self, g_id):
        self.g_id = g_id
        self.animals = []
        self.lock = threading.Lock()
        self.speed = random.uniform(0,1)
        self.rest_time = random.uniform(0,0.5)

class PredatorGroup(Group):
    def __init__(self, g_id):
        super().__init__(g_id)
        self.hunts = 0