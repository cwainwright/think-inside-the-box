import threading
from queue import Queue

from blessed import Terminal

from src.manager import GameManager

FPS = 60


def main():
    term = Terminal()
    input_queue = Queue()
    manager = GameManager(input_queue, term)
    manager_thread = threading.Thread(target=manager)
    manager_thread.start()

    with term.raw(), term.hidden_cursor(), term.location(), term.fullscreen():
        while manager_thread.is_alive():
            inp = term.inkey(1 / FPS)
            if inp != '':
                input_queue.put(inp)
        print(term.normal + term.clear)


if __name__ == '__main__':
    main()
