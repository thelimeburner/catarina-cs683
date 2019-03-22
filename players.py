import globals

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

    def available_roads(self):
        for road in self.roads_built:
            print(road)
