from random import randint


class Action(object):
    def __init__(self, do, undo):
        self.do = do
        self.undo = undo


class BuildRoadAction(Action):
    def __init__(self, board, player, road):
        self.done = False
        self.board = board
        self.current_player = player

        def do():
            road.owner = player
            road.available = False
            player.roads_built.append(road)
            player.roads -= 1
            print("Player #{} has built road {}".format(player.color, road.road_id))
            self.done = True
            return True

        def undo():
            if self.done:
                road.owner = None
                road.available = True
                player.roads_built.remove(road)
                player.roads += 1
                print("Player #{} undid the road {}".format(player.color, road.road_id))
                return True

        super().__init__(do, undo)


class BuildSettelmentAction(Action):
    def __init__(self, board, player, sett):
        self.done = False
        self.board = board
        self.current_player = player

        def do():
            sett.available = False
            sett.owner = self.current_player
            self.current_player.settlements_built.append(sett)
            for s in sett.neighbours:
                s.available = False
            self.current_player.points += 1
            self.current_player.settlements -= 1
            self.done = True
            print("Player #{} built a settelment on {}".format(self.current_player.color, sett.settelment_id))
            return True

        def undo():
            if self.done:
                sett.available = True
                sett.owner = None
                del self.current_player.settlements_built[-1]
                for s in sett.neighbours:
                    s.available = True
                self.current_player.points -= 1
                self.current_player.settlements += 1
                print("Player #{} undid the settelment on {}".format(self.current_player.color, sett.settelment_id))
                return True
            return False

        super().__init__(do, undo)


class BuildCityAction(Action):
    def __init__(self, board, player, sett):
        self.done = False
        self.board = board
        self.current_player = player

        def do():
            self.current_player.settlements_built.remove(sett)
            self.current_player.cities_built.append(sett)
            self.current_player.points += 1
            self.current_player.cities -= 1
            self.current_player.settlements += 1
            sett.settelment = False
            sett.city = True
            self.done = True
            print("Player #{} built a city on {}".format(self.current_player.color, sett.settelment_id))
            return True

        def undo():
            if self.done:
                self.current_player.settlements_built.append(sett)
                self.current_player.cities_built.remove(sett)
                self.current_player.points -= 1
                self.current_player.cities += 1
                self.current_player.settlements -= 1
                sett.settelment = True
                sett.city = False
                print("Player #{} undid the city on {}".format(self.current_player.color, sett.settelment_id))
                return True

        super().__init__(do, undo)


class PlaceRobberAction(Action):
    def __init__(self, board, player, tile_id, knight=False):
        self.done = False
        self.board = board
        self.current_player = player
        self.knight = knight

        def do():
            self.board.tiles[self.board.current_blocked].blocked = False
            self.board.previous_blocked = self.board.current_blocked
            self.board.tiles[tile_id].blocked = True
            self.board.current_blocked = tile_id
            print("Player #{} placed the robber on tile {}: The number {} and resource {}".format(
                self.current_player.color,
                self.board.tiles[tile_id].tile_id,
                self.board.tiles[tile_id].number,
                self.board.tiles[tile_id].resource))
            if knight:
                self.current_player.knights += 1
            self.done = True
            return True

        def undo():
            if self.done:
                if self.board.previous_blocked:
                    self.board.tiles[self.board.previous_blocked].blocked = True
                self.board.current_blocked = self.board.previous_blocked
                self.board.tiles[tile_id].blocked = False
                print("Player #{} undid the robber on tile {}".format(
                    self.current_player.color, self.board.tiles[tile_id].tile_id))
                print("Robber moved back to tile {}: The number {} and resource {}".format(
                    self.board.tiles[self.board.previous_blocked].tile_id,
                    self.board.tiles[self.board.previous_blocked].number,
                    self.board.tiles[self.board.previous_blocked].resource))
                if knight:
                    self.current_player.knights -= 1
                return True

        super().__init__(do, undo)
