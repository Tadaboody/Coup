from card import Card
import actions
from random import randint
import random
import copy
from abc import abstractmethod, ABCMeta


class Player():  # TODO: make an abstract player class
    __metaclass__ = ABCMeta

    def __init__(self, num=2, coins=2):
        self.strategy = "None"
        self.playing = True
        self.hand = list()
        self.hand_size = 0
        self.coins = coins
        self.num = num
        self.possible_actions = {
            'income': actions.Income(self),
            'steal': actions.Steal(self),
            'aid': actions.ForeignAid(self),
            'coup': actions.Coup(self),
            'assassinate': actions.Assassinate(self),
            'tax': actions.Tax(self),
            # 'exchange':actions.Exchange(self)
        }
        self._game = None

    @property
    def game(self):
        return self._game

    @game.setter
    def game(self, value):
        for name, action in self.possible_actions.iteritems():
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

    # @property
    # def num(self):
    #     return self._num
    #
    # @num.setter
    # def num(self, value):
    #     self._num = value

    def take_turn(self, callback):
        self.pick_action(callback)

    def draw_card(self, card):
        self.hand.append(card)
        self.hand_size += 1

    @abstractmethod
    def pick_action(self, callback):
        pass

    @abstractmethod
    def pick_target(self, callback):
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

    def swap_cards(self, drawn_cards, callback):
        self.hand = self.hand + drawn_cards
        self.picked = list()
        self.pick_card(callback)

    def think_about_turn(self, turn):
        pass

    def start_thinking(self):
        pass


class HumanPlayer(Player):
    def __init__(self, num=3, coins=2):
        super(HumanPlayer, self).__init__(num, coins)
        self.strategy = "Human"

    def pick_target(self, callback):
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
        act = random.choice(self.possible_actions.values())  # needs to be a dict - not polymorphic :(
        callback(act)

    def stop_action(self, callback, action):
        callback(bool(randint(0, 1)))

    def pick_target(self, callback):
        # return game.players[input("who {}".format(len(game.players) - 1))]
        players_copy = copy.copy(self.game.players)
        if self in players_copy:
            players_copy.remove(self)
        if players_copy:
            target = random.choice(players_copy)
            callback(target)
        else:
            self.game.game_over()

    def inspect_action(self, action, callback):
        callback(bool(randint(0, 1)))

    def pick_card(self, callback):
        card = random.choice(self.hand)
        callback(card)


class ThinkingAI(Player):
    doubt_const = 0
    sure_const = 1

    def stop_action(self, callback, action):
        pass

    def pick_target(self, callback):
        pass

    def pick_action(self, callback):
        if self.coins >= 7:
            callback(self.possible_actions['coup'])

    def pick_card(self, callback):
        pass

    def inspect_action(self, action, callback):
        pass

    def think_about_turn(self, turn):
        self.think_about_action(turn.main_action, turn)

    def think_about_action(self, action, turn):
        current_player = action.executor
        if not (action.cancelled or action.stopped):  # if the action was succsessfully done
            self.other_players[current_player][action.enabler_card] += self.sure_const
        if action.cancelled:
            self.other_players[current_player][action.enabler_card] = 0
        if action.stopped:
            self.think_about_action(turn.stopping_action, turn)

    def __init__(self, num=3, coins=2):
        super(ThinkingAI, self).__init__(num, coins)
        self.strategy = "Thinking"
        self.other_players = dict()

    def draw_card(self, card):
        super(ThinkingAI, self).draw_card(card)

    def start_thinking(self):
        self.init_player_dict()

    def init_player_dict(self):
        for player in self.game.players:
            if player is not self:
                self.other_players[player] = dict()
                for i in xrange(1, Card.num_of_types):
                    # starting probability for having a certain type - amount of cards from a type/total cards
                    self.other_players[player][Card(i)] = self.game.deck_size / self.game.deck_size * Card.num_of_types
                for card in self.hand:
                    self.other_players[player][card] /= self.game.deck_size
