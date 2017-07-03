from players import Player
from board import Board
from game import Game
import game_config
import logging
import json


def main():
    logging.basicConfig(format="%(asctime)s.%(msecs)03d %(levelname)s>  %(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S",
                        level=logging.INFO)
    logging.info("Starting a new game")
    with open("board_map.json") as json_data:
        board_map = json.load(json_data)
    board = Board(board_map)
    # board.generate_new_board()
    playing_colors = ['Red', 'Blue', 'White']
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
    while True:
        if game.player_turn():
            if game.winner:
                if game.end_game():
                    break
    print("End reached")

if __name__ == '__main__':
    main()
