from random import shuffle


class Action(object):
    def __init__(self, do=lambda: True, undo=lambda: True):
        self.do = do
        self.undo = undo

class PayAction(Action):
    costs = {'development card': {'sheep': 1, 'ore': 1, 'grain': 1},
             'settlement':       {'sheep': 1, 'brick': 1, 'grain': 1, 'wood': 1},
             'city':             {'grain': 2, 'ore': 3},
             'road':             {'brick': 1, 'wood': 1}}

    def __init__(self, item, player):
        self.done = False
        self.item = item
        self.player = player

        def do():
            cost = self.costs[item]
            missing = {}
            for resource, count in cost.items():
                if player.resource_cards[resource] < count:
                    missing[resource] = count - player.resource_cards[resource]
            if missing:
                cost = ', '.join(['{}*{}'.format(c, r) for r, c in cost.items()])
                missing = ', '.join(['{}*{}'.format(c, r) for r, c in missing.items()])
                print('Resources not available for a {}: it costs {}'.format(item, cost))
                print('You are missing: {}'.format(missing))
                return False
            for resource, count in cost.items():
                player.resource_cards[resource] -= count
            self.done = True
            return True

        def undo():
            if not self.done:
                return False
            for resource, count in self.costs[item]:
                player.resource_cards[resource] += count
            return True

        super().__init__(do, undo)

class BuildRoadAction(Action):
    def __init__(self, board, player, road, pay=False):
        self.done = False
        self.board = board
        self.current_player = player
        if pay:
            payment = PayAction('road', player)
        else:
            payment = Action()

        def do():
            if not payment.do():
                return False
            road.owner = player
            road.available = False
            player.roads_built.append(road)
            player.roads -= 1
            print("{} has built road {}".format(player.color.capitalize(), road.road_id))
            self.done = True
            return True

        def undo():
            if self.done:
                if not payment.undo():
                    return False
                road.owner = None
                road.available = True
                player.roads_built.remove(road)
                player.roads += 1
                print("{} undid the road {}".format(player.color.capitalize(), road.road_id))
                return True

        super().__init__(do, undo)


class BuildSettelmentAction(Action):
    def __init__(self, board, player, sett, pay=False):
        self.done = False
        self.board = board
        self.current_player = player
        if pay:
            payment = PayAction('settlement', player)
        else:
            payment = Action()

        def do():
            if not payment.do():
                return False
            sett.available = False
            sett.owner = self.current_player
            self.current_player.settlements_built.append(sett)
            for s in sett.neighbours:
                s.available = False
            self.current_player.points += 1
            self.current_player.settlements -= 1
            self.done = True
            print("{} built a settelment on {}".format(self.current_player.color.capitalize(), sett.settelment_id))
            return True

        def undo():
            if self.done:
                if not payment.undo():
                    return False
                sett.available = True
                sett.owner = None
                del self.current_player.settlements_built[-1]
                for s in sett.neighbours:
                    s.available = True
                self.current_player.points -= 1
                self.current_player.settlements += 1
                print("{} undid the settelment on {}".format(self.current_player.color.capitalize(), sett.settelment_id))
                return True
            return False

        super().__init__(do, undo)


class BuildCityAction(Action):
    def __init__(self, board, player, sett, pay=False):
        self.done = False
        self.board = board
        self.current_player = player
        if pay:
            payment = PayAction('city', player)
        else:
            payment = Action()

        def do():
            if not payment.do():
                return False
            self.current_player.settlements_built.remove(sett)
            self.current_player.cities_built.append(sett)
            self.current_player.points += 1
            self.current_player.cities -= 1
            self.current_player.settlements += 1
            sett.settelment = False
            sett.city = True
            self.done = True
            print("{} built a city on {}".format(self.current_player.color.capitalize(), sett.settelment_id))
            return True

        def undo():
            if self.done:
                if not payment.undo():
                    return False
                self.current_player.settlements_built.append(sett)
                self.current_player.cities_built.remove(sett)
                self.current_player.points -= 1
                self.current_player.cities += 1
                self.current_player.settlements -= 1
                sett.settelment = True
                sett.city = False
                print("{} undid the city on {}".format(self.current_player.color.capitalize(), sett.settelment_id))
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
            print("{} placed the robber on tile {}: The number {} and resource {}".format(
                self.current_player.color.capitalize(),
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
                print("{} undid the robber on tile {}".format(
                    self.current_player.color.capitalize(), self.board.tiles[tile_id].tile_id))
                print("Robber moved back to tile {}: The number {} and resource {}".format(
                    self.board.tiles[self.board.previous_blocked].tile_id,
                    self.board.tiles[self.board.previous_blocked].number,
                    self.board.tiles[self.board.previous_blocked].resource))
                if knight:
                    self.current_player.knights -= 1
                return True

        super().__init__(do, undo)


class BuyDCAction(Action):
    def __init__(self, board, player, pay=False):
        self.done = False
        self.board = board
        self.current_player = player
        self.card = self.board.dev_cards[0]
        if pay:
            payment = PayAction('development card', player)
        else:
            payment = Action()

        def do():
            if not payment.do():
                return False
            self.current_player.dev_cards.append(self.card)
            self.board.dev_cards.remove(self.card)
            print("{} bought a Development Card and it's {}".format(
                self.current_player.color.capitalize(),
                self.card.card_type)
            )
            self.done = True
            return True

        def undo():
            if self.done:
                if not payment.undo():
                    return False
                self.card = self.current_player.dev_cards[len(self.current_player.dev_cards)-1]
                self.board.dev_cards.append(self.card)
                self.current_player.dev_cards.remove(self.card)
                shuffle(self.board.dev_cards)
                return True

        super().__init__(do, undo)


class BuildRoadsDCAction(Action):
    def __init__(self, board, player, step):
        self.done = False
        self.board = board
        self.current_player = player
        self.step = step
        self.card_type = "build_roads"

        def do():
            if self.step == 1:
                self.done = True
                return True
            for card in self.current_player.dev_cards:
                if card.card_type == self.card_type and card.already_used is False:
                    print("DEBUG: marked card as used")
                    card.used()
                    break
            self.done = True
            return True

        def undo():
            if self.done:
                for card in self.current_player.dev_cards:
                    if card.card_type == self.card_type and card.already_used is True:
                        print("DEBUG: undo - marked card as unused")
                        card.already_used = False
                        break
                return True

        super().__init__(do, undo)
