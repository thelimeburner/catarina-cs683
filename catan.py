from board import Board
from game import Game
from players import Player
import logging
import json


def main():
    logging.basicConfig(format="%(asctime)s.%(msecs)03d %(levelname)s>  %(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S",
                        level=logging.INFO)
    logging.info("Starting a new game")
    players = [Player(1), Player(2), Player(3)]
    with open("board_map.json") as json_data:
        board_map = json.load(json_data)
    board = Board(board_map)
    board.generate_new_board()
    game = Game(players, board)
    # PreGame starts here
    if game.pregame():
        print("Game starts now")
    game.seat_players()
    while True:
        if game.player_turn():
            if game.winner:
                if game.end_game():
                    break
    print("End reached")

if __name__ == '__main__':
    main()
