from random import randrange, randint

from ..game_config import FRIENDLY_ROBBER, MOCK_UP
from .. import globals
from . import actions


class Turn(object):
    def __init__(self, board, current_player):
        self.board = board
        self.current_player = current_player
        self.actions = []
        self.roll = None

    def pregame_player_action(self, mock_up=False):
        # Undo == 666
        # End turn == 777
        self.actions = []
        built_sett = False
        built_road = False
        done_turn = False
        while not built_sett:
            if mock_up == 'random':
                choice_sett = randrange(54)
                while not self.build_settlement(choice_sett, first=True, pay=False, silent=True):
                    choice_sett = randrange(54)
                break
            elif mock_up:
                choice_sett = MOCK_UP[0]
                self.current_player.announce("{}, where would you like to place a settlement: {}".format(
                    self.current_player.color.capitalize(), MOCK_UP[0]))
                del MOCK_UP[0]
                if self.build_settlement(choice_sett, first=True, pay=False):
                    break
            choice_sett = self.current_player.choose_settlement_placement()
            if choice_sett == 'undo':
                if len(self.actions) > 0:
                    self.undo()
                    return False
                else:
                    print("Nothing to Undo")
            else:
                if self.build_settlement(choice_sett, first=True, pay=False):
                    built_sett = True
        while not built_road:
            if mock_up == 'random':
                choice_road = randrange(72)
                while not self.build_road(choice_road, choice_sett, pay=False, silent=True):
                    choice_road = randrange(72)
                break
            elif mock_up:
                choice_road = MOCK_UP[0]
                print("{}, where would you like to place a road: {}".format(
                    self.current_player.color.capitalize(), MOCK_UP[0]))
                del MOCK_UP[0]
                if self.build_road(choice_road, choice_sett, pay=False):
                    break
            choice_road = self.current_player.choose_road_placement()
            if choice_road == 'undo':
                if len(self.actions) > 0:
                    self.undo()
                    self.undo()
                    return False
                else:
                    print("Nothing to Undo")
                print("Invalid input, try again")
            else:
                if self.build_road(choice_road, choice_sett, pay=False):
                    built_road = True
        return True

    def player_action(self):
        self.roll = actions.RollAction(self.board, self.current_player)
        self.roll.do()
        from pprint import pprint
        pprint(self.current_player.possible_actions())
        while True:
            current = self.current_player
            resources = ', '.join(['{}*{}'.format(c, r) for r, c in current.resource_cards.items() if c])
            if resources:
                current.announce("{}'s resources: {}".format(current.color.capitalize(), resources))
            else:
                current.announce("{} has no resources right now".format(current.color.capitalize()))
            dev_strs = [x.card_type for x in current.dev_cards]
            dev_cards = ', '.join(['{}*{}'.format(dev_strs.count(x), x.replace('_', ' ')) for x in set(dev_strs)])
            if dev_cards:
                current.announce("{}'s development cards: {}".format(current.color.capitalize(), dev_cards))
            choice = current.choose_action()
            if choice == "end":
                break
            self.parse_action(choice)
        return True

    def parse_action(self, choice):
        if choice == 'pdb':
            pl = self.current_player
            pl.available_settlements()
            import pdb; pdb.set_trace()
        elif choice.startswith("t"):
            try:
                i = choice.index(':')
                count = int(choice[1])
                old = choice[2:i]
                new = choice[i+1:]
            except (ValueError, IndexError):
                self.current_player.announce('Trades must be formated as "t<#><old>:<new>", i.e. "t3wood:sheep"')
                return
            action = actions.TradeAction(self.board, self.current_player, count, old, new)
            if action.do():
                self.actions.append(action)
            return
        elif choice.startswith("r"):
            self.build_road(int(choice[1:]))
        elif choice.startswith("s"):
            if self.board.settlements[int(choice[1:])].owner is self.current_player:
                if not self.board.settlements[int(choice[1:])].city:
                    self.upgrade_settlement(int(choice[1:]))
                else:
                    self.current_player.announce("Cannot upgrade. It is already a city")
                    return
            else:
                self.build_settlement(int(choice[1:]))
        # temporary hack: enter "D" and the number you wish to score
        elif choice.startswith("D"):
            self.roll_dice(int(choice[1:]))
        elif choice == 'dice':
            self.roll_dice()
        elif choice.startswith('dice='):
            self.roll_dice(mock=choice[5:])
        elif choice == 'buy dc':
            self.buy_dc()
        elif choice == 'knight':
            for a in self.actions:
                if hasattr(a, 'knight'):
                    if a.knight:
                        self.current_player.announce("Cannot use more than one development card per turn")
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
                self.current_player.announce("Cannot use more than one development card per turn")
                return
            if not self.verify_player_holds_dc("build_roads"):
                self.current_player.announce("{} doesn't hold Build Road card".format(self.current_player.color.capitalize()))
                return
            else:
                self.build_roads()
        # TODO
        elif choice == "plenty":
            self.plenty()

    def roll_dice(self, mock=None):
        if mock:
            self.board.dice = int(mock)
        else:
            if self.board.dice:
                self.current_player.announce("Cannot roll dice more than once")
                return
            self.board.dice = randint(1, 6) + randint(1, 6)
        self.current_player.announce("Dice: {}".format(self.board.dice))
        if self.board.dice == 7:
            self.place_robber(friendly_robber=FRIENDLY_ROBBER)
        else:
            self.check_profits()

    #TODO Gather profits by the players sitting order
    def check_profits(self):
        for t in self.board.tiles:
            if self.board.dice is t.number:
                if not t.blocked:
                    for s in t.buildings:
                        if s.owner is not None:
                            cards = 2 if s.city else 1
                            self.current_player.announce("{player} has gained {cards} {resource} from settlement {sett}".format(
                                player=s.owner.color.capitalize(),
                                cards=2 if s.city else 1,
                                resource=t.resource,
                                sett=s.settlement_id
                            ))
                            cards = self.board.cards_deck.give(t.resource.lower(), 2 if s.city else 1)
                            s.owner.resource_cards[t.resource.lower()] += 2 if s.city else 1

    def buy_dc(self, pay=True):
        # buy Development Card
        if len(self.board.dev_cards) > 0:
            action = actions.BuyDCAction(self.board, self.current_player, pay=pay)
            if action.do():
                self.actions.append(action)
                return True
            return False
        else:
            self.current_player.announce("No Development Cards left in deck")

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

    def build_road(self, road_id, sett=None, pay=True, silent=False):
        road = self.board.roads[road_id]
        if self.current_player.roads > 0:
            if sett is not None:
                if not self.road_spot_available(road, self.board.settlements[sett]):
                    if not silent:
                        self.current_player.announce("Spot not available!")
                    return False
            else:
                if not self.road_spot_available(road):
                    if not silent:
                        self.current_player.announce("Spot not available!")
                    return False
        else:
            raise Exception("{} has no roads left to build".format(self.current_player.color.capitalize()))
        action = actions.BuildRoadAction(self.board, self.current_player, road, pay=pay)
        if action.do():
            self.actions.append(action)
            return True
        return False

    def road_spot_available(self, road, pregame_sett=None):
        if road.available:
            if pregame_sett is not None:
                if pregame_sett.owner is self.current_player:
                    for r in pregame_sett.neighbor_roads:
                        if r is road:
                            return True
            else:
                for sett in road.neighbor_settlements:
                    if sett.owner is self.current_player:
                        return True
                    elif sett.owner is None:
                        for r in sett.neighbor_roads:
                            if r is road:
                                continue
                            if r.owner is self.current_player:
                                return True
        return False

    def build_settlement(self, sett_id, first=False, pay=True, silent=False):
        sett = self.board.settlements[sett_id]
        if not self.sett_spot_available(sett, first):
            if not silent:
                self.current_player.announce("Cannot build on a settlement on", sett_id)
            return False
        action = actions.BuildSettelmentAction(self.board, self.current_player, sett, pay=pay)
        if action.do():
            self.actions.append(action)
            return True
        return False

    def sett_spot_available(self, sett, first):
        if sett.available:
            if first:
                return True
            else:
                for road in sett.neighbor_roads:
                    if road.owner is self.current_player:
                        return True
        return False

    def upgrade_settlement(self, settlement_id, pay=True):
        sett = self.board.settlements[settlement_id]
        if sett.owner is not self.current_player:
            self.current_player.announce("Cannot build on a city on", sett.settlement_id)
            return False
        action = actions.BuildCityAction(self.board, self.current_player, sett, pay=pay)
        self.actions.append(action)
        if action.do():
            self.actions.append(action)
            return True
        return False

    def place_robber(self, knight=False, friendly_robber=False):
        while True:
            tile_id = int(input("Which tile would you like to block (0-18): "))
            if tile_id not in list(range(0, 19)):
                self.current_player.announce("Invalid tile number")
            else:
                if tile_id is self.board.current_blocked:
                    self.current_player.announce("The robber cannot remain on the same tile")
                else:
                    if friendly_robber:
                        if self.friendly_robber(tile_id):
                            break
                        else:
                            self.current_player.announce("Cannot rob a spot belongs to a player that has less then 3 points")
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

    def undo_turn(self):
        while len(self.actions) > 0:
            self.undo()
        self.roll.undo()

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
            self.current_player.announce("Build Roads Development Card - Road {}/2:".format(roads_built + 1))
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
                    if self.build_road(int(choice[1:]), pay=False):
                        roads_built += 1
                        break
                else:
                    self.current_player.announce("Wrong input. To end the turn type: 'end'")
            if choice == "end":
                return False
            if roads_built == 2:
                break
        self.current_player.announce("Finished playing the Build Roads Development Card")
        action = actions.BuildRoadsDCAction(self.board, self.current_player, roads_built)
        self.actions.append(action)
        if action.do():
            return True

    def plenty(self):
        # year of plenty Development Card
        pass

    def count_longest_road(self):
        pass
