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
        self.knights = 0
        self.points = 0
