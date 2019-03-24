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
                tile_id = input("{}, where would you like to place a settlement: ".format(
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
            if choice == 'end' or choice in globals.CONTROLS or choice.startswith(globals.HACKS) or choice.startswith('t'):
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
                corner = (set(neighbor.neighbor_settlements)&set(road.neighbor_settlements)).pop()
                if neighbor.check_avilability() and (corner.owner == None or corner.owner == self):
                    ret.append(neighbor)
        return ret

    def available_settlements(self):
        ret = []
        for road in self.roads_built:
            for corner in road.neighbor_settlements:
                if corner.owner:
                    continue
                available = True
                for r in corner.neighbor_roads:
                    for c in r.neighbor_settlements:
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

    def possible_resources(self, resource_deck, resources=None):
        if resources == None:
            resources = self.resource_cards
        ports = self.ports()
        def reduce(path, resources, resource_deck):
            ret = [(path, resources, resource_deck)]
            for port in ports:
                if port == '3:1':
                    for resource in resources:
                        if resource in ports or resources[resource] < 3:
                            continue
                        for new_resource in resources:
                            if not resource_deck[new_resource]:
                                continue
                            deck = dict(resource_deck)
                            reduced = dict(resources)
                            reduced[new_resource] += 1
                            reduced[resource] -= 3
                            deck[new_resource] -= 1
                            deck[resource] += 3
                            new_path = list(path)
                            new_path.append('t3{}:{}'.format(resource, new_resource))
                            ret.extend(reduce(new_path, reduced, deck))
                    continue
                if resources[port] < 2:
                    continue
                for resource in resources:
                    if not resource_deck[resource]:
                        continue
                    deck = dict(resource_deck)
                    reduced = dict(resources)
                    reduced[resource] += 1
                    reduced[port] -= 2
                    deck[resource] -= 1
                    deck[port] += 2
                    new_path = list(path)
                    new_path.append('t2{}:{}'.format(port, resource))
                    ret.extend(reduce(new_path, reduced, deck))
            if '3:1' in ports:
                return ret
            for resource in resources:
                if resource in ports or resources[resource] < 4:
                    continue
                for new_resource in resources:
                    if not resource_deck[new_resource]:
                        continue
                    deck = dict(resource_deck)
                    reduced = dict(resources)
                    reduced[new_resource] += 1
                    reduced[resource] -= 4
                    deck[new_resource] -= 1
                    deck[resource] += 4
                    new_path = list(path)
                    new_path.append('t4{}:{}'.format(resource, new_resource))
                    ret.extend(reduce(new_path, reduced, deck))
            return ret

        return sorted(reduce([], dict(resources), dict(resource_deck)), key=lambda x: sum([n for n in x[1].values()]), reverse=True)

    costs = {#'development card': {'sheep': 1, 'ore': 1, 'grain': 1},
             'settlement':       {'sheep': 1, 'brick': 1, 'grain': 1, 'wood': 1},
             'city':             {'grain': 2, 'ore': 3},
             'road':             {'brick': 1, 'wood': 1}}

    def possible_actions(self, resource_deck):
        def safe_recurse(actions, resources, deck, cost):
            resources = dict(resources)
            deck = dict(deck)
            for resource, quant in cost.items():
                resources[resource] -= quant
                deck[resource] += quant
            return single_buy(actions, resources, deck)
        def single_buy(actions, resources, resource_deck):
            possible_resources = self.possible_resources(resource_deck, resources=resources)
            ret = [actions]
            for action, cost in self.costs.items():
                for trades, resources, deck in possible_resources:
                    can_pay = True
                    for resource in cost:
                        if resources[resource] < cost[resource]:
                            can_pay = False
                            break
                    if can_pay:
                        if action == 'settlement' and self.settlements:
                            for corner in self.available_settlements():
                                new_action = 's{}'.format(corner)
                                if new_action not in actions:
                                    new_actions = actions + trades
                                    new_actions.append(new_action)
                                    ret.extend(safe_recurse(new_actions, resources, deck, cost))
                        elif action == 'city' and self.cities:
                            for settlement in self.settlements_built:
                                new_action = 's{}'.format(settlement.settlement_id)
                                if new_action not in actions:
                                    new_actions = actions + trades
                                    new_actions.append(new_action)
                                    ret.extend(safe_recurse(new_actions, resources, deck, cost))
                        elif action == 'road' and self.roads:
                            for edge in self.available_roads():
                                new_action = 'r{}'.format(edge.road_id)
                                if new_action not in actions:
                                    new_actions = actions + trades
                                    new_actions.append(new_action)
                                    ret.extend(safe_recurse(new_actions, resources, deck, cost))
                        break
            return ret

        ret = single_buy([], self.resource_cards, resource_deck)
        for action in ret:
            action.append('end')
        return ret

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
