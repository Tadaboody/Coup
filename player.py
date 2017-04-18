from card import Card
import actions
from random import randint
import random
import copy
from abc import abstractmethod, ABCMeta
from fractions import Fraction


class Player():  # TODO: make an abstract player class
    __metaclass__ = ABCMeta

    def __init__(self, num=2, coins=2):
        self.strategy = "None"
        self.playing = True
        self.hand = list()
        self.hand_size = 0
        self.coins = coins
        self.num = num
        self.possible_actions = (
            actions.Income(self),
            actions.Steal(self),
            actions.ForeignAid(self),
            actions.Coup(self),
            actions.Assassinate(self),
            actions.Tax(self),
            # actions.Exchange(self)
        )
        self._game = None

    @property
    def game(self):
        return self._game

    @game.setter
    def game(self, value):
        # for name, action in self.possible_actions.iteritems():
        for action in self.possible_actions:
            action.game = value
        self._game = value

    def __repr__(self):
        """overloading the print function"""
        return "P{}\n" \
               "Coins:{}\n" \
               "Hand:{}".format(self.num, self.coins, self.hand)

    def __str__(self):
        return "P{}\n" \
               "Coins:{}\n" \
               "Hand size:{}".format(self.num, self.coins, len(self.hand))

    def take_turn(self, callback):
        self.pick_action(callback)

    def draw_card(self, card):
        self.hand.append(card)
        self.hand_size += 1

    @abstractmethod
    def pick_action(self, callback):
        pass

    @abstractmethod
    def pick_target(self, callback, action):
        pass

    @abstractmethod
    def inspect_action(self, action, callback):
        pass

    @abstractmethod
    def pick_card(self, callback):
        pass

    @abstractmethod
    def stop_action(self, callback, action):
        pass

    def return_cards(self, callback):
        if callback is not None:
            self.return_callback = callback
        if len(self.hand) > self.hand_size:
            self.pick_card(self.pick_card_callback)
        else:
            self.return_callback(self.picked)

    def pick_card_callback(self, card):
        self.hand.remove(card)
        self.picked.append(card)
        self.return_cards(None)

    def discard_card(self, callback):
        self.hand_size -= 1
        self.picked = list()
        self.return_cards(callback)

    # def swap_cards(self, drawn_cards, callback):
    #     self.hand = self.hand + drawn_cards
    #     self.picked = list()
    #     self.pick_card(callback)

    def think_about_turn(self, turn):
        pass

    def start_thinking(self):
        pass


class HumanPlayer(Player):
    def __init__(self, num=3, coins=2):
        super(HumanPlayer, self).__init__(num, coins)
        self.strategy = "Human"

    def pick_target(self, callback, action):
        players_copy = copy.copy(self.game.players)
        players_copy.remove(self)
        self.pick_item(players_copy, "Pick a target", callback)

    def pick_action(self, callback):
        self.pick_item(self.possible_actions, "Pick an action {}".format(self.__repr__()), callback)

    def inspect_action(self, action, callback):
        self.pick_item((True, False), "Player {} - Inspect {}?".format(self.__repr__(), action.name), callback)

    def stop_action(self, callback, action):
        self.pick_item((True, False), "Player {} - Stop {}?".format(self.num, action), callback)

    def pick_card(self, callback):
        self.pick_item(self.hand, "Player {} pick a card".format(self.num), callback, pop=True)

    def pick_item(self, items, message, callback, pop=False):
        print message
        if pop:
            callback(items.pop(input(items)))
        else:
            callback(items[input(items)])


class RandomAI(Player):
    def __init__(self, num=3, coins=2):
        Player.__init__(self, num, coins)
        self.strategy = "Random"

    def pick_action(self, callback):
        # act = random.choice(self.possible_actions.values())  # needs to be a dict - not polymorphic :(
        valid_actions = list()
        for action in self.possible_actions:
            if action.is_valid():
                valid_actions.append(action)
        act = random.choice(valid_actions)
        callback(act)

    def stop_action(self, callback, action):
        callback(bool(randint(0, 1)))

    def pick_target(self, callback, action):
        # return game.players[input("who {}".format(len(game.players) - 1))]
        if isinstance(action, actions.Coup):
            self.pick_coup_target(callback)
        elif isinstance(action, actions.Steal):
            self.pick_steal_target(callback)

    def inspect_action(self, action, callback):
        callback(bool(randint(0, 1)))

    def pick_card(self, callback):
        card = random.choice(self.hand)
        callback(card)

    def pick_coup_target(self, callback):
        players_copy = copy.copy(self.game.players)
        if self in players_copy:
            players_copy.remove(self)  # dont pick yourself
        if players_copy:
            target = random.choice(players_copy)
            callback(target)
        else:
            self.game.game_over()

    def pick_steal_target(self, callback):
        steal_targets = list()
        for player in self.game.players:
            if player.coins >= 2:
                steal_targets.append(player)
        if steal_targets:
            callback(random.choice(steal_targets))
        else:
            callback(self)


class ThinkingAI(Player):
    doubt_const = 0.5
    sure_const = 3
    saftey_const = 0.3
    fear_from_stop = 0.5
    heuristic_value = {"Coup": 3.5, "Assassinate": 3, "Steal": 2.5, "Tax": 2, "Foreign aid": 1.5, "Income": 1}

    def __init__(self, num=3, coins=2):
        super(ThinkingAI, self).__init__(num, coins)
        self.strategy = "Thinking"
        self.other_players = dict()
        self.current_action = None

    def stop_action(self, callback, action):
        callback(action.stopper_card in self.hand)

    def pick_target(self, callback, action):
        if isinstance(action, actions.Coup):
            self.pick_coup_target(callback)
        elif isinstance(action, actions.Steal):
            self.pick_steal_target(callback)

    def pick_action(self, callback):
        """Picks the action with the highest heuristic value"""
        heuristic = list()
        self.game.output("Calculating chances of success")
        for x in self.possible_actions:
            heuristic.append((self.action_heuristic_func(x), x))

        callback(max(heuristic, key=lambda x: x[0])[1])
        # if self.coins >= 7:
        #     callback(self.find_action_by_name('coup'))
        # if Card('captain') in self.hand:
        #     callback(self.find_action_by_name('steal'))

    def action_heuristic_func(self, action):
        """
        :type action: actions.Action
        """
        return_value = self.heuristic_value[action.name.capitalize()] * action.is_valid()
        if action.enabler_card and action.enabler_card not in self.hand:
            return_value -= max(
                self.card_chance_diff(player, action.enabler_card) for player in self.game.players if player != self)
        if action.stopper_card:
            return_value -= max(self.card_chance_diff(player, action.stopper_card) for player in self.game.players if
                                player != self) * self.fear_from_stop
        self.game.output(str(action) + str(return_value))
        return return_value
        # if action.enabler_card: :really cool "one line" version:
        #     return self.heuristic_value[action.name.capitalize()] * \
        #            action.is_valid() - \
        #            (action.enabler_card not in self.hand) * \
        #            max(self.card_chance_diff(player, action.enabler_card) for player in self.game.players if
        #                player != self) \
        #            - (action.stopper_card is not None) * \
        #              max(self.card_chance_diff(player, action.stopper_card) for player in self.game.players if
        #                  player != self) * self.fear_from_stop

    def pick_card(self, callback):
        # choose_from = self.hand
        # choice = random.choice(self.hand)
        # if self.coins >= 3 and choice.name is 'Assassinate':
        #     choose_from = (x for x in choose_from if x.name != 'Assassinate')
        # if choose_from:
        #     callback(random.choice((x for x in choose_from if x.name != 'Assassinate')))
        # else:
        callback(random.choice(self.hand))

    def inspect_action(self, action, callback):
        self.game.output("Chances he can't {} {}".format(str(action),str(self.card_chance_diff(action.executor, action.enabler_card))))
        callback(self.card_chance_diff(action.executor, action.enabler_card) > self.doubt_const)

    def think_about_turn(self, turn):
        self.think_about_action(turn.main_action, turn)

    def think_about_action(self, action, turn):
        """Adds new data from the last action and turn"""
        current_player = action.executor
        enabler_card = action.enabler_card
        if not action.enabler_card:
            enabler_card = Card(0)
        if current_player is not self:
            if action.inspected and not action.canceled:
                self.other_players[current_player][enabler_card] = 1
                self.card_discovered(enabler_card)
            if not (action.canceled or action.stopped):  # if the action was succsessfully done
                self.other_players[current_player][enabler_card] *= self.sure_const
            if action.canceled:
                self.other_players[current_player][enabler_card] = 0
                self.card_discovered()
                if self.game.inspecting_player is not self:
                    self.other_players[self.game.inspecting_player][enabler_card] *= self.sure_const
            if action.stopped:
                self.think_about_action(turn.stopping_action, turn)

    # def is_safe_card(self, card_name):
    #     card = Card(card_name)
    #     if card in self.hand:
    #         return True
    #     for player in self.game.players:  # check if there isnt a big chance someone else has the card
    #         pass

    def card_chance_diff(self, player, card):
        if (not card) or player is self:
            return 0
        safe_copy = copy.deepcopy(self.other_players[player])
        chance_of_card = safe_copy[card]
        del safe_copy[card]
        # diff_list = ((chance_of_card * inverse_fraction(x), x) for x in safe_copy.values())
        diff_list = (chance_of_card * inverse_fraction(x) for x in safe_copy.values())
        # return max(diff_list, key=lambda x: x[0])
        re_val = max(diff_list)
        # print "max is " + str(re_val)
        return re_val

    # def draw_card(self, card): # i'd use this to update the player_dict, but I don't know the rest of the players are
    # initialized at this point
    #     super(ThinkingAI, self).draw_card(card)

    def start_thinking(self):
        self.init_player_dict()

    def init_player_dict(self):
        for player in self.game.players:
            if player is not self:
                self.other_players[player] = dict()
                self.other_players[player][Card(0)] = 0  # cant have a "none" card
                for i in xrange(1, Card.num_of_types):
                    # starting probability for having a certain type - amount of cards from a type/total cards
                    self.other_players[player][Card(i)] = Fraction(self.game.amount_of_each_card,
                                                                   (self.game.amount_of_each_card * (Card.num_of_types - 1)) - 2)
                for card in self.hand:
                    self.other_players[player][card] = Fraction(
                        self.other_players[player][card].numerator - 1, self.other_players[player][card].denominator)

    def pick_steal_target(self, callback=None):
        """Picks the player with the most coins"""
        players_copy = copy.copy(self.game.players)
        players_copy.remove(self)  # don't pick yourself!
        wealthy_player = max(self.game.players, key=lambda x: x.coins)
        callback(wealthy_player)

    def find_action_by_name(self, name):  # because I dont want possible actions to be a dictionary- it fucks stuff up
        """helper function to select a action by name"""
        return next(x for x in self.possible_actions if name.lower() == x.name.lower())

    def pick_coup_target(self, callback):
        """eh random for now"""
        players_copy = copy.copy(self.game.players)
        if self in players_copy:
            players_copy.remove(self)  # dont pick yourself
        if players_copy:
            target = random.choice(players_copy)
            callback(target)
        else:
            self.game.game_over()

    def card_discovered(self, card=None):
        pass
        # """reduces the odds of players having a certain card if that card is discovered, or if a player is discovered not to have a certain card"""
        # for player_dict in self.other_players.values():
        #     for card_chances in player_dict.keys():
        #         if player_dict[card_chances] is not 1 or player_dict[card_chances] is not 0:
        #             player_dict[card_chances] = reduce_denominator(player_dict[card_chances], 1)


def reduce_numerator(fraction, amount):
    return Fraction(fraction.numerator - amount, fraction.denominator)


def reduce_denominator(fraction, amount):
    try:
        return Fraction(fraction.numerator, fraction.denominator - amount)
    except ZeroDivisionError:
        return 0


def inverse_fraction(fraction):
    try:
        return Fraction(fraction.denominator, fraction.numerator)
    except ZeroDivisionError:
        return Fraction(0, 1)
