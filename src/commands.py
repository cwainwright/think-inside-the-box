from typing import Literal


class StartGame:
    """An instance of this is passed into the first game section that is run at the start of the game"""
    pass


class ChangeSection:
    """Return an instance of this class to make the manager change game section.

    The new section can be 'over_world', 'question' or 'menu', and a section can move to itself (e.g. 'menu' to 'menu').
    The class passes the data parameter to the next section, so you can pass information between sections.
    """
    def __init__(
            self,
            new_section: Literal['over_world', 'question', 'menu'],
            data,
    ):
        self.new_section = new_section
        self.data = data


class EndGame:
    """An instance of this should only be returned by a game section if that section should be stopped"""
    pass
