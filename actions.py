from random import randint

MOCK_UP = [31, 32, 33, 35, 35, 38, 37, 41, 39, 44, 41, 68]
FRIENDLY_ROBBER = True


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
            print("Player #{} has built road {}".format(player.player_id, road.road_id))
            self.done = True
            return True

        def undo():
            if self.done:
                road.owner = None
                road.available = True
                player.roads_built.remove(road)
                player.roads += 1
                print("Player #{} undid the road {}".format(player.player_id, road.road_id))
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
            print("Player #{} built a settelment on {}".format(self.current_player.player_id, sett.settelment_id))
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
                print("Player #{} undid the settelment on {}".format(self.current_player.player_id, sett.settelment_id))
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
            print("Player #{} built a city on {}".format(self.current_player.player_id, sett.settelment_id))
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
                print("Player #{} undid the city on {}".format(self.current_player.player_id, sett.settelment_id))
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
                self.current_player.player_id,
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
                    self.current_player.player_id, self.board.tiles[tile_id].tile_id))
                print("Robber moved back to tile {}: The number {} and resource {}".format(
                    self.board.tiles[self.board.previous_blocked].tile_id,
                    self.board.tiles[self.board.previous_blocked].number,
                    self.board.tiles[self.board.previous_blocked].resource))
                if knight:
                    self.current_player.knights -= 1
                return True

        super().__init__(do, undo)


class Turn(object):
    def __init__(self, board, current_player):
        self.board = board
        self.current_player = current_player
        self.actions = []

    def pregame_player_action(self, mock_up=False):
        # Undo == 666
        # End turn == 777
        self.actions = []
        built_sett = False
        built_road = False
        done_turn = False
        while not built_sett:
            if mock_up:
                choice_sett = MOCK_UP[0]
                print("Player #{}, where would you like to place a settelment: {}".format(
                    self.current_player.player_id, MOCK_UP[0]))
                del MOCK_UP[0]
                if self.build_settelment(choice_sett, first=True):
                    break
            choice_sett = int(input("Player #{}, where would you like to place a settelment: ".format(
                self.current_player.player_id)))
            if choice_sett not in list(range(0, 54)):
                if choice_sett == 666:
                    if len(self.actions) > 0:
                        self.undo()
                        return False
                    else:
                        print("Nothing to Undo")
                print("Invalid input, try again")
            else:
                if self.build_settelment(choice_sett, first=True):
                    built_sett = True
        while not built_road:
            if mock_up:
                choice_road = MOCK_UP[0]
                print("Player #{}, where would you like to place a road: {}".format(
                    self.current_player.player_id, MOCK_UP[0]))
                del MOCK_UP[0]
                if self.build_road(choice_road, choice_sett):
                    break
            choice_road = int(input("Player #{}, where would you like to place a road: ".format(
                self.current_player.player_id)))
            if choice_road not in list(range(0, 72)):
                if choice_road == 666:
                    if len(self.actions) > 0:
                        self.undo()
                        self.undo()
                        return False
                    else:
                        print("Nothing to Undo")
                print("Invalid input, try again")
            else:
                if self.build_road(choice_road, choice_sett):
                    built_road = True
        while not done_turn:
            if mock_up:
                break
            choice_end = int(input("Player #{}, end the turn or undo (777 = end, 666 = undo) ".format(
                self.current_player.player_id)))
            if choice_end == 777:
                done_turn = True
            elif choice_end == 666:
                self.undo()
                self.undo()
                return False
        return True

    def player_action(self):
        while True:
            choice = input("Player #{}, what would you like to do: ".format(self.current_player.player_id))
            if choice == 'End_Turn':
                break
            else:
                self.parse_action(choice)
        return True

    def parse_action(self, choice):
        if len(choice) is 3:
            if choice[0] == 'R':
                self.build_road(int(choice[1:]))
            elif choice[0] == 'S':
                if self.board.settelments[int(choice[1:])].owner is self.current_player:
                    if not self.board.settelments[int(choice[1:])].city:
                        self.upgrade_settelment(int(choice[1:]))
                    else:
                        print("Cannot upgrade. It is already a city")
                        return
                else:
                    self.build_settelment(int(choice[1:]))
            elif choice[0] == 'D':
                self.roll_dice(int(choice[1:]))
        else:
            if choice == 'Dice':
                self.roll_dice()
            elif choice == 'Knight':
                for a in self.actions:
                    if hasattr(a, 'knight'):
                        if a.knight:
                            print("Cannot use more than one development card per turn")
                            return
                self.place_robber(knight=True, friendly_robber=FRIENDLY_ROBBER)
            elif choice == 'Undo':
                self.undo()

    def roll_dice(self, mock=None):
        if mock:
            self.board.dice = mock
        else:
            if self.board.dice:
                print("Cannot roll dice more than once")
                return
            self.board.dice = randint(1, 6) + randint(1, 6)
        print("Dice: ", self.board.dice)
        if self.board.dice == 7:
            self.place_robber(friendly_robber=FRIENDLY_ROBBER)
        else:
            self.check_profits()

    def check_profits(self):
        for t in self.board.tiles:
            if self.board.dice is t.number:
                if not t.blocked:
                    for s in t.buildings:
                        if s.owner is not None:
                            print("Player #{player} has gained {cards} {resource} from settelment {sett}".format(
                                player=s.owner.player_id,
                                cards=2 if s.city else 1,
                                resource=t.resource,
                                sett=s.settelment_id
                            ))

    def build_road(self, road_id, sett=None):
        road = self.board.roads[road_id]
        if self.current_player.roads > 0:
            if sett:
                if not self.road_spot_available(road, self.board.settelments[sett]):
                    print("Spot not available!")
                    return False
            else:
                if not self.road_spot_available(road):
                    print("Spot not available!")
                    return False
        else:
            raise Exception("Player {} has no roads left to build".format(self.current_player.player_id))
        action = BuildRoadAction(self.board, self.current_player, road)
        self.actions.append(action)
        action.do()
        return True

    def road_spot_available(self, road, pregame_sett=None):
        if road.available:
            if pregame_sett:
                if pregame_sett.owner is self.current_player:
                    for r in pregame_sett.neighbour_roads:
                        if r is road:
                            return True
            else:
                for sett in road.neighbour_settelments:
                    if sett.owner is self.current_player:
                        return True
                    elif sett.owner is None:
                        for r in sett.neighbour_roads:
                            if r is road:
                                continue
                            if r.owner is self.current_player:
                                return True
        return False

    def build_settelment(self, sett_id, first=False):
        sett = self.board.settelments[sett_id]
        if not self.sett_spot_available(sett, first):
            print("Cannot build on a settelment on", sett_id)
            return False
        action = BuildSettelmentAction(self.board, self.current_player, sett)
        self.actions.append(action)
        if action.do():
            return True

    def sett_spot_available(self, sett, first):
        if sett.available:
            if first:
                return True
            else:
                for road in sett.neighbour_roads:
                    if road.owner is self.current_player:
                        return True
        return False

    def upgrade_settelment(self, settelment_id):
        sett = self.board.settelments[settelment_id]
        if sett.owner is not self.current_player:
            print("Cannot build on a city on", sett.settelment_id)
            return False
        action = BuildCityAction(self.board, self.current_player, sett)
        self.actions.append(action)
        if action.do():
            return True

    def place_robber(self, knight=False, friendly_robber=False):
        while True:
            tile_id = int(input("Which tile would you like to block: "))
            if tile_id not in list(range(0, 19)):
                print("Invalid tile number")
            else:
                if tile_id is self.board.current_blocked:
                    print("The robber cannot remain on the same tile")
                else:
                    if friendly_robber:
                        if self.friendly_robber(tile_id):
                            break
                        else:
                            print("Cannot rob a spot belongs to a player that has less then 3 points")
                    else:
                        break
        if knight:
            action = PlaceRobberAction(self.board, self.current_player, tile_id, knight)
        else:
            action = PlaceRobberAction(self.board, self.current_player, tile_id)
        self.actions.append(action)
        if action.do():
            return True

    def friendly_robber(self, tile_id):
        if self.board.tiles[tile_id].resource == 'Desert':
            return True
        ok = []
        for s in self.board.tiles[tile_id].buildings:
            if s.owner:
                if s.owner.points > 2:
                    ok.append(True)
                else:
                    ok.append(False)
        if all(ok):
            return True
        return False

    def count_longest_road(self):
        pass

    def undo(self):
        if len(self.actions) == 0:
            return False
        last_action = self.actions[-1]
        last_action.undo()
        self.actions.remove(last_action)
