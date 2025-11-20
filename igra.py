from abc import ABC, abstractmethod
from random import uniform, randint, choice,random
   
class Entity(ABC):
    def __init__(self,position: tuple[int, int] = (0,0)) -> None:
        self.position = position
    
    @abstractmethod
    def symbol(self) -> str:
        pass



class Board():
    def __init__(self, rows:int,cols:int,grid: list[list[tuple[Entity| None, bool]]],start: tuple[int,int],goal:tuple[int,int]) -> None:
        self.rows = rows
        self.cols = cols
        self.grid = grid
        self.start = start
        self.goal = goal

    def place(self,entity:Entity, pos: tuple[int,int]) -> None:
        coors = self.grid[[pos[0]][pos[1]]]
        coors = (entity, coors[1])
        
    def entity_at(self, pos: tuple[int, int]) -> Entity | None:
        return self.grid[[pos[0]][pos[1]]]
    
    def in_bounds(self, pos: tuple[int, int]) -> bool:
        if pos[0] < self.rows and pos[1] < self.cols and pos[0]>=0 and pos[1] >= 0:
            return True
        else:
            return False
    def render(self, player: "Player") -> None:
        for i in range(self.rows):
            for y in range(self.cols):
                coors = self.grid[i][y]
                if (i,y) == player.position and isinstance(coors[0], Enemy):
                    print(f'|{player.symbol()},E|', end = "")
                elif (i,y) == player.position and isinstance(coors[0], Bonus):
                    print(f'|{player.symbol()},B|', end = "")
                elif (i,y) == player.position and isinstance(coors[0], Weapon):
                    print(f'|{player.symbol()},W|', end = "")
                elif (i,y) == player.position and isinstance(coors[0], Tower):
                    print(f'|{player.symbol()},T|', end = "")
                elif (i,y) == player.position and coors[0] == None:
                    print(f'|{player.symbol()}|', end = " ")
                else:
                    if coors[1] == True:
                        if isinstance(coors[0], Enemy):
                            print("|E|", end =' ')
                        elif isinstance(coors[0], Bonus):
                            print("|B|", end =' ')
                        elif isinstance(coors[0], Weapon):
                            print("|W|", end =' ')
                        elif isinstance(coors[0], Tower):
                            print("|T|", end =' ')
                        else:
                            print("| |", end =' ')
                    else:
                        print("|X|",end =' ')
            print("\n")

class Damageable(ABC):
    def __init__(self, hp: float, max_hp: float) -> None:
        self.hp = hp
        self.max_hp = max_hp
        super().__init__()
    
    def is_alive(self) -> bool:
        if self.hp > 0:
            return True
        else:
            return False
    
    def heal(self, amount: float) -> float:
        self.hp = self.hp + amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        return self.hp
    
    def take_damage(self, amount: float) -> float:
        self.hp = self.hp - amount
        return amount


class Attacker(ABC):
    @abstractmethod
    def attack(self, target: Damageable) -> float:
        pass
        
class Player(Entity,Damageable,Attacker):
    def __init__(self,lvl:int,weapon:"Weapon",inventory: dict[str,int], statuses: dict[str,int], rage:float = 1.0, accuracy:float=1.0, fight: bool = False) -> None:
        self.lvl = lvl
        self.weapon = weapon
        self.inventory = inventory
        self.statuses = statuses
        self.rage = rage
        self.accuracy = accuracy
        self.fight = fight
        super().__init__()
        Damageable.__init__(self, Damageable.hp, Damageable.max_hp)
       
        
    
    def move(self,d_row:int, d_col:int) -> None:
        self.position = (d_row, d_col)

    def attack(self, target: Damageable) -> float:
        amount = self.weapon.damage(self.rage)
        return target.take_damage(amount)
    
    def choose_weapon(self,new_weapon: "Weapon") -> None:
        pass

    def apply_status_tick(self) -> float:
        amount = 0
        for key in self.statuses:
            if key == "Infection":
                amount += 5*(1+self.lvl/10)
                key["Infection"] -=1
            if key == "Poison":
                amount += 15*(1+self.lvl/10)
                key["Poison"] -=1

        
        return self.hp.take_damage(amount)
    
    def add_coins(self, amount: int) -> None:
        self.inventory["Coins"] += amount

    def use_bonus(self, bonus: "Bonus") -> None:
        bonus.apply(self)
    
    def buy_auto_if_needed(self, bonus: str) -> "Bonus":
        pass

    def symbol(self) -> str:
        return "P"
    
    def change_fight(self) -> None:
        if self.change_fight == True:
            self.change_fight = False
        else:
            self.change_fight = True




class Bonus(Entity):
    @abstractmethod
    def apply(self, player: 'Player') -> None:
        pass
    
    def symbol(self):
        return "B"


class Weapon(Entity):
    def __init__(self, name:str,max_damage:float) -> None:
        self.name = name
        self.max_damage = max_damage
    
    @abstractmethod
    def roll_damage(self) -> float:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass


class MeleeWeapon(Weapon):
    def is_available(self) -> bool:
        pass

    def roll_damage(self) -> float:
        w_damage = uniform(0, self.max_damage)
        return w_damage
       
    def damage(self,rage: float) -> float:
        if self.roll_damage() * rage <= self.max_damage:
            return self.roll_damage() * rage 
        else:
            return self.max_damage

     
class RangedWeapon(Weapon):
    def is_available(self) -> bool:
        pass

    def __init__(self,ammo:int)-> None:
        self.ammo = ammo
    
    def roll_damage(self) -> float:
        w_damage = uniform(0, self.max_damage)
        return w_damage
    
    def consume_ammo(self, n: int = 1) -> bool:
        if n <= self.ammo:
            return True
        else:
            return False
    
    def damage(self, accuracy: float) -> float:
        if self.consume_ammo() is True: 
            if self.roll_damage() * accuracy <= self.max_damage:
                return accuracy * self.roll_damage()
            else:
                return self.max_damage
        else:
            return "Увы, ваш боезапас пуст!"


class Fist(MeleeWeapon):
    def __init__(self) -> None:
        self.name:str = "Кулак"
        self.max_damage:float = 20
    
    def __str__(self):
        return self.name

    def is_available(self) -> bool:
        pass

    def damage(self,rage: float) -> float:
        if self.roll_damage() * rage <= self.max_damage:
            return self.roll_damage() * rage 
        else:
            return self.max_damage
    
    def symbol():
        pass

class Stick(MeleeWeapon):
    def __init__(self) -> None:
        self.name:str = "Палка"
        self.max_damage:float = 25
        self.durability:int = uniform(10,20)
    
    def __str__(self):
        return self.name
    
    def is_available(self) -> bool:
        if self.durability > 0:
            return True
        else:
            return False
    
    def damage(self,rage: float) -> float:
        if self.roll_damage() * rage <= self.max_damage:
            self.durability = self.durability - 1
            return self.roll_damage() * rage 
        else:
            return self.max_damage
        
    def symbol():
        pass

class Bow(RangedWeapon):
    def __init__(self) -> None:
        self.name:str = "Лук"
        self.max_damage:float = 35
        self.ammo:int = uniform(10,15)
    
    def __str__(self):
        return self.name

    def is_available(self) -> bool:
        if self.ammo > 0:
            return True
        else:
            return False
        
    def damage(self, accuracy: float) -> float:
        if self.consume_ammo() is True: 
            if self.roll_damage() * accuracy <= self.max_damage:
                self.ammo = self.ammo - 1
                return accuracy * self.roll_damage()
            else:
                return self.max_damage
        else:
            return "Увы, ваш боезапас пуст!"
        
    def symbol():
        pass


class Revolver(RangedWeapon):
    def __init__(self) -> None:
        self.name:str = "Револьер"
        self.max_damage:float = 45
        self.ammo:int = uniform(5,10)
    
    def __str__(self):
        return self.name
    
    def is_available(self) -> bool:
        if self.ammo > 0:
            return True
        else:
            return False
    
    def damage(self, accuracy: float) -> float:
        if self.consume_ammo() is True: 
            if self.roll_damage() * accuracy <= self.max_damage:
                self.ammo = self.ammo - 1
                return accuracy * self.roll_damage()
            else:
                return self.max_damage
        else:
            return "Увы, ваш боезапас пуст!"
    
    def symbol():
        pass
        
class Medkit(Bonus):
    def __init__(self):
        self.power = uniform(10,40)
    
    def __str__(self) -> None:
        return "Medkit"
    
    def apply(self, player: 'Player') -> None:
        if player.fight == True:
            player.hell(self.power) 
        else:
            if self.__str__() in player.inventory:
                player.inventory[self.__str__()] += 1
            else:
                player.inventory[self.__str__()] = 1

class Rage(Bonus):
    def __init__(self):
        self.multiplier = uniform(0.1,1.0)
    
    def __str__(self) -> None:
        return "Rage"

    def apply(self, player: 'Player') -> None:
        if player.fight == True:
            old_rage = player.rage #после боя вернуть обратно
            player.rage += self.multiplier
        else:
            if self.__str__() in player.inventory:
                player.inventory[self.__str__()] += 1
            else:
                player.inventory[self.__str__()] = 1


class Arrows(Bonus): # нельзя купить
    def __init__(self):
        self.amount = uniform(1,20)

    def __str__(self) -> None:
        return "Arrows"
    
    def apply(self, player: 'Player') -> None:
        if isinstance(player.weapon,Bow):
            player.inventory["BowAmmo"] += self.amount
        else:
            if self.__str__() in player.inventory:
                player.inventory[self.__str__()] += 1
            else:
                player.inventory[self.__str__()] = 1

class Bullets(Bonus):
    def __init__(self) -> None:
        self.amount = uniform(1,10)

    def __str__(self) -> None:
        return "Bullets"
    
    def apply(self, player: 'Player') -> None:
        if isinstance(player.weapon,Revolver):
            player.inventory["RevAmmo"] += self.amount
        else:
            if  self.__str__() in player.inventory:
                player.inventory[self.__str__()] += 1
            else:
                player.inventory[self.__str__()] = 1

class Accuracy(Bonus):
    def __init__(self):
        self.multiplier = uniform(0.1,1.0)
        self.price:int = 50

    def __str__(self) -> None:
        return "Accuracy"

    def apply(self, player: 'Player') -> None:
        if player.fight == True:
            player.accuracy += self.multiplier
        #после боя вернуть обратно 
        else:
            if  self.__str__()  in player.inventory:
                player.inventory[self.__str__()] += 1
            else:
                player.inventory[self.__str__()] = 1


class Coins(Bonus):
    def __init__(self):
        self.amount = randint(50,100)
    
    def __str__(self) -> None:
        return "Coins"

    def apply(self, player: 'Player') -> None:
        if  self.__str__()  in player.inventory:
            player.inventory[self.__str__()] += self.amount
        else:
             player.inventory[self.__str__()] = self.amount


class Structure(Entity):
    @abstractmethod
    def interact(self, player: 'Player') -> None:
        pass

class Tower(Structure):
    def __init__(self):
        self.reveal_radius: int = 2
        super().__init__()
    def interact(self, board: "Board") -> None:
        circle_i = (self.position[0] - self.reveal_radius, self.position[0] + self.reveal_radius)
        circle_y = (self.position[1] -  self.reveal_radius, self.position[1] +  self.reveal_radius)
        
        for i in range(circle_i[0], circle_i[1]+1):
            for y in range(circle_y[0], circle_y[1]+1):
                if i>= 0 and y>=0 and i<= board.goal[0] and y<= board.goal[1]:
                    place = board.grid[i][y]
                    place[1] = True
    
    def symbol():
        pass


class Enemy(Entity, Damageable, Attacker):
    def __init__( self, lvl:int, max_enemy_damage:float,reward_coins: int)-> None:
        self.lvl = lvl
        self.max_enemy_damage = max_enemy_damage
        self.reward_coins = reward_coins

    @abstractmethod
    def before_turn(self, player: 'Player') -> None:
        pass
    def roll_enemy_damage(self) -> float:
        return uniform(0,self.max_enemy_damage)
    
    def symbol(self) -> str:
        return "E"
    

class Rat(Enemy):
    def __init__(self):
        self.lvl = randint(1,10)
        self.max_damage = 15 * (1 + self.lvl / 10)
        self.infection_chance: float = 0.25
        self.flee_chance_low_hp: float = 0.10
        self.flee_threshold: float = 0.15 #доля HP, при которой возможен побег.
        self.infection_damage_base: float = 5.0
        self.infection_turns: int = 3
        self.reward_coins: int = 200

    def __str__(self):
        return "Rat"
    
    def before_turn(self, player: "Player") -> None:
            if self.hp == self.flee_threshold * 100 * (1 + self.lvl / 10):
                a = randint(1,int(1/self.flee_chance_low_hp))
                if a==1:
                    #крыса убегает
                    player.add_coins(self.reward_coins)
                else:
                    pass
            b = randint(1,int(1/self.infection_chance))
            if b == 1:
                if "Infection" in player.statuses:
                    player.statuses["Infection"] += self.infection_turns
                else: 
                    player.statuses["Infection"] = self.infection_turns
                player.apply_status_tick()

    def attack(self, target: Damageable) -> float:
        amount = uniform(0, 15 * (1 + self.lvl / 10))
        target.take_damage(amount)
        return amount
    
    def symbol(self) -> str:
        pass
    
class Spider(Enemy):
    def __init__(self):
        self.lvl = randint(1,10)
        self.max_damage = 20 * (1 + self.lvl / 10)
        self.poison_chance: float = 0.10
        self.summon_chance_low_hp: float = 0.10
        self.poison_damage_base: float = 15.0
        self.poison_turns: int = 2
        self.reward_coins: int = 250
    
    def __str__(self):
        return "Spider"

    def before_turn(self, player: "Player") -> None:
        if self.hp == 0.15 * 100 * (1 + self.lvl / 10):
                a = randint(1,int(1/self.summon_chance_low_hp))
                if a==1:
                    return Spider(randint(1,10),20 * (1 + Spider.lvl / 10),250)
                else:
                    pass
        b = randint(1,int(1/self.poison_chance * (1 + self.lvl / 10)))
        if b == 1:
            if "Poison" in player.statuses:
                player.statuses["Poison"] += self.poison_turns
            else: 
                player.statuses["Poison"] = self.poison_turns
            player.apply_status_tick()

    def attack(self, target: Damageable) -> float:
        target.take_damage(uniform(0,20 * (1 + self.lvl / 10)))
        return uniform(0,20 * (1 + self.lvl / 10))
    
    def symbol(self) -> str:
        pass

class Skeleton(Enemy):
    def __init__(self,weapon:Weapon):
        self.reward_coins: int = 150
        self.lvl = randint(1,10)
        self.max_damage = 10 * (1 + self.lvl / 10)
    
    def __str__(self):
        return "Skeleton"
    
    def before_turn(self, player: "Player") -> None:
        pass

    def attack(self, target: Damageable) -> float:
            target.damage(self.weapon.damage())
            return self.weapon.damage()
  
    def drop_loot(self, player: "Player") -> Weapon | None:
        if isinstance(self.weapon, Fist):
            pass
        else:
            #опустить оружие
            pass

    def symbol(self) -> str:
        pass

def start(n:int, m:int, player_lvl:int)-> tuple["Board","Player"]:
    fist = Fist()
    desk = []
    for i in range(n):
        lst = []
        for y in range(m):
            lst.append(0)
        desk.append(lst)
    weapons = [Revolver(),Stick(),Bow()]
    bonuses = [Medkit(),Arrows(),Rage(),Bullets(),Accuracy(),Coins()]
    enemies = [Skeleton(choice(weapons)),Rat(), Spider()]
    p_tower = 0.01
    p_weapon = 0.05
    p_enemy = 0.15
    p_bonus = 0.3
    for i in range(n):
        for y in range(m):
            if i == 0 and y == 0:
                desk[i][y] = [None,True]
            elif i==n-1 and y==m-1:
                desk[i][y] = [None,True]
            else:
                tow = [0 if k > int(n*m*p_tower) else 1 for k in range(n*m)]
                rand_tow = choice(tow)
                if rand_tow == 1:
                    desk[i][y] = [Tower(),False]
                else:
                    bon = [0 if k > int(n*m*p_bonus) else 1 for k in range(n*m)]
                    rand_bon = choice(bon)
                    if rand_bon == 1:
                        desk[i][y] = [choice(bonuses), False]
                       
                    else:
                        ene = [0 if k > int(n*m*p_enemy) else 1 for k in range(n*m)]
                        rand_ene = choice(ene)
                        if rand_ene == 1:
                            desk[i][y] = [choice(enemies), False]
                            
                        else:
                            wea = [0 if k > int(n*m*p_weapon) else 1 for k in range(n*m)]
                            rand_wea = choice(wea)
                            if rand_wea == 1:
                                desk[i][y] = [choice(weapons), False]
                                
                            else:
                                desk[i][y] = [None,False]

   
    return Board(n,m,desk,(0,0),(n-1,m-1)), Player(player_lvl, fist, {}, {})

def game(board: Board, player: Player) -> None:
    print('Добро пожаловать в игру "Сдохни или умри!"\n Команды:\n w - вперед \n a - налево \n d - направо \n s - назад \n f - атака \n i - Посмотреть инвентарь')
    i=player.position[0]
    y=player.position[1]
    coors = board.grid[i][y]
      
    while player.position[0] != board.goal[0] or  player.position[1] != board.goal[1] :

        command = input()

        if command == "i":
            for key in player.inventory:
                print(f"{key} - {player.inventory[key]}")
      
        if command == "w":
            if board.in_bounds((i+1,y)):
                player.move(i+1,y)
                print("Вы пошли вперед!")
                coors[1] = True
                board.render(player)
            else:
                 print("не удалось пойти")
            
        
        elif command == "a":
            if board.in_bounds((i,y+1)):
                player.move(i,y+1)
                print("Вы пошли налево!")
                coors[1] = True
                board.render(player)
            else:
                print("не удалось пойти")
            

        elif command == "d":
            if board.in_bounds((i,y-1)) and y>0:
                player.move(i,y-1)
                print("Вы пошли направо!")
                coors[1] = True
                board.render(player)
            else:
                print("не удалось пойти")

        elif command == "s":
            if board.in_bounds((i-1,y)) and i>0:
                player.move(i-1,y)
                print("Вы пошли назад!")
                coors[1] = True
                board.render(player)
            else:
                print("не удалось пойти")
        
        i=player.position[0]
        y=player.position[1]
        coors = board.grid[i][y]

            
        if isinstance(coors[0], Tower):
            print("\033[1;33m Tower!\033[0m \n")
            coors[0].position = (i,y)
            coors[0].interact(board)
            board.render(player)
            print("Открыты новые поля!\n")
           
        
        if isinstance(coors[0], Bonus):
            print(f"\033[1;32m {coors[0]}!\033[0m\n")
            coors[0].apply(player)
        
        if isinstance(coors[0], Enemy):
            print(f"\033[1;31m{coors[0]}!\033[0m\n")
            player.fight = True
            while player.is_alive() and coors[0].is_alive():
                command = input()
                print(f"\033[1;31m {coors[0].before_turn(player)}!\033[0m\n")
                print(f"\033[1;31m {coors[0].attack(player)}!\033[0m\n")
                if command == 'f':
                    print(f"{player.attack(coors[0])}\n")
                # if command == "b":
                #     n = 1
                #     for key in player.inventory:
                #        print(f" {n}- {key} - {player.inventory[key]}", end = "")
                #        print("Введите номер бонуса")
                #        n+=1
                #     n = 1
                #     m = int(input())
                #     if m <= len(player.inventory):
                #         for key in player.inventory:
                #             if n!=m:
                #                 pass
                #             else:
                #                 player.inventory.apply(player)
                #             n+=1

if __name__ == "__main__":
    print(start(10,5,6))
    game(start(10,5,randint(1,10))[0], start(10,5,randint(1,10))[1])
