
GAME_CONTROLS = [
    "dice",
    "end",
    "undo",
    "knight",
    "monopoly",
    "build roads",
    "plenty"
]


def sort_them(controllers, letter):
    current_list = [s for s in controllers]
    return [str(letter + str(s)) for s in sorted(current_list, key=int)]


# Controllers representation
def get_all_controllers(board_map):
    list_of_controllers = []
    list_of_controllers.extend(sort_them(board_map["roads_and_settelments"], "r"))
    list_of_controllers.extend(sort_them(board_map["neighbour_settelments"], "s"))
    list_of_controllers.extend(sort_them(board_map["tiles_and_settelments"], "t"))
    list_of_controllers.extend(GAME_CONTROLS)
    return list_of_controllers
