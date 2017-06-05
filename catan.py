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
    player = {}
    for p in players:
        player[int(p.player_id)] = p
    with open("board_map.json") as json_data:
        board_map = json.load(json_data)
    board = Board(board_map)
    board.generate_new_board()
    game = Game(players, board)
    game.pregame(game.first_player(len(players)))
    while True:
        game.understand_action()
    logging.info("Game ended")
    print("Hello")

if __name__ == '__main__':
    main()
