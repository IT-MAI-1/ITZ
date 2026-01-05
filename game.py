import random
import os
from typing import List, Dict
from battle import Player, battle, Boss

# Список доступных артефактов в игре
ARTIFACTS = [
    '🗡️ Меч Пламени',
    '🛡️ Щит Бури',
    '🌑 Посох Теней',
    '💍 Кольцо Света',
    '👑 Корона Мудрости',
    '🏹 Лук Соколиного Глаза',
    '🧭 Компас Судьбы',
    '🔮 Хрустальный Шар Провидца',
    '🧿 Амулет Забвения',
    '🕶️ Плащ Невидимости'
]

# Функция авторизации пользователя
# Загружает данные из файла users.txt и проверяет логин/пароль
def login() -> str:
    users = {}
    with open('ИТЗ/users.txt', 'r', encoding='utf-8') as f:
        for line in f:
            login, password = line.strip().split(':')
            users[login] = password
    
    while True:
        login_input = input('Введите логин: ')
        password_input = input('Введите пароль: ')
        if login_input in users and users[login_input] == password_input:
            return login_input
        print('Неверный логин или пароль.')

# Загрузка копилки артефактов пользователя из файла {login}.txt
def load_kopilka(login: str) -> List[str]:
    filename = f'ИТЗ/{login}.txt'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f]
    return []

# Сохранение копилки артефактов в файл {login}.txt
def save_kopilka(login: str, artifacts: List[str]):
    with open(f'ИТЗ/{login}.txt', 'w', encoding='utf-8') as f:
        for art in artifacts:
            f.write(art + '\n')

# Выбор стартового артефакта (нельзя выбрать уже собранный)
def choose_start_artifact(kopilka: List[str]) -> str:
    available = [a for a in ARTIFACTS if a not in kopilka]
    if not available:
        available = ARTIFACTS
    print('Выберите стартовый артефакт:')
    for i, art in enumerate(available, 1):
        print(f'{i}. {art}')
    while True:
        try:
            choice = int(input('Введите номер: ')) - 1
            if 0 <= choice < len(available):
                return available[choice]
        except ValueError:
            pass
        print('Неверный выбор.')

# Мини-игра: камень-ножницы-бумага со скелетом
def rock_paper_scissors() -> bool:
    choices = ['камень', 'ножницы', 'бумага']
    print('💀 Игра со скелетом. Победите — получите артефакт, проиграете — он заберет ваш.')
    while True:
        player = input('Ваш выбор (камень/ножницы/бумага): ').lower()
        if player in choices:
            break
        print('Неверный выбор.')
    skeleton = random.choice(choices)
    print(f'Скелет выбрал: {skeleton}')
    if (player == 'камень' and skeleton == 'ножницы') or \
       (player == 'ножницы' and skeleton == 'бумага') or \
       (player == 'бумага' and skeleton == 'камень'):
        print('🎉 Вы победили скелета!')
        return True
    elif player == skeleton:
        print('Ничья! Играем снова.')
        return rock_paper_scissors()
    else:
        print('💀 Скелет победил!')
        return False

# Мини-игра: виселица с лешим
def hangman() -> bool:
    words = ['лес', 'пещера', 'болото', 'леший', 'артефакт', 'скелет']
    word = random.choice(words)
    guessed = set()
    attempts = 6
    display = ['_'] * len(word)
    print('Игра виселица с лешим.')
    while attempts > 0 and '_' in display:
        print(' '.join(display))
        letter = input('Введите букву: ').lower()
        if letter in guessed:
            print('Уже угадывали.')
            continue
        guessed.add(letter)
        if letter in word:
            for i, l in enumerate(word):
                if l == letter:
                    display[i] = letter
        else:
            attempts -= 1
            print(f'Неверно. Осталось попыток: {attempts}')
    if '_' not in display:
        print('Вы победили!')
        return True
    print('Вы проиграли.')
    return False

# Потеря случайного артефакта при проигрыше
def lose_random_artifact(kopilka: List[str]) -> None:
    if kopilka:
        lost = random.choice(kopilka)
        kopilka.remove(lost)
        print(f"💀 Вы потеряли артефакт: {lost}!")
    else:
        print("💀 У вас нет артефактов для потери.")

# Выбор артефакта после победы в мини-игре или битве
def choose_artifact(current: str, kopilka: List[str], login_user: str) -> str:
    available = [a for a in ARTIFACTS if a not in kopilka and a != current]
    if not available:
        print('Вы собрали все артефакты! Копилка очищена. Начните играть заново, чтобы собрать все артефакты!')
        kopilka.clear()
        save_kopilka(login_user, kopilka)
        available = [a for a in ARTIFACTS if a != current]
    print('Выберите артефакт:')
    for i, art in enumerate(available, 1):
        print(f'{i}. {art}')
    while True:
        try:
            choice = int(input('Введите номер: ')) - 1
            if 0 <= choice < len(available):
                return available[choice]
        except ValueError:
            pass
        print('Неверный выбор.')

# Основная функция игры
def main():
    # Авторизация пользователя
    login_user = login()
    # Загрузка ранее собранных артефактов
    kopilka = load_kopilka(login_user)
    # Выбор стартового артефакта
    current_artifact = choose_start_artifact(kopilka)
    kopilka.append(current_artifact)
    save_kopilka(login_user, kopilka)
    print(f'💎 Вы получаете артефакт: {current_artifact}')
    # Список посещенных локаций
    locations = []
    # Основной игровой цикл
    while True:
        print('🌲Вы стоите на перекрестке в лесу. Куда вы пойдете?🌲')
        direction = input('Введите \'налево\', \'направо\' или \'прямо\': ').lower()
        if direction == 'налево':
            # Мини-игра со скелетом
            print('Вы идете налево и встречаете скелета в пещере.')
            if rock_paper_scissors():
                new_art = choose_artifact(current_artifact, kopilka, login_user)
                kopilka.append(new_art)
                print(f'Вы получили артефакт: {new_art}')
            else:
                lose_random_artifact(kopilka)
            locations.append('Пещера со скелетом')
        elif direction == 'направо':
            # Мини-игра с лешим
            print('Вы идете направо и встречаете лешего в болоте.')
            if hangman():
                new_art = choose_artifact(current_artifact, kopilka, login_user)
                kopilka.append(new_art)
                print(f'Вы получили артефакт: {new_art}')
            else:
                lose_random_artifact(kopilka)
            locations.append('Болото с лешим')
        elif direction == 'прямо':
            # Битва с боссом
            print('Вы идете прямо и встречаете босса леса!')
            player = Player("Игрок", hp=40, mp=20, strength=6, intelligence=5)
            boss = Boss("Босс леса")
            if battle(player, boss):
                new_art = choose_artifact(current_artifact, kopilka, login_user)
                kopilka.append(new_art)
                print(f'Вы получили артефакт: {new_art}')
            else:
                lose_random_artifact(kopilka)
            locations.append('Босс леса')
        else:
            print('Неверный выбор.')
            continue

        # Концовка
        print('Ход завершен.')
        print(f'🌿 Посещенные локации: {", ".join(locations)}')
        print(f'🎁 Собранные артефакты: {", ".join(kopilka)}')
        save_choice = input('Сохранить прогресс? (да/нет): ').lower()
        if save_choice == 'да':
            save_kopilka(login_user, kopilka)
        else:
            # Копилка остается пустой до следующей игры
            pass
        again = input('Продолжить игру? (да/нет): ').lower()
        if again != 'да':
            break

if __name__ == '__main__':
    main()