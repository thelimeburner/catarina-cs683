from random import shuffle, randint

class Action(object):
    def __init__(self, do=lambda: True, undo=lambda: True):
        self.do = do
        self.undo = undo

class RollAction(Action):
    def __init__(self, board, player, roll=None):
        self.board = board
        self.player = player
        self.roll = roll
        if not roll or roll not in list(range(2, 12)):
            self.roll = randint(1, 6) + randint(1, 6)
        self.robber_action = None
        self.cards_gained = {}

        def do():
            self.board.dice = self.roll
            self.player.announce('Dice: {}'.format(self.roll))
            if self.board.dice == 7:
                while True:
                    tile_id = self.player.choose_robber_placement()
                    if tile_id is self.board.current_blocked:
                        self.player.announce("The robber cannot remain on the same tile")
                    else:
                        break
                action = PlaceRobberAction(self.board, self.player, tile_id)
                if action.do():
                    self.robber_action = action
                return True
            else:
                for t in self.board.tiles:
                    if self.board.dice is t.number and not t.blocked:
                        for s in t.buildings:
                            if s.owner is not None:
                                cards = 2 if s.city else 1
                                self.player.announce("{player} has gained {cards} {resource} from settlement {sett}".format(
                                    player=s.owner.color.capitalize(),
                                    cards=2 if s.city else 1,
                                    resource=t.resource,
                                    sett=s.settlement_id
                                ))
                                cards = self.board.cards_deck.give(t.resource.lower(), 2 if s.city else 1)
                                self.cards_gained[s.owner] = self.cards_gained.get(s.owner, {
                                    "brick": 0,
                                    "wood": 0,
                                    "grain": 0,
                                    "sheep": 0,
                                    "ore": 0
                                })
                                self.cards_gained[s.owner][t.resource.lower()] += cards
                                s.owner.resource_cards[t.resource.lower()] += cards
                return True

        def undo():
            if self.robber_action:
                return self.robber_action.undo()
            for player, resources in self.cards_gained.items():
                for resource in resources:
                    player.resource_cards[resource] -= resources[resource]
                    self.board.cards_deck.accept(resource, resources[resource])
            return True

        super().__init__(do, undo)

class PayAction(Action):
    costs = {'development card': {'sheep': 1, 'ore': 1, 'grain': 1},
             'settlement':       {'sheep': 1, 'brick': 1, 'grain': 1, 'wood': 1},
             'city':             {'grain': 2, 'ore': 3},
             'road':             {'brick': 1, 'wood': 1}}

    def __init__(self, item, player, board):
        self.done = False
        self.item = item
        self.player = player
        self.resource_deck = board.cards_deck

        def do():
            cost = self.costs[item]
            missing = {}
            for resource, count in cost.items():
                if player.resource_cards[resource] < count:
                    missing[resource] = count - player.resource_cards[resource]
            if missing:
                cost = ', '.join(['{}*{}'.format(c, r) for r, c in cost.items()])
                missing = ', '.join(['{}*{}'.format(c, r) for r, c in missing.items()])
                self.player.announce('Resources not available for a {}: it costs {}'.format(item, cost))
                self.player.announce('You are missing: {}'.format(missing))
                return False
            for resource, count in cost.items():
                player.resource_cards[resource] -= count
                self.resource_deck.accept(resource, count)
            self.done = True
            return True

        def undo():
            if not self.done:
                return False
            for resource, count in self.costs[item].items():
                count = self.resource_deck.give(resource, count)
                player.resource_cards[resource] += count
            return True

        super().__init__(do, undo)

class TradeAction(Action):
    def __init__(self, board, player, count, old, new):
        self.done = False
        self.deck = board.cards_deck
        self.player = player
        self.count = count
        self.old = old
        self.new = new

        def do():
            if self.player.resource_cards[self.old] < self.count:
                self.player.announce("You don't have enough {} to trade.".format(self.old))
                return False
            ports = self.player.ports()
            if self.count == 3 and '3:1' not in ports:
                self.player.announce("You need a 3:1 port to trade at a 3:1 ratio.")
                return False
            if self.count == 2 and self.old not in ports:
                self.player.announce("You need a {r} port to trade {r} at a 2:1 ratio.".format(r=self.old))
                return False
            new_cards = self.deck.give(self.new)
            if not new_cards:
                self.player.announce("There aren't any {} cards left to trade for.".format(self.new))
                return False
            self.deck.accept(self.old, self.count)
            self.player.resource_cards[self.old] -= self.count
            self.player.resource_cards[self.new] += new_cards
            self.player.announce("Trading {} {} for 1 {}.".format(self.count, self.old, self.new))
            self.done = True
            return True

        def undo():
            if not self.done:
                return False
            if not self.player.resource_cards[self.new]:
                self.player.announce("You don't have any {} to give back.".format(self.old))
                return False
            ports = self.player.ports()
            if self.deck.deck[self.old] < self.count:
                self.player.announce("The deck doesn't have enough {} cards left to undo the trade.".format(self.new))
                return False
            new_cards = self.deck.give(self.old, self.count)
            self.deck.accept(self.new)
            self.player.resource_cards[self.old] += new_cards
            self.player.resource_cards[self.new] -= 1
            return True

        super().__init__(do, undo)

class BuildRoadAction(Action):
    def __init__(self, board, player, road, pay=False):
        self.done = False
        self.board = board
        self.current_player = player
        if pay:
            payment = PayAction('road', player, board)
        else:
            payment = Action()

        def do():
            if not payment.do():
                return False
            road.owner = player
            road.available = False
            player.roads_built.append(road)
            player.roads -= 1
            self.current_player.announce("{} has built road {}".format(player.color.capitalize(), road.road_id))
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
                self.current_player.announce("{} undid the road {}".format(player.color.capitalize(), road.road_id))
                return True

        super().__init__(do, undo)


class BuildSettlementAction(Action):
    def __init__(self, board, player, sett, pay=False):
        self.done = False
        self.board = board
        self.current_player = player
        if pay:
            payment = PayAction('settlement', player, board)
        else:
            payment = Action()

        def do():
            if not payment.do():
                return False
            sett.available = False
            sett.owner = self.current_player
            self.current_player.settlements_built.append(sett)
            for s in sett.neighbors:
                s.available = False
            self.current_player.points += 1
            self.current_player.settlements -= 1
            self.done = True
            self.current_player.announce("{} built a settlement on {}".format(self.current_player.color.capitalize(), sett.settlement_id))
            return True

        def undo():
            if self.done:
                if not payment.undo():
                    return False
                sett.available = True
                sett.owner = None
                self.current_player.settlements_built.remove(sett)
                for s in sett.neighbors:
                    s.available = True
                self.current_player.points -= 1
                self.current_player.settlements += 1
                self.current_player.announce("{} undid the settlement on {}".format(self.current_player.color.capitalize(), sett.settlement_id))
                return True
            return False

        super().__init__(do, undo)


class BuildCityAction(Action):
    def __init__(self, board, player, sett, pay=False):
        self.done = False
        self.board = board
        self.current_player = player
        self.sett = sett
        if pay:
            payment = PayAction('city', player, board)
        else:
            payment = Action()

        def do():
            if not payment.do():
                return False
            self.current_player.settlements_built.remove(self.sett)
            self.current_player.cities_built.append(self.sett)
            self.current_player.points += 1
            self.current_player.cities -= 1
            self.current_player.settlements += 1
            self.sett.settlement = False
            self.sett.city = True
            self.done = True
            self.current_player.announce("{} built a city on {}".format(self.current_player.color.capitalize(), self.sett.settlement_id))
            return True

        def undo():
            if self.done:
                if not payment.undo():
                    return False
                self.current_player.settlements_built.append(self.sett)
                self.current_player.cities_built.remove(self.sett)
                self.current_player.points -= 1
                self.current_player.cities += 1
                self.current_player.settlements -= 1
                self.sett.settlement = True
                self.sett.city = False
                self.current_player.announce("{} undid the city on {}".format(self.current_player.color.capitalize(), self.sett.settlement_id))
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
            self.current_player.announce("{} placed the robber on tile {}: The number {} and resource {}".format(
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
                self.current_player.announce("{} undid the robber on tile {}".format(
                    self.current_player.color.capitalize(), self.board.tiles[tile_id].tile_id))
                self.current_player.announce("Robber moved back to tile {}: The number {} and resource {}".format(
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
            payment = PayAction('development card', player, board)
        else:
            payment = Action()

        def do():
            if not payment.do():
                return False
            self.current_player.dev_cards.append(self.card)
            self.board.dev_cards.remove(self.card)
            self.current_player.announce("{} bought a Development Card and it's {}".format(
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
