from .. import globals
from ..view import view

from random import choice, random, randrange
from csv import DictWriter

class Player(object):
    def __init__(self, color, board):
        self.color = color
        self.board = board
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
                print('Please input an integer from 0 through 53, inclusive, or "undo"')
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

    def available_roads(self, roads=None):
        if roads is None:
            roads = self.roads_built
        ret = []
        for road in roads:
            for neighbor in road.neighbor_roads:
                corner = (set(neighbor.neighbor_settlements)&set(road.neighbor_settlements)).pop()
                if neighbor.check_avilability() and (corner.owner == None or corner.owner == self):
                    ret.append(neighbor)
        return ret

    def available_settlements(self, settlements=None, roads=None):
        if settlements is None:
            settlements = self.settlements_built
        if roads is None:
            roads = self.roads_built
        ret = []
        for road in roads:
            for corner in road.neighbor_settlements:
                if corner.owner or corner in settlements:
                    continue
                available = True
                for r in corner.neighbor_roads:
                    for c in r.neighbor_settlements:
                        if c.owner or c in settlements:
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

    def possible_resources(self, resource_deck=None, resources=None):
        if resource_deck is None:
            resource_deck = self.board.cards_deck.deck
        if resources is None:
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

        return sorted(reduce([], dict(resources), dict(self.board.cards_deck.deck)), key=lambda x: sum([n for n in x[1].values()]), reverse=True)

    costs = {#'development card': {'sheep': 1, 'ore': 1, 'grain': 1},
             'settlement':       {'sheep': 1, 'brick': 1, 'grain': 1, 'wood': 1},
             'city':             {'grain': 2, 'ore': 3},
             'road':             {'brick': 1, 'wood': 1}}

    def possible_actions(self):
        def safe_recurse(actions, resources, deck, settlements, roads, cities, cost):
            resources = dict(resources)
            deck = dict(deck)
            for resource, quant in cost.items():
                resources[resource] -= quant
                deck[resource] += quant
            return single_buy(actions, resources, deck, settlements, roads, cities)
        def single_buy(actions, resources, resource_deck, settlements, roads, cities):
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
                            for corner in self.available_settlements(settlements=settlements, roads=roads):
                                new_action = 's{}'.format(corner.settlement_id)
                                if new_action not in actions:
                                    new_actions = actions + trades
                                    new_actions.append(new_action)
                                    new_settlements = list(settlements)
                                    new_settlements.append(corner)
                                    ret.extend(safe_recurse(new_actions, resources, deck, new_settlements, roads, cities, cost))
                        elif action == 'city' and self.cities:
                            for settlement in settlements:
                                if settlement in cities or settlement.city:
                                    continue
                                new_action = 's{}'.format(settlement.settlement_id)
                                if new_action not in actions:
                                    new_actions = actions + trades
                                    new_actions.append(new_action)
                                    new_cities = list(cities)
                                    new_cities.append(settlement)
                                    ret.extend(safe_recurse(new_actions, resources, deck, settlements, roads, new_cities, cost))
                        elif action == 'road' and self.roads - len([x for x in actions if x[0] == 'r']) > 0:
                            for edge in self.available_roads(roads=roads):
                                new_action = 'r{}'.format(edge.road_id)
                                if new_action not in actions:
                                    new_actions = actions + trades
                                    new_actions.append(new_action)
                                    new_roads = list(roads)
                                    new_roads.append(edge)
                                    ret.extend(safe_recurse(new_actions, resources, deck, settlements, new_roads, cities, cost))
                        break
            return ret

        ret = single_buy([], self.resource_cards, self.board.cards_deck.deck, self.settlements_built, self.roads_built, [])
        for action in ret:
            action.append('end')
        return ret

    def end_game_hook(self, won=True):
        return True

class AI(Player):
    def __init__(self, color, board):
        self.plan = []
        self.state_tree = None
        self.current_state = None
        self.turns_remaining = 10**2
        super().__init__(color, board)

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

    class State(object):
        def __init__(self, parent=None, **kwargs):
            self.parent = parent
            if parent:
                parent.add_child(self)
            self.children = []
            self.num_leaves = 0
            self.num_wins = 0
            self.features = kwargs

        def add_child(self, child):
            self.children.append(child)
            child.parent = self

        def ancestry(self):
            state = self
            while state:
                yield state
                state = state.parent

        def decendants(self):
            yield self
            for child in self.children():
                yield from child.descendents()

    def extract_features(self, game):
        features = {}
        for player in game.players:
            color = player.color
            player_dict = {}
            player_dict['setts'] = 5-player.settlements
            player_dict['roads'] = 15-player.roads
            player_dict['cities'] = 4-player.cities
            possible_ports = ['3:1']
            player_dict['EVs'] = {}
            for resource, count in player.resource_cards.items():
                player_dict[resource] = count
                possible_ports.append(resource)
                player_dict['EVs'][resource] = 0
            ports = player.ports()
            player_dict['ports'] = {}
            for port in possible_ports:
                player_dict['ports'][port] = port in ports
            features[color] = player_dict
        for tile in game.board.tiles:
            if tile.blocked or not tile.number:
                continue
            rolls = 6 - abs(tile.number-7)
            for building in tile.buildings:
                if not building.owner:
                    continue
                mult = 2 if building.city else 1
                features[building.owner.color.capitalize()]['EVs'][tile.resource.lower()] += mult * rolls
        return features

    def end_game_hook(self, game, won=False):
        tree_depth = 0
        if won:
            Player.show_board(self, game.board)
            print('{} won!'.format(self.color.capitalize()))
        for ancestor in self.current_state.ancestry():
            tree_depth += 1
            if won:
                ancestor.num_wins += 1
            ancestor.num_leaves += 1
        if self.turns_remaining > 0:
            to_turn = min(0, tree_depth - randrange(12, tree_depth))
            for i, ancestor in enumerate(self.current_state.ancestry()):
                if i == tree_depth - to_turn:
                    self.current_state = ancestor
                    break
            self.turns_remaining -= to_turn
            game.revert_turn(to_turn)
            return True

        return False

    def record_features(self, output_file=None):
        if output_file is None:
            output_file = '{}_features.csv'.format(self.color)
        def flatten(features, prefix=''):
            ret = {}
            for k, v in features.items():
                if type(v) == type({}):
                    ret.update(flatten(v, prefix='{}_{}'.format(prefix, k)))
                else:
                    ret[k] = v
            return ret
        fieldnames = sorted(flatten(self.state_tree.features).keys(), key=str.lower)
        fieldnames.append('win_prop')
        writer = DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for state in self.state_tree.descendents():
            features = flatten(state.features)
            features.append('{.4f}'.format(state.num_leaves/state.num_leaves))
            writer.writerow()

class RandomAI(AI):
    def choose_robber_placement(self):
        return randrange(19)

    def choose_road_placement(self):
        return choice(self.available_roads())

    def choose_settlement_placement(self):
        return choice(self.available_settlements())

    def take_turn(self, turn, game, pregame=False, mock_up=None):
        if pregame:
            return turn.pregame_player_action(mock_up=mock_up)
        self.plan = choice(self.possible_actions())
        new_state = self.State(parent=self.current_state, **self.extract_features(game))
        self.current_state = new_state
        return turn.player_action()

    def choose_action(self):
        return self.plan.pop(0)
