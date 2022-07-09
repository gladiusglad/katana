import mmap
import random
import curses
import threading
from generatewords import generate

def read_words():
    with open("./words.txt", "r", encoding="utf-8") as file:
        return mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)

def get_answer(words):
    answer_pos = random.randrange(0, 31400, 5)
    words.seek(answer_pos)
    answer = words.read(5).decode("utf-8")
    words.seek(0)
    return answer

def is_in_word_list(words, word):
    return words.find(str.encode(word, "utf-8")) != -1

def addstr_center(window, ypos, text, attr):
    window_x = window.getmaxyx()[1]
    xpos = window_x // 2 - (len(text) - 1) // 2
    window.addstr(ypos, xpos, text, attr)
    return xpos

def clear_line(window, ypos):
    window.addstr(ypos, 0, " " * window.getmaxyx()[1], curses.color_pair(1))

def popup(window, ypos, text, attr=None):
    if attr is None:
        attr = curses.color_pair(5)
    addstr_center(window, ypos, text, attr)
    threading.Timer(3, lambda: clear_line(window, ypos)).start()

def move_cursor(window, prev_xpos, ypos, xpos):
    if prev_xpos >= xpos:
        window.chgat(ypos, prev_xpos, 1, curses.color_pair(4))
    window.chgat(ypos, xpos, 1, curses.color_pair(7))

def katana_curses(stdscr):
    words = read_words()
    answer = get_answer(words)

    curses.use_default_colors()
    curses.curs_set(0)

    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, 8, -1)
    curses.init_pair(4, 250, -1)
    curses.init_pair(5, curses.COLOR_RED, -1)
    curses.init_pair(6, curses.COLOR_YELLOW, -1)
    curses.init_pair(7, 51, -1)

    stdscr.bkgd(" ", curses.color_pair(1))

    addstr_center(stdscr, 2, "KATANA", curses.color_pair(7))

    tries = 7
    min_ypos = 4
    max_ypos = min_ypos + tries - 1
    min_xpos = addstr_center(stdscr, min_ypos, "_____", curses.color_pair(4))
    max_xpos = min_xpos + 5
    for blanks_ypos in range(min_ypos + 1, max_ypos + 1):
        addstr_center(stdscr, blanks_ypos, "_____", curses.color_pair(3))

    stdscr.move(min_ypos, min_xpos)
    move_cursor(stdscr, min_xpos, min_ypos, min_xpos)
    stdscr.refresh()

    restart = False
    game_over = False
    cursor_ypos = min_ypos
    cursor_xpos = min_xpos
    while True:
        prev_xpos = cursor_xpos
        char = stdscr.getch()
        if char == 32:
            restart = True
            break
        if game_over:
            break
        if (64 < char < 91 or 96 < char < 123) and cursor_xpos != max_xpos:
            cap_char = char if 64 < char < 91 else char - 32
            stdscr.addstr(cursor_ypos, cursor_xpos, chr(cap_char), curses.color_pair(1))
            cursor_xpos += 1
        if char == curses.KEY_BACKSPACE and cursor_xpos != min_xpos:
            cursor_xpos -= 1
            stdscr.addstr(cursor_ypos, cursor_xpos, "_", curses.color_pair(4))
        if char == 10:
            if cursor_xpos != max_xpos:
                popup(stdscr, max_ypos + 2, "Kata harus 5 huruf.")
            else:
                guess = stdscr.instr(cursor_ypos, min_xpos, 5).decode("utf-8").lower()
                if not is_in_word_list(words, guess):
                    popup(stdscr, max_ypos + 2, "Kata tidak ditemukan di KBBI.")
                elif guess == answer:
                    stdscr.chgat(cursor_ypos, min_xpos, 5, curses.color_pair(2))
                    popup(stdscr, max_ypos + 2, "Luar biasa!", curses.color_pair(2))
                    game_over = True
                else:
                    for (letter_index, letter) in enumerate(guess):
                        if letter == answer[letter_index]:
                            stdscr.chgat(cursor_ypos, min_xpos + letter_index, 1,
                                    curses.color_pair(2))
                        elif letter in answer:
                            stdscr.chgat(cursor_ypos, min_xpos + letter_index, 1,
                                    curses.color_pair(6))
                        else:
                            stdscr.chgat(cursor_ypos, min_xpos + letter_index, 1,
                                    curses.color_pair(4))
                    cursor_ypos += 1
                    if cursor_ypos > max_ypos:
                        popup(stdscr, max_ypos + 2, "Sayang sekali...")
                        popup(stdscr, max_ypos + 3, "Tekan spasi untuk mengulang.")
                        game_over = True
                    cursor_xpos = min_xpos
                    stdscr.chgat(cursor_ypos, min_xpos, 5, curses.color_pair(4))

        stdscr.move(cursor_ypos, cursor_xpos)
        move_cursor(stdscr, prev_xpos, cursor_ypos, cursor_xpos)
        stdscr.refresh()

    curses.endwin()
    if restart:
        start_curses()

def start_curses():
    curses.wrapper(katana_curses)

if __name__ == "__main__":
    generate()
    start_curses()
