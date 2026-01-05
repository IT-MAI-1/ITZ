from typing import List, Callable

# Класс эффекта
class Effect:
    def __init__(self, name:str, duration:int, dot=0):
        self.name=name
        self.duration=duration
        self.dot=dot

    # Действие эффекта в начале хода 
    def on_turn_start(self, target:'Human'):
        if self.dot>0:
            target.take_damage(self.dot, source="DoT")
        self.duration-=1

    # Модификация входящего урона
    def modify_incoming(self, amount:int)->int:
        return amount

    # Проверка, истек ли эффект
    @property
    def expired(self)->bool:
        return self.duration<=0 and self.dot<=0

# Класс предмета с эффектом
class Item:
    def __init__(self, name:str, effect:Callable[['Human','Human'],None]):
        self.name=name
        self.effect=effect

    # Использование предмета 
    def use(self, user:'Human', target:'Human')->None:
        self.effect(user, target)

# Инвентарь персонажа
class Inventory:
    def __init__(self):
        self.items: List[Item]=[]

    # Добавление предмета в инвентарь
    def add(self, item:Item)->None:
        self.items.append(item)

    # Использование предмета по имени
    def use(self, name:str, user:'Human', target:'Human')->bool:
        for i, it in enumerate(self.items):
            if it.name==name:
                it.use(user, target)
                self.items.pop(i)
                return True
        return False

# Класс персонажа
class Human:
    def __init__(self, name:str, hp:int, mp:int, strength:int, intelligence:int):
        self.name=name
        self.max_hp=hp
        self.max_mp=mp
        self._hp=hp
        self._mp=mp
        self._strength=strength
        self._intelligence=intelligence
        self.effects: List[Effect]=[] 
        self.inventory=Inventory()  

    # Текущее здоровье
    @property
    def hp(self)->int:
        return self._hp

    @hp.setter
    def hp(self, value:int)->None:
        self._hp=max(0, min(self.max_hp, int(value)))

    # Текущая мана
    @property
    def mp(self)->int:
        return self._mp

    @mp.setter
    def mp(self, value:int)->None:
        self._mp=max(0, min(self.max_mp, int(value)))

    # Проверка жив ли персонаж
    @property
    def is_alive(self)->bool:
        return self.hp>0

    # Сила
    @property
    def strength(self)->int:
        return self._strength

    # Интеллект
    @property
    def intelligence(self)->int:
        return self._intelligence

    # Добавление эффекта
    def add_effect(self, effect:Effect)->None:
        self.effects.append(effect)
        print(f"{self.name} получает эффект {effect.name} на {effect.duration} ходов.")

    # Очистка истекших эффектов
    def clean_effects(self)->None:
        self.effects=[e for e in self.effects if not e.expired]

    # Начало хода: применение эффектов
    def start_turn(self)->None:
        for e in list(self.effects):
            e.on_turn_start(self)
        self.clean_effects()

    # Получение урона
    def take_damage(self, amount:int, source:str="удар")->None:
        modified=amount
        for e in self.effects:
            modified=e.modify_incoming(modified)
        self.hp=self.hp - modified
        print(f"{self.name} получает {modified} урона ({source}). HP: {self.hp}/{self.max_hp}")

    # Исцеление
    def heal(self, amount:int)->None:
        old=self.hp
        self.hp=self.hp+amount
        print(f"{self.name} исцелен на {self.hp-old}. HP: {self.hp}/{self.max_hp}")

    # Трата маны
    def spend_mana(self, cost:int)->bool:
        if self.mp>=cost:
            self.mp=self.mp-cost
            return True
        print(f"{self.name} не хватает MP!")
        return False

    # Обычная атака
    def attack(self, target:'Human')->None:
        dmg=max(1, self.strength)
        print(f"{self.name} бьёт обычной атакой по {target.name}.")
        target.take_damage(dmg, source="атака")

# Абстрактная стратегия поведения босса
class Strategy:
    def act(self, boss:'Boss', party:List[Human])->None:
        raise NotImplementedError

# Стратегия первой фазы босса (при высоком здоровье)
class Phase1Strategy(Strategy):
    def act(self, boss:'Boss', party:List[Human])->None:
        player = party[0]  
        if boss.mp>=6:
            boss.mp-=6
            print(f"{boss.name} выпускает 'Тёмный выстрел' в {player.name}.")
            player.take_damage(boss.intelligence+3, source="Тёмный выстрел")
        else:
            boss.attack(player)

# Стратегия второй фазы босса (при низком здоровье)
class Phase2Strategy(Strategy):
    def act(self, boss:'Boss', party:List[Human])->None:
        player = party[0]
        if boss.mp>=8:
            boss.mp-=8
            print(f"{boss.name} рычит и обрушивает 'Теневую волну' на игрока.")
            if player.is_alive:
                player.take_damage(3+boss.intelligence//2, source="Теневая волна")
                player.add_effect(Effect("Страх", duration=2))
        else:
            boss.attack(player)

# Класс босса
class Boss(Human):
    def __init__(self, name:str):
        super().__init__(name, hp=70, mp=25, strength=6, intelligence=6)
        self.strategy: Strategy=Phase1Strategy()

    # Обновление стратегии в зависимости от здоровья
    def update_strategy(self)->None:
        if self.hp <= self.max_hp//2:
            self.strategy=Phase2Strategy()

    # Атака босса
    def attack(self, target:'Human')->None:
        dmg=self.strength+3
        print(f"{self.name} (Босс) сокрушает {target.name}.")
        target.take_damage(dmg, source="кулак")

    # Ход босса
    def take_turn(self, party:List[Human])->None:
        self.update_strategy()
        self.start_turn()
        self.strategy.act(self, party)

# Класс игрока
class Player(Human):
    def __init__(self, name, hp, mp, strength, intelligence):
        super().__init__(name, hp, mp, strength, intelligence)
        # Добавляем предметы в инвентарь
        self.inventory.add(Item("Зелье", lambda u, t: t.heal(12)))
        self.inventory.add(Item("Эфир", lambda u, t: setattr(t, 'mp', t.mp + 8)))

    # Способность: мощный удар
    def power_strike(self, target):
        cost = 5
        if self.spend_mana(cost):
            dmg = self.strength * 2
            print(f"{self.name} использует 'Мощный удар' по {target.name}.")
            target.take_damage(dmg, source="Мощный удар")

    # Способность: огненный шар
    def fireball(self, target):
        cost = 7
        if self.spend_mana(cost):
            dmg = self.intelligence * 2 + 2
            print(f"{self.name} кидает 'Огненный шар' в {target.name}.")
            target.take_damage(dmg, source="Огненный шар")
            target.add_effect(Effect("Горение", duration=2, dot=2))

    # Способность: лечение
    def heal_ally(self, ally):
        cost = 6
        if self.spend_mana(cost):
            amount = self.intelligence * 2 + 4
            print(f"{self.name} лечит {ally.name}.")
            ally.heal(amount)

# Функция битвы между игроком и боссом
def battle(player, boss):
    round_no = 1
    # Основной цикл битвы
    while player.is_alive and boss.is_alive:
        print(f"\n--- Раунд {round_no} ---")
        player.start_turn()  # Применение эффектов игрока
        print("Выберите действие:")
        print("1. Обычная атака")
        print("2. Мощный удар (5 MP)")
        print("3. Огненный шар (7 MP)")
        print("4. Лечение (6 MP)")
        print("5. Использовать предмет")
        choice = input("Введите номер: ")
        if choice == '1':
            player.attack(boss)
        elif choice == '2':
            player.power_strike(boss)
        elif choice == '3':
            player.fireball(boss)
        elif choice == '4':
            player.heal_ally(player)  
        elif choice == '5':
            # Использование предмета
            items = [it.name for it in player.inventory.items]
            if not items:
                print("Инвентарь пуст.")
                continue
            print("Предметы:", items)
            item_choice = input("Введите название предмета: ")
            if player.inventory.use(item_choice, player, player):
                print(f"Использован {item_choice}.")
            else:
                print("Предмет не найден.")
        else:
            print("Неверный выбор.")
            continue
        if not boss.is_alive:
            break
        boss.start_turn()  # Применение эффектов босса
        boss.take_turn([player])  # Ход босса
        round_no += 1
        if round_no > 20:  # Ограничение на количество раундов
            break
    # Конец боя
    if boss.hp <= 0:
        print("Победа!")
        return True
    else:
        print("Поражение...")
        return False