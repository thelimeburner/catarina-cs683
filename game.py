from collections import defaultdict
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
                        done = self.end_pregame_turn()
            else:
                    if self.turn.player_action():
                        done = self.end_turn()
        return done

    def end_pregame_turn(self):
        self.current_player = self.current_player.next_player
        return True

    def end_turn(self):
        self.count_longest_road()
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
        pairs = self._pair_built_roads()
        self.calculate(pairs, pairs[0])
        starting_routes = self._starting_routes()
        for road in starting_routes:
            checked = set([])
            checked.add(road)
            branches = set([])
            options = self._connected_road(road, checked,branches, 1)
            print("Longest road found: {}".format(len(options)))

    def _pair_built_roads(self):
        checked = set([])
        pairs = []
        for r in self.current_player.roads_built:
            checked.add(r)
            for s in r.neighbour_settelments:
                if s in self.current_player.settlements_built or s.owner is None:
                    for road in s.neighbour_roads:
                        if road not in checked and road in self.current_player.roads_built:
                            pairs.append([r.road_id, road.road_id])
        return pairs

    def deep_first_search(self, g, v, seen=None, path=None):
        #  https://stackoverflow.com/questions/29320556/finding-longest-path-in-a-graph
        #  http://eddmann.com/posts/depth-first-search-and-breadth-first-search-in-python/
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
                paths.extend(self.deep_first_search(g, t, seen[:], t_path))
        return paths

    def calculate(self, pairs, start):
        # Define graph by pairs/edges

        # Build graph dictionary
        g = defaultdict(list)
        for (s, t) in pairs:
            g[s].append(t)
            g[t].append(s)

        # Run DFS, compute metrics
        all_paths = self.deep_first_search(g, start)
        max_len = max(len(p) for p in all_paths)
        max_paths = [p for p in all_paths if len(p) == max_len]

        # Output
        print("All Paths:")
        print(all_paths)
        print("Longest Paths:")
        for p in max_paths:
            print("  ", p)
        print("Longest Path Length:")
        print(max_len)
        print("End")

    def _starting_routes(self):
        checked = set([])
        owned_setts = set([])
        starting_roads = set([])
        for s in self.current_player.settlements_built:
            owned_setts.add(s)
        for s in owned_setts:
            for r in s.neighbour_roads:
                if r.owner is self.current_player:
                    starting_roads.add(r)

        for road in starting_roads:
            options = []
            for s in road.neighbour_settelments:
                if s.owner is self.current_player or s.owner is None:
                    connected_roads = [r for r in s.neighbour_roads]
                    for r in connected_roads:
                        if r.owner is self.current_player and r is not road:
                            options.append(r)
            if len(options) is 1:
                checked.add(road)
        return checked

    def _connected_road(self, road, checked, branches, count):
        for s in road.neighbour_settelments:
            if s.owner is self.current_player or s.owner is None:
                for r in s.neighbour_roads:
                    if r in checked:
                        continue
                    else:
                        if r.owner is self.current_player:
                            branches.add(r)
                            checked.add(r)
                            branches = self._connected_road(r, checked, branches, count+1)
            return branches
