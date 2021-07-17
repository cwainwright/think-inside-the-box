from argparse import ArgumentParser

from src.dummy_manager import (
    DummyGameOverManager, DummyMenuManager, DummyOverWorldManager,
    DummyQuestionManager
)
from src.game import Game
from src.manager import GameManager


def main() -> None:
    """Run the game"""
    parser = ArgumentParser()
    parser.set_defaults(manager=GameManager)

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--menu', dest='manager', action='store_const', const=DummyMenuManager)
    group.add_argument('--over_world', dest='manager', action='store_const', const=DummyOverWorldManager)
    group.add_argument('--question', dest='manager', action='store_const', const=DummyQuestionManager)
    group.add_argument('--game_over', dest='manager', action='store_const', const=DummyGameOverManager)

    args = parser.parse_args()

    game = Game(args.manager)
    game.run()


if __name__ == '__main__':
    main()
