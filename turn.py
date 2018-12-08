from game_config import FRIENDLY_ROBBER, MOCK_UP
import globals
import actions

from random import randint


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
                print("{}, where would you like to place a settelment: {}".format(
                    self.current_player.color.capitalize(), MOCK_UP[0]))
                del MOCK_UP[0]
                if self.build_settelment(choice_sett, first=True):
                    break
            choice_sett = int(input("{}, where would you like to place a settelment: ".format(
                self.current_player.color.capitalize())))
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
                print("{}, where would you like to place a road: {}".format(
                    self.current_player.color.capitalize(), MOCK_UP[0]))
                del MOCK_UP[0]
                if self.build_road(choice_road, choice_sett):
                    break
            choice_road = int(input("{}, where would you like to place a road: ".format(
                self.current_player.color.capitalize())))
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
            choice_end = int(input("{}, end the turn or undo (777 = end, 666 = undo) ".format(
                self.current_player.color.capitalize())))
            if choice_end == 777:
                done_turn = True
            elif choice_end == 666:
                self.undo()
                self.undo()
                return False
        return True

    def player_action(self):
        while True:
            choice = input("{}, what would you like to do: ".format(self.current_player.color.capitalize()))
            if choice == "end":
                break
            elif choice in globals.CONTROLS:
                self.parse_action(choice)
            else:
                print("Wrong input. To end the turn type: End_Turn")
        return True

    def parse_action(self, choice):
        if choice.startswith("r"):
            self.build_road(int(choice[1:]))
        elif choice.startswith("s"):
            if self.board.settelments[int(choice[1:])].owner is self.current_player:
                if not self.board.settelments[int(choice[1:])].city:
                    self.upgrade_settelment(int(choice[1:]))
                else:
                    print("Cannot upgrade. It is already a city")
                    return
            else:
                self.build_settelment(int(choice[1:]))
        # temporary hack: enter "D" and the number you wish to score
        elif choice.startswith("D"):
            self.roll_dice(int(choice[1:]))
        elif choice == 'dice':
            self.roll_dice()
        elif choice == 'buy dc':
            self.buy_dc()
        elif choice == 'knight':
            for a in self.actions:
                if hasattr(a, 'knight'):
                    if a.knight:
                        print("Cannot use more than one development card per turn")
                        return
            self.place_robber(knight=True, friendly_robber=FRIENDLY_ROBBER)
        elif choice == 'undo':
            self.undo()
        # TODO
        elif choice == "monopoly":
            self.monopoly()
        # TODO
        elif choice == "build roads":
            # using development card - build two roads
            if self.check_used_dev_card():
                print("Cannot use more than one development card per turn")
                return
            if not self.verify_player_holds_dc("build_roads"):
                print("{} doesn't hold Build Road card".format(self.current_player.color.capitalize()))
                return
            else:
                self.build_roads()
        # TODO
        elif choice == "plenty":
            self.plenty()

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
                            print("{player} has gained {cards} {resource} from settelment {sett}".format(
                                player=s.owner.color.capitalize(),
                                cards=2 if s.city else 1,
                                resource=t.resource,
                                sett=s.settelment_id
                            ))

    def buy_dc(self):
        # buy Development Card
        if len(self.board.dev_cards) > 0:
            action = actions.BuyDCAction(self.board, self.current_player)
            self.actions.append(action)
            action.do()
            return True
        else:
            print("No Development Cards left in deck")

    def verify_player_holds_dc(self, card_type):
        # check if the player actually has this Development Card while not already used
        right_cards = []
        for card in self.current_player.dev_cards:
            if card.card_type == card_type:
                right_cards.append(card)
        if next((x for x in right_cards if x.already_used is False), None):
            return True
        return False

    def check_used_dev_card(self):
        for a in self.actions:
            if all(hasattr(a, attr) for attr in ["build_roads", "year_of_plenty", "knight", "monopoly"]):
                return True
        return False

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
            raise Exception("{} has no roads left to build".format(self.current_player.color.capitalize()))
        action = actions.BuildRoadAction(self.board, self.current_player, road)
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
        action = actions.BuildSettelmentAction(self.board, self.current_player, sett)
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
        action = actions.BuildCityAction(self.board, self.current_player, sett)
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
            action = actions.PlaceRobberAction(self.board, self.current_player, tile_id, knight)
        else:
            action = actions.PlaceRobberAction(self.board, self.current_player, tile_id)
        self.actions.append(action)
        if action.do():
            return True

    def undo(self):
        if len(self.actions) == 0:
            return False
        last_action = self.actions[-1]
        last_action.undo()
        self.actions.remove(last_action)

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

    def monopoly(self):
        # monopoly Development Card
        pass

    def build_roads(self):
        roads_built = 0
        while True:
            print("Build Roads Development Card - Road {}/2:".format(roads_built + 1))
            while True:
                action = actions.BuildRoadsDCAction(self.board, self.current_player, roads_built)
                self.actions.append(action)
                if action.do():
                    pass
                choice = input("{}, what road would you like to build: ".format(self.current_player.color.capitalize()))
                if choice == "end":
                    self.undo()
                    break
                elif choice in globals.SPECIFIC_CONTROLS["roads"]:
                    if self.build_road(int(choice[1:])):
                        roads_built += 1
                        break
                else:
                    print("Wrong input. To end the turn type: 'end'")
            if choice == "end":
                return False
            if roads_built == 2:
                break
        print("Finished playing the Build Roads Development Card")
        action = actions.BuildRoadsDCAction(self.board, self.current_player, roads_built)
        self.actions.append(action)
        if action.do():
            return True

    def plenty(self):
        # year of plenty Development Card
        pass

    def count_longest_road(self):
        pass

