from random import randint
import re
import logging


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
            logging.info("Player #{} has built road {}".format(player.player_id, road_id))
            self.done = True

        def undo():
            if self.done:
                road.owner = None
                road.available = True
                player.roads_built.remove(road)
                player.roads += 1
                logging.info("Player #{} undid the road {}".format(player.player_id, road_id))

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
            logging.info("Player #{} built a settelment on {}".format(self.current_player.player_id, sett.settelment_id))

        def undo():
            if self.done:
                sett.available = True
                sett.owner = None
                del self.current_player.settlements_built[-1]
                for s in sett.neighbours:
                    s.available = True
                self.current_player.points -= 1
                self.current_player.settlements += 1
                logging.info("Player #{} undid the settelment on {}".format(self.current_player.player_id, sett.settelment_id))

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
            logging.info("Player #{} built a city on {}".format(self.current_player.player_id, sett.settelment_id))

        def undo():
            if self.done:
                self.current_player.settlements_built.append(sett)
                self.current_player.cities_built.remove(sett)
                self.current_player.points -= 1
                self.current_player.cities += 1
                self.current_player.settlements -= 1
                sett.settelment = True
                sett.city = False
                logging.info("Player #{} undid the city on {}".format(self.current_player.player_id, sett.settelment_id))

        super().__init__(do, undo)


class Turn(object):
    def __init__(self, board, current_player):
        self.board = board
        self.current_player = current_player
        self.dice = None
        self.actions = []

    def player_action(self):
        """
        dice
        road
        settelment
            city
        knight
        undo
        end turn
        :return: 
        """
        def road():
            road_id = input("Enter the road id you would like to build: ")
            self.build_road(road_id)

        def sett():
            sett_id = input("Enter the settelment id you would like to build: ")
            if self.board.settelments[sett_id].owner is self.current_player:
                self.upgrade_settelment(sett_id)
            else:
                self.build_settelment(sett_id)

        options = {
            'dice': self.roll_dice(),
            'road': road(),
            'sett': sett(),
            'knight': 1,
            'undo': self.undo(),
            'end': self.end_turn()
        }
        choice = input("Player #{}, what would you like to do: ".format(self.current_player.player_id))
        options[choice]

    def end_turn(self):
        """
        Sums up players points and if >= 10 game ends
        :return: 
        """
        # self.count_longest_road()
        if self.current_player.points >= 10:
            return False
        else:
            self.player_turn(self.current_player.next_player)

    def roll_dice(self):
        """
        Rolls the dice and calls check_profits()
        :return: 
        """
        self.dice = randint(1, 6) + randint(1, 6)
        print("Dice: ", self.dice)
        self.check_profits()

    def check_profits(self):
        """
        Each players gain resources if not blocked by the robber
        :return: 
        """
        for t in self.board.tiles:
            if self.dice is t.number:
                if not t.blocked:
                    for s in t.buildings:
                        if s.owner is not None:
                            logging.info("Player #{player} has gained {cards} {resource}".format(
                                player=s.owner.player_id,
                                cards=2 if s.city else 1,
                                resource=t.resource
                            ))

    def build_road(self, road_id):
        road = self.board.roads[road_id]
        if self.current_player.roads > 0:
            if not self.road_spot_available(road):
                raise Exception("Spot not available!")
        else:
            raise Exception("Player {} has no roads left to build".format(self.current_player.player_id))
        action = BuildRoadAction(self.board, self.current_player, road)
        self.actions += action
        action.do()

    def road_spot_available(self, road):
        if road.available:
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
            logging.info("Cannot build on a settelment on", sett_id)
        action = BuildSettelmentAction(self.board, self.current_player, sett)
        self.actions += action
        action.do()

    def sett_spot_available(self, sett, first):
        if sett.available:
            if all(sett.neighbours.available):
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
            logging.info("Cannot build on a city on", sett.settelment_id)
        action = BuildCityAction(self.board, self.current_player, sett)
        self.actions += action
        action.do()

    def place_robber(self, tile_id):
        self.board.move_robber(tile_id)

    def use_knight(self, tile_id):
        self.board.move_robber(tile_id)
        self.current_player.knights += 1
        self.current_player.points += 1

    def count_longest_road(self):
        pass

    def undo(self):
        last_action = self.actions[-1]
        last_action.undo()
        self.actions.remove(last_action)
