from random import randint
from actions import Turn


class Game(object):
    def __init__(self, players, board):
        self.players = players
        self.board = board
        self.dice = None
        self.previous_player = None
        self.current_player = None
        self.robber = None
        self.turn = None

    def seat_players(self):
        n = len(self.players)
        i = 0
        for p in self.players:
            if i == (n - 1):
                i = 0
            p.next_player = self.players[i]
            i += 1

    def player_turn(self, player):
        """
        Advances to the next player
        :param player: 
        :return: 
        """
        self.previous_player = self.current_player
        self.current_player = player
        self.dice = None
        print("Current turn: Player #", self.current_player.player_id)
        self.turn = Turn(self.board, player)

    def pregame(self, turns_list):
        while turns_list:
            self.player_turn(self.players[turns_list[0]])
            self.wait_for_player_input_sett()
            self.wait_for_player_input_road()
            del turns_list[0]
        self.seat_players()
        print("Game starts now")
        print("Current turn: Player ", self.current_player.player_id)
        self.roll_dice()

    def wait_for_player_input_road(self):
        valid = False
        options = set([])
        for s in self.current_player.settlements_built:
            for r in s.neighbour_roads:
                if r.available:
                    options.add(r.road_id)
        while not valid:
            road_id = int(input("Player #{}, where would you like to build a road: "
                                .format(self.current_player.player_id)))
            if road_id not in list(range(0, 72)):
                print("Not a valid road id")
                continue
            if road_id not in options:
                print("Not an optional road id")
                continue
            if self.road_spot_available(road_id):
                valid = True
            else:
                print("Not an optional road id")
        self.build_road(road_id)

    def wait_for_player_input_sett(self):
        valid = False
        while not valid:
            sett_id = int(input("Player #{}, where would you like to build a settelment: "
                                .format(self.current_player.player_id)))
            if sett_id not in list(range(0, 54)):
                print("Not a valid settelment id")
                continue
            if self.sett_spot_available(sett_id):
                valid = True
            else:
                print("Not an optional spot")
        self.build_first_settelment(sett_id)

    @staticmethod
    def first_player(number_of_players):
        first = randint(0, number_of_players)
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
        return players


