from random import randint, randrange, shuffle


class DevelopmentCard(object):
    def __init__(self, card_type):
        self.card_type = card_type
        self.owner = None
        self.already_used = False

    def used(self):
        self.already_used = True


class ResourceDeck(object):
    def __init__(self):
        self.deck = {
            "brick": 19,
            "wood": 19,
            "grain": 19,
            "sheep": 19,
            "ore": 19
        }

    def accept(self, card, number_of_cards=1):
        self.deck[card] += number_of_cards

    def give(self, card, number_of_cards=1):
        if self.deck[card] - number_of_cards >= 0:
            self.deck[card] -= number_of_cards
            return number_of_cards
        else:
            leftovers = self.deck[card]
            self.deck[card] -= self.deck[card]
            return leftovers


class Tile(object):
    def __init__(self, tile_id, resource):
        self.tile_id = tile_id
        self.resource = resource
        self.number = None
        self.blocked = False
        self.roads = []
        self.buildings = []

    def update_number(self, number):
        self.number = number


class Road(object):
    def __init__(self, road_id):
        self.road_id = road_id
        self.available = True
        self.owner = []
        self.neighbor_roads = []
        self.neighbor_settlements = []

    def check_avilability(self):
        if self.available:
            return True
        else:
            return False

    def update_status(self, available):
        self.available = available

    def __str__(self):
        return 'r{}'.format(self.road_id)

    __repr__ = __str__


class Settelment(object):
    def __init__(self, settlement_id):
        self.settlement_id = settlement_id
        self.available = True
        self.owner = None
        self.blocked = False
        self.numbers = set([])
        self.settlement = True
        self.city = False
        self.player = None
        self.tiles = []
        self.neighbors = []
        self.neighbor_roads = []
        self.port = None

    def check_avilability(self):
        if self.available:
            return True
        else:
            return False

    def update_owner(self, player_id):
        self.player = player_id
        self.available = False

    def upgrade(self):
        self.settlement = False
        self.city = True

    def __str__(self):
        return 's{}'.format(self.settlement_id)

    __repr__ = __str__


class Board(object):
    def __init__(self, board_map):
        self.board_map = board_map
        self.dice = None
        self.tiles = []
        self.roads = []
        self.cards_deck = None
        self.dev_cards = []
        self.settlements = []
        self.longest_road = None
        self.largest_army = None
        self.previous_blocked = None
        self.current_blocked = None

    def generate_new_board(self):
        resources = [
            'Brick', 'Brick', 'Brick', 'Desert', 'Ore', 'Ore', 'Ore', 'Sheep', 'Sheep', 'Sheep',
            'Sheep', 'Grain', 'Grain', 'Grain', 'Grain', 'Wood', 'Wood', 'Wood', 'Wood'
        ]
        numbers = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]

        tiles_id = list(range(0, 19))
        last_n = 18
        for tile in tiles_id:
            resource_index = randint(0, last_n)
            self.tiles.append(Tile(tile, resources[resource_index]))
            #print("Tile #{} is now {}".format(tile, resources[resource_index]))
            del resources[resource_index]
            last_n -= 1
        starting_point = randrange(0, 11, 2)
        # anchor_points = {2: 13, 4: 14, 6: 15, 8: 16, 10: 17}
        anc = {
            0: list(range(0, 19)),
            2: list(range(2, 12)) + [0, 1] + list(range(13, 18)) + [12, 18],
            4: list(range(4, 12)) + list(range(0, 4)) + list(range(14, 18)) + [12, 13, 18],
            6: list(range(6, 12)) + list(range(0, 6)) + list(range(15, 18)) + list(range(12, 15)) + [18],
            8: list(range(8, 12)) + list(range(0, 8)) + [16, 17] + list(range(12, 16)) + [18],
            10: [10, 11] + list(range(0, 10)) + [17] + list(range(12, 17)) + [18]
        }
        tiles_id = anc[starting_point]
        for tile in tiles_id:
            if self.tiles[tile].resource is 'Desert':
                self.tiles[tile].blocked = True
                #print("Tile #{} is a Desert".format(self.tiles[tile].tile_id))
                continue
            self.tiles[tile].update_number(numbers[0])
            #print("Tile #{} has the number {}".format(self.tiles[tile].tile_id, numbers[0]))
            del numbers[0]

        for road_id in range(0, 72):
            self.roads.append(Road(road_id))
        for settlement_id in range(0, 54):
            self.settlements.append(Settelment(settlement_id))
        for port, settlements in self.board_map['ports'].items():
            for settlement in settlements:
                self.settlements[settlement].port = port
        self.cards_deck = ResourceDeck()
        self._connect_roads()
        self._connect_settlements()
        self._connect_tiles()
        self._stack_development_card()
        self._init_robber()

    def _connect_tiles(self):
        for tile in self.tiles:
            for key_tile, value_connected_settlements in self.board_map['tiles_and_settlements'].items():
                if int(key_tile) is tile.tile_id:
                    tile.buildings = [self.settlements[idx] for idx in value_connected_settlements]

    def _connect_settlements(self):
        for settlement in self.settlements:
            for key_settlement, value_neighbor_settlements in self.board_map['neighbor_settlements'].items():
                if int(key_settlement) is settlement.settlement_id:
                    settlement.neighbors = [self.settlements[idx] for idx in value_neighbor_settlements]
        for settlement in self.settlements:
            for key_settlement, value_connected_tiles in self.board_map['tiles_for_each_settlement'].items():
                if int(key_settlement) is settlement.settlement_id:
                    settlement.tiles = [self.tiles[idx] for idx in value_connected_tiles]
        for settlement in self.settlements:
            for key_settlement, value_connected_roads in self.board_map['settlements_and_roads'].items():
                if int(key_settlement) is settlement.settlement_id:
                    settlement.neighbor_roads = [self.roads[idx] for idx in value_connected_roads]
        for settlement in self.settlements:
            for tile in settlement.tiles:
                settlement.numbers.add(tile.number)

    def _connect_roads(self):
        for road in self.roads:
            for key_road, value_connecting_roads in self.board_map['connecting_roads'].items():
                if int(key_road) is road.road_id:
                    road.neighbor_roads = [self.roads[idx] for idx in value_connecting_roads]
        for road in self.roads:
            for key_road, neighbor_settlements in self.board_map['roads_and_settlements'].items():
                if int(key_road) is road.road_id:
                    road.neighbor_settlements = [self.settlements[idx] for idx in neighbor_settlements]

    def _stack_development_card(self):
        cards = {
            "knight": 14,
            "victory_point": 5,
            "monopoly": 2,
            "year_of_plenty": 2,
            "build_roads": 2
        }
        for card, number in cards.items():
            for _ in range(number):
                self.dev_cards.append(DevelopmentCard(card_type=card))
        shuffle(self.dev_cards)

    def _init_robber(self):
        for t in self.tiles:
            if t.resource == 'Desert':
                self.current_blocked = t.tile_id
