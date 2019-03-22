from enum import Enum
from colorama import Fore, Back, Style, init

init(autoreset=True)

class Palette(Enum):
    ROBBER = (Fore.GREEN, Back.WHITE, Style.BRIGHT)
    ROAD = (Fore.MAGENTA, Back.WHITE)
    WATER = (Fore.BLUE, Back.WHITE)

class Dark(Palette):
    ROBBER = (Fore.GREEN, Back.WHITE)
    ROAD = (Fore.MAGENTA, Back.WHITE)
    WATER = (Fore.BLUE, Back.WHITE)
