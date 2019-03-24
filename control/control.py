
GAME_CONTROLS = [
    #"dice",
    "end",
    "undo",
    #"buy dc",
    #"knight",
    #"monopoly",
    #"build roads",
    #"plenty",
    #"help"
]


def sort_them(controllers, letter):
    current_list = [s for s in controllers]
    return [str(letter + str(s)) for s in sorted(current_list, key=int)]


def get_roads_controllers(board_map):
    roads = []
    roads.extend(sort_them(board_map["roads_and_settlements"], "r"))
    return roads


def get_setts_controllers(board_map):
    setts = []
    setts.extend(sort_them(board_map["neighbor_settlements"], "s"))
    return setts


def get_tiles_controllers(board_map):
    tiles = []
    tiles.extend(sort_them(board_map["tiles_and_settlements"], "t"))
    return tiles


# Controllers representation
def get_all_controllers(board_map):
    list_of_controllers = []
    list_of_controllers.extend(sort_them(board_map["roads_and_settlements"], "r"))
    list_of_controllers.extend(sort_them(board_map["neighbor_settlements"], "s"))
    list_of_controllers.extend(sort_them(board_map["tiles_and_settlements"], "t"))
    list_of_controllers.extend(GAME_CONTROLS)
    return list_of_controllers
