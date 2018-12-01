from random import randint, randrange


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
        self.neighbour_roads = []
        self.neighbour_settelments = []

    def check_avilability(self):
        if self.available:
            return True
        else:
            return False

    def update_status(self, available):
        self.available = available


class Settelment(object):
    def __init__(self, settelment_id):
        self.settelment_id = settelment_id
        self.available = True
        self.owner = None
        self.blocked = False
        self.numbers = set([])
        self.settelment = True
        self.city = False
        self.player = None
        self.tiles = []
        self.neighbours = []
        self.neighbour_roads = []

    def check_avilability(self):
        if self.available:
            return True
        else:
            return False

    def update_owner(self, player_id):
        self.player = player_id
        self.available = False

    def upgrade(self):
        self.settelment = False
        self.city = True


class Board(object):
    def __init__(self, board_map):
        self.board_map = board_map
        self.dice = None
        self.tiles = []
        self.roads = []
        self.settelments = []
        self.longest_road = None
        self.largest_army = None
        self.previous_blocked = None
        self.current_blocked = None

    def generate_new_board(self):
        resources = [
            'Brick', 'Brick', 'Brick', 'Desert', 'Ore', 'Ore', 'Ore', 'Sheep', 'Sheep', 'Sheep',
            'Sheep', 'Wheat', 'Wheat', 'Wheat', 'Wheat', 'Wood', 'Wood', 'Wood', 'Wood'
        ]
        numbers = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]

        tiles_id = list(range(0, 19))
        last_n = 18
        for tile in tiles_id:
            resource_index = randint(0, last_n)
            self.tiles.append(Tile(tile, resources[resource_index]))
            print("Tile #{} is now {}".format(tile, resources[resource_index]))
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
                print("Tile #{} is a Desert".format(self.tiles[tile].tile_id))
                continue
            self.tiles[tile].update_number(numbers[0])
            print("Tile #{} has the number {}".format(self.tiles[tile].tile_id, numbers[0]))
            del numbers[0]

        for road_id in range(0, 72):
            self.roads.append(Road(road_id))
        for settelment_id in range(0, 54):
            self.settelments.append(Settelment(settelment_id))
        self._connect_roads()
        self._connect_settelments()
        self._connect_tiles()
        self._init_robber()

    def _connect_tiles(self):
        for tile in self.tiles:
            for key_tile, value_connected_settelments in self.board_map['tiles_and_settelments'].items():
                if int(key_tile) is tile.tile_id:
                    tile.buildings = [self.settelments[idx] for idx in value_connected_settelments]

    def _connect_settelments(self):
        for settelment in self.settelments:
            for key_settelment, value_neighbour_settelments in self.board_map['neighbour_settelments'].items():
                if int(key_settelment) is settelment.settelment_id:
                    settelment.neighbours = [self.settelments[idx] for idx in value_neighbour_settelments]
        for settelment in self.settelments:
            for key_settelment, value_connected_tiles in self.board_map['tiles_for_each_settelment'].items():
                if int(key_settelment) is settelment.settelment_id:
                    settelment.tiles = [self.tiles[idx] for idx in value_connected_tiles]
        for settelment in self.settelments:
            for key_settelment, value_connected_roads in self.board_map['settelments_and_roads'].items():
                if int(key_settelment) is settelment.settelment_id:
                    settelment.neighbour_roads = [self.roads[idx] for idx in value_connected_roads]
        for settelment in self.settelments:
            for tile in settelment.tiles:
                settelment.numbers.add(tile.number)

    def _connect_roads(self):
        for road in self.roads:
            for key_road, value_connecting_roads in self.board_map['connecting_roads'].items():
                if int(key_road) is road.road_id:
                    road.neighbour_roads = [self.roads[idx] for idx in value_connecting_roads]
        for road in self.roads:
            for key_road, neighbour_settelments in self.board_map['roads_and_settelments'].items():
                if int(key_road) is road.road_id:
                    road.neighbour_settelments = [self.settelments[idx] for idx in neighbour_settelments]

    def _init_robber(self):
        for t in self.tiles:
            if t.resource == 'Desert':
                self.current_blocked = t.tile_id

