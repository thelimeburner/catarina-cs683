import json
import logging, trace, time
import os

from . import globals
from . import game_config
from .control import control
from .view import view
from .model.game import Game
from .model.players import Player
from .model.board import Board
from .model.res import PATH as RES_PATH

def main():
    logging.basicConfig(format="%(asctime)s.%(msecs)03d %(levelname)s>  %(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S",
                        level=logging.INFO)
    # import the board skeleton in json format
    logging.info("Starting a new game")
    globals.init()
    with open(os.path.join(RES_PATH, "board_map.json")) as json_data:
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
    if game_config.using_search_AI:
        tracer = trace.Trace(trace=0, outfile='coverage/randomx3_{}.trace'.format(int(time.time())))
    else:
        tracer = trace.Trace(trace=0, outfile='coverage/bsrandomx2_{}.trace'.format(int(time.time())))
    tracer.run('main()')
    r = tracer.results()
    r.write_results(show_missing=True, coverdir="./coverage", summary=True)
