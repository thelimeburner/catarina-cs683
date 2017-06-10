class Player(object):
    def __init__(self, player_id):
        self.player_id = player_id
        self.name = None
        self.color = None
        self.next_player = None
        self.roads_built = []
        self.roads = 15
        self.settlements_built = []
        self.settlements = 5
        self.cities_built = []
        self.cities = 4
        self.knights = 0
        self.points = 0
