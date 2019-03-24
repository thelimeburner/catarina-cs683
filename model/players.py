from .. import globals
from ..view import view

from random import choice, random, randrange

class Player(object):
    def __init__(self, color):
        self.color = color
        self.player_id = None
        self.name = None
        self.next_player = None
        self.roads_built = []
        self.roads = 15
        self.settlements_built = []
        self.settlements = 5
        self.cities_built = []
        self.cities = 4
        self.resource_cards = {
            "brick": 0,
            "wood": 0,
            "grain": 0,
            "sheep": 0,
            "ore": 0
        }
        self.dev_cards = []
        self.knights = 0
        self.points = 0

    def choose_robber_placement(self):
        tile_id = None
        while tile_id is None:
            try:
                tile_id = int(input("Which tile would you like to block (0-18): "))
                assert 0 <= tile_id < 19
            except (ValueError, AssertionError):
                print('Please input an integer from 0 through 18, inclusive')
        return tile_id

    def choose_settlement_placement(self):
        tile_id = None
        while tile_id is None:
            try:
                tile_id = input("{}, where would you like to place a settelment: ".format(
                    self.color.capitalize()))
                if tile_id == 'undo':
                    return tile_id
                tile_id = int(tile_id)
                assert 0 <= tile_id < 54
            except (ValueError, AssertionError):
                print('Please input an integer from 0 through 54, inclusive, or "undo"')
        return tile_id

    def choose_road_placement(self):
        tile_id = None
        while tile_id is None:
            try:
                tile_id = input("{}, where would you like to place a road: ".format(
                    self.color.capitalize()))
                if tile_id == 'undo':
                    return tile_id
                tile_id = int(tile_id)
                assert 0 <= tile_id < 72
            except (ValueError, AssertionError):
                print('Please input an integer from 0 through 72, inclusive, or "undo"')
        return tile_id

    def choose_action(self):
        while True:
            choice = input("{}, what would you like to do: ".format(self.color.capitalize()))
            if choice == 'end' or choice in globals.CONTROLS or choice.startswith(globals.HACKS):
                return choice
            print("Invalid input.")

    announcements = {}

    def announce(self, event, **kwargs):
        event = self.announcements.get(event, event)
        kwargs['current_player'] = self.color.capitalize()
        print(event.format(**kwargs))

    def show_board(self, board):
        view.update_view(board)

    def available_roads(self):
        ret = []
        for road in self.roads_built:
            for neighbor in road.neighbor_roads:
                corner = (set(neighbor.neighbor_settelments)&set(road.neighbor_settelments)).pop()
                if neighbor.check_avilability() and (corner.owner == None or corner.owner == self):
                    ret.append(neighbor)
        return ret

    def available_settlements(self):
        ret = []
        for road in self.roads_built:
            for corner in road.neighbor_settelments:
                if corner.owner:
                    continue
                available = True
                for r in corner.neighbor_roads:
                    for c in r.neighbor_settelments:
                        if c.owner:
                            available = False
                if available:
                    ret.append(corner)
        return ret

    def take_turn(self, turn, game=None, pregame=False, mock_up=None):
        if pregame:
            return turn.pregame_player_action(mock_up=mock_up)
        return turn.player_action()

    def ports(self):
        ret = set()
        for settlement in self.settlements_built:
            if settlement.port:
                ret.add(settlement.port)
        return ret

    def possible_resources(self):
        ports = self.ports()
        def reduce(resources):
            ret = set([resources])
            for port in ports:
                if port == '3:1':
                    for resource in resources:
                        if resource in ports or resources[resource] < 3:
                            continue
                        reduced = dict(resources)
                        reduced[resource] -= 3
                        for resource in reduced:
                            increased = dict(reduced)
                            increased[resource] += 1
                            ret |= reduce(increased)
                    continue
                if resources[port] < 2:
                    continue
                reduced = dict(resources)
                reduced[port] -= 2
                for resource in reduced:
                    increased = dict(increased)
                    increased[resource] += 1
                    ret |= reduce(increased)
            if '3:1' not in ports:
                return ret
            for resource in resources:
                if resource in ports or resources[resource] < 4:
                    continue
                reduced = dict(resources)
                reduced[resource] -= 4
                for resource in reduced:
                    increased = dict(reduced)
                    increased[resource] += 1
                    ret |= reduce(increased)
            return ret

        return reduce(dict(self.resource_cards))

class AI(Player):
    def announce(self, event, **kwargs):
        pass

    def show_board(self, board):
        pass

    def choose_robber_placement(self):
        raise NotImplementedError

    def choose_settlement_placement(self):
        raise NotImplementedError

    def choose_road_placement(self):
        raise NotImplementedError

    def choose_action(self):
        raise NotImplementedError

    class GameState(object):
        def __init__(self, turn, game):
            self.turn = turn
            self.game = game
            self.turn_number = len(game.turn_history)

        def restore(self):
            self.game.revert_turn(self.turn_number)

class RandomAI(AI):
    def choose_robber_placement(self):
        return randrange(19)

    def choose_road_placement(self):
        return choice(self.available_roads())

    def choose_settlement_placement(self):
        return choice(self.available_settlements())
