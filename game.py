from random import randint
from actions import Turn


class Game(object):
    def __init__(self, players, board):
        self.players = players
        self.board = board
        self.first_player = None
        self.current_player = None
        self.pregame_turns_list = []
        self.robber = None
        self.turn = None
        self.winner = None

    def pregame_turns(self, number_of_players):
        first = randint(0, number_of_players-1)
        self.first_player = self.players[first]
        print("First player is Player #{}".format(self.first_player.player_id))
        players = list(range(first, number_of_players))
        if first is not 0 or number_of_players-1:
            for i in list(range(0, first)):
                players.append(i)
            for i in reversed(players):
                players.append(i)
        elif first is 0:
            for i in reversed(players):
                players.append(i)
        else:
            for i in list(range(0, number_of_players)):
                players.append(i)
            for i in reversed(players):
                players.append(i)
        self.pregame_turns_list = players

    def change_pregame_player(self):
        self.current_player = self.players[self.pregame_turns_list[0]]
        del self.pregame_turns_list[0]

    def pregame(self):
        self.pregame_turns(len(self.players))
        while True:
            self.change_pregame_player()
            if self.player_turn(pregame=True):
                if len(self.pregame_turns_list) == 0:
                    break
        return True

    def seat_players(self):
        self.players[0].next_player = self.players[1]
        self.players[1].next_player = self.players[2]
        if len(self.players) == 3:
            self.players[2].next_player = self.players[0]
        else:
            self.players[2].next_player = self.players[3]
            self.players[3].next_player = self.players[0]
        self.current_player = self.first_player

    def player_turn(self, pregame=False):
        print("Current turn: Player #{}".format(self.current_player.player_id))
        self.turn = Turn(self.board, self.current_player)
        done = False
        while not done:
            if pregame:
                    if self.turn.pregame_player_action(mock_up=True):
                        done = self.end_turn()
            else:
                    if self.turn.player_action():
                        done = self.end_turn()
        return done

    def end_turn(self):
        # self.count_longest_road()
        self.count_largest_army()
        self.board.dice = None
        if self.current_player.points >= 10:
            self.winner = self.current_player
            return True
        self.current_player = self.current_player.next_player
        return True

    def end_game(self):
        print("The winner is: Player #{} with {} victory points".format(self.winner.player_id, self.winner.points))
        return True

    def count_largest_army(self):
        if self.current_player.knights >= 3:
            if self.board.largest_army:
                if self.current_player.knights > self.board.largest_army.knights:
                    self.board.largest_army.points -= 2
                    self.board.largest_army = self.current_player
                    self.current_player.points += 2
            else:
                self.board.largest_army = self.current_player
                self.current_player.points += 2

    def count_longest_road(self):
        pass
