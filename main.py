import sys
import os
import random
import time
import msvcrt

sys.stdout.reconfigure(encoding='utf-8')
os.system('')

# Управление консолью
CSI = '\x1b['
def clear_screen():
    sys.stdout.write(CSI + '2J' + CSI + 'H')

def hide_cursor():
    sys.stdout.write(CSI + '?25l')

def show_cursor():
    sys.stdout.write(CSI + '?25h')

def move_to(row, col):
    sys.stdout.write(f"{CSI}{row};{col}H")

def get_terminal_size():
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24

# Описание звёздочек
class Stars:
    def __init__(self, width, height):
        self.x = random.randint(1, width)
        self.y = random.randint(1, height)
        self.speed = random.choice([1, 1, 2, 2, 3])

        self.prev_x = None
        self.prev_y = None
        self.real_y = float(self.y)
        self.drawn = False

    def reset_top(self, width):
        self.x = random.randint(1, width)
        self.real_y = 1.0
        self.y = 1
        self.speed = random.choice([1, 1, 2, 2, 3])
        self.prev_x = None
        self.prev_y = None
        self.drawn = False

class FallingStars:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.play_height = height - 1
        self.stars = [Stars(self.width, self.play_height) for _ in range(100)]
        self.paused = False
        self.speed_mult = 1.0

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.play_height = height - 1
        for s in self.stars:
            if s.x > self.width:
                s.x = self.width
            if s.y > self.play_height:
                s.y = self.play_height
                s.real_y = float(s.y)
            s.drawn = False
            s.prev_x = None

    def erase_all(self):
        for s in self.stars:
            if s.drawn and s.prev_x is not None:
                move_to(s.prev_y, s.prev_x)
                sys.stdout.write(' ')

    def update_and_draw(self):
        self.erase_all()

        for s in self.stars:
            if not self.paused:
                s.real_y += s.speed * self.speed_mult
                s.y = int(s.real_y)

                if s.y > self.play_height:
                    s.reset_top(self.width)

            s.prev_x = s.x
            s.prev_y = max(1, s.y)

            move_to(s.prev_y, s.prev_x)
            sys.stdout.write('*')
            s.drawn = True

    def draw_status(self):
        state = 'Пауза' if self.paused else 'Звёздочки'
        msg = f"[{state}] Скорость: x{self.speed_mult:.1f} | Количество звезд: {len(self.stars)} | Space=пауза, +/-=скорость, q=выход"

        move_to(self.height, 1)
        msg = msg.ljust(self.width)[:self.width]
        sys.stdout.write(msg)

def main():
    hide_cursor()
    clear_screen()

    width, height = get_terminal_size()
    if width < 30 or height < 5:
        show_cursor()
        print("Ошибка: Терминал слишком мал для запуска.")
        return

    game = FallingStars(width, height)
    frame_time = 0.06

    try:
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('\x00', '\xe0'):
                    msvcrt.getwch()
                else:
                    if ch in ('q', 'Q', 'й', 'Й'):
                        break
                    elif ch == ' ':
                        game.paused = not game.paused
                    elif ch in ('+', '='):
                        game.speed_mult = min(game.speed_mult + 0.25, 10.0)
                    elif ch == '-':
                        game.speed_mult = max(game.speed_mult - 0.25, 0.25)

            nw, nh = get_terminal_size()
            if nw != width or nh != height:
                width, height = nw, nh
                if width >= 30 and height >= 5:
                    clear_screen()
                    game.resize(width, height)

            game.update_and_draw()
            game.draw_status()
            sys.stdout.flush()

            time.sleep(frame_time)

    except KeyboardInterrupt:
        pass
    finally:
        clear_screen()
        show_cursor()
        sys.stdout.flush()
        print("Программа успешно завершена.")


if __name__ == '__main__':
    main()