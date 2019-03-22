from players import Player
from board import Board
import globals
from game import Game
import game_config
import control
import view
import logging
import json

def main():
    logging.basicConfig(format="%(asctime)s.%(msecs)03d %(levelname)s>  %(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S",
                        level=logging.INFO)
    # import the board skeleton in json format
    logging.info("Starting a new game")
    globals.init()
    with open("board_map.json") as json_data:
        board_map = json.load(json_data)
    # initialize controllers
    globals.CONTROLS = control.get_all_controllers(board_map)
    globals.HACKS = ("dice=", "end=", "pdb")
    globals.SPECIFIC_CONTROLS = {
        "roads": control.get_roads_controllers(board_map),
        "setts": control.get_setts_controllers(board_map),
        "tiles": control.get_tiles_controllers(board_map)
    }
    # import the asci board json
    view.initialize_board()

    board = Board(board_map)
    board.generate_new_board()
    playing_colors = ['Red', 'Blue', 'Yellow']
    game = Game(playing_colors, board)
    game.determine_starting_color()
    game.seat_players()
    # PreGame starts here
    for player in game.players:
        game.current_player = player
        game.player_turn(pregame=True)
    for player in reversed(game.players):
        game.current_player = player
        game.player_turn(pregame=True)
    # game starts here
    while True:
        if game.player_turn():
            if game.winner:
                if game.end_game():
                    break
    print("End reached")


if __name__ == '__main__':
    main()
