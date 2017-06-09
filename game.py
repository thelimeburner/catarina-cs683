from random import randint
from actions import Turn


class Game(object):
    def __init__(self, players, board):
        self.players = players
        self.board = board
        self.first_player = None
        self.dice = None
        self.current_player = None
        self.pregame_turns_list = []
        self.robber = None
        self.turn = None
        self.winner = None

    def pregame_turns(self, number_of_players):
        self.first_player = randint(0, number_of_players)
        players = list(range(self.first_player, number_of_players))
        if self.first_player is not 0 or number_of_players-1:
            for i in list(range(0, self.first_player)):
                players.append(i)
            for i in reversed(players):
                players.append(i)
        elif self.first_player is 0:
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
        n = len(self.players)
        i = 0
        for p in self.players:
            if i == (n - 1):
                i = 0
            p.next_player = self.players[i]
            i += 1
        self.current_player = self.first_player

    def player_turn(self, pregame=False):
        print("Current turn: Player #{}".format(self.current_player.player_id))
        self.turn = Turn(self.board, self.current_player)
        if pregame:
            done = False
            while not done:
                if self.turn.pregame_player_action():
                    done = self.end_turn()
        else:
            if self.turn.player_action():
                return self.end_turn()
        return done

    def change_player(self):
        raise NotImplementedError

    def end_turn(self):
        # self.count_longest_road()
        if self.current_player.points >= 10:
            self.winner = self.current_player
        self.current_player = self.current_player.next_player
        return True

    def end_game(self):
        pass



