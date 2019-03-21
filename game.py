from collections import defaultdict
from players import Player
import view
from random import randint
from turn import Turn
import networkx as nx
from game_config import *


class Game(object):
    def __init__(self, playing_colors, board):
        self.playing_colors = playing_colors
        self.players = None
        self.board = board
        self.first_player = None
        self.current_player = None
        self.robber = None
        self.turn = None
        self.winner = None

    def determine_starting_color(self):
        first_color = randint(0, len(self.playing_colors) - 1)
        self.first_player = self.playing_colors[first_color]
        # print("First player is {}".format(self.first_player.color))

    def seat_players(self):
        self.players = [Player(self.first_player)]
        for i in range(0, len(self.playing_colors) - 1):
            self.players.append(Player(PLAYERS_ORDER[len(self.playing_colors)][self.players[-1].color]))
            self.players[-2].next_player = self.players[-1]
        self.players[-1].next_player = self.players[0]
        self.first_player = self.players[0]

    def player_turn(self, pregame=False):
        print("Current turn: {} player".format(self.current_player.color.capitalize()))
        self.turn = Turn(self.board, self.current_player)
        done = False
        while not done:
            if pregame:
                    if self.turn.pregame_player_action(mock_up=MOCK_UP):
                        done = self.end_pregame_turn()
            else:
                    if self.turn.player_action():
                        done = self.end_turn()
        return done

    def end_pregame_turn(self):
        self.current_player = self.current_player.next_player
        view.update_view(self.board)
        return True

    def end_turn(self):
        self.count_longest_road()
        self.count_largest_army()
        self.board.dice = None
        if self.current_player.points >= 10:
            self.winner = self.current_player
            return True
        self.current_player = self.current_player.next_player
        view.update_view(self.board)
        return True

    def end_game(self):
        print("The winner is: {} with {} victory points".format(self.winner.color.capitalize(), self.winner.points))
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
        whole_graph = {}
        for road in self.current_player.roads_built:
            whole_graph.update(self._connected_road(road))
        G = nx.Graph()
        sub_graphs = nx.connected_component_subgraphs(G)

    def _return_nodes(self):
        pass

    def _pairs(self):
        pairs = []
        seen = set([])
        for road in self.current_player.roads_built:
            for s in road.neighbour_settelments:
                if s.owner is self.current_player or s.owner is None:
                    for r in s.neighbour_roads:
                        if r in seen:
                            continue
                        if r is not road and r.owner is self.current_player:
                            pairs.append([road.road_id, r.road_id])
                            seen.add(r)
        return pairs

    def _connected_road(self, road):
        connected = ()
        for s in road.neighbour_settelments:
            if s.owner is self.current_player or s.owner is None:
                for r in s.neighbour_roads:
                    if r is road:
                        continue
                    else:
                        if r in self.current_player.roads_built:
                            connected = connected + (r.road_id,)
        return {road.road_id: connected}


def dfs(g, v, seen=None, path=None):
    if seen is None:
        seen = []
    if path is None:
        path = [v]

    seen.append(v)

    paths = []
    for t in g[v]:
        if t not in seen:
            t_path = path + [t]
            paths.append(tuple(t_path))
            paths.extend(dfs(g, t, seen[:], t_path))
    return paths
