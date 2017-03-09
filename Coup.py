from itertools import cycle
from card import Card
from random import shuffle
import actions
import copy

class TurnPassException(Exception):
    def __str__(self):
        return "Turn Passed"


class GameEndException(Exception):
    def __str__(self):
        return "Game over!"

class Turn:
    def __init__(self):
        self.player = None

class Coup:
    def __init__(self, players, deck_size=3,hand_size=2):
        self.hand_size = hand_size
        self.num_of_players = 0
        self.deck = []
        self.is_playing = True
        self.current_action = None
        self.stopping_player = None
        self.inspecting_player = None
        self.stopping_action = None
        self.init_deck(deck_size)
        self.players = []  # player initialization
        for player in players:
            self.add_player(player)
        self.current_player_pointer = cycle(self.players)
        self.turns = list()

    def init_deck(self, deck_size):
        for i in xrange(deck_size):
            for j in xrange(1, Card.num_of_types):
                self.deck.append(Card(j))
        shuffle(self.deck)
        shuffle(self.deck)

    def add_player(self, player):
        """adds another player"""
        self.num_of_players += 1
        player.num = self.num_of_players
        player.game = self
        self.deal_cards(player)
        self.players.append(player)

    def deal_cards(self, player):
        for i in xrange(self.hand_size):
            player.draw_card(self.deck.pop())

    def run_turn(self):
        if self.is_playing:
            self.current_action = None
            self.stopping_player = None
            self.inspecting_player = None
            current_player = next(self.current_player_pointer)
            self.output(current_player)
            while not current_player.playing:
                current_player = next(self.current_player_pointer)
            # try:
            if self.num_of_players > 1:
                current_player.take_turn(self.pick_action)
            else:
                self.declare_winner(current_player)

    def run_game(self):
        self.output("Game start:")
        try:
            self.run_turn()
        except GameEndException as a:
            self.output(a)
        finally:
            pass

    def pick_action(self, action):
        if not action.is_valid():
            action.executor.pick_action(self.pick_action)
        else:
            self.declare_action_to_inspect(action)

    def declare_action_to_inspect(self, action):  # todo: break into two functions
        self.output(action)
        self.current_action = action
        if action.enabler_card:
            self.inspect_cycle = cycle(self.players)
            self.inspecting_player = next(self.inspect_cycle)
            while self.inspecting_player is not action.executor:
                self.inspecting_player = next(self.inspect_cycle) #startring with the player after the executor
            self.inspecting_player = next(self.inspect_cycle)
            # if self.inspecting_player is not action.executor:
            self.inspecting_player.inspect_action(action, self.inspect_action)
        else:
            self.declare_action_to_stop()

    def inspect_action(self,inspection):
        if inspection:
            self.output("P{} is inspecting the {}".format(self.inspecting_player.num,self.current_action))
            if self.demand_proof(self.current_action,self.inspecting_player):
                self.damage_player(self.inspecting_player,callback=self.current_action.do_action)
                # self.current_action.do_action()
            else:
                self.current_action.stopped = True
                self.damage_player(self.current_action.executor,self.pass_turn)
        else:
            inspecting_player = next(self.inspect_cycle)
            if inspecting_player is not self.current_action.executor:
                inspecting_player.inspect_action(action=self.current_action,callback=self.inspect_action)
            else:
                self.declare_action_to_stop()

    def declare_action_to_stop(self):
        if self.current_action.stopper_card:
            self.stopping_cycle = cycle(self.players)
            self.stopping_player = next(self.stopping_cycle)
            while self.stopping_player is not self.current_action.executor:
                self.stopping_player = next(self.stopping_cycle)  # startring with the player after the executor
            self.stopping_player = next(self.stopping_cycle)
            # if self.inspecting_player is not action.executor:
            self.stopping_player.stop_action(self.stop_action, self.current_action)
        else:
            self.current_action.do_action()

    def stop_action(self,stop):
        if stop:
            self.stopping_action = counter = actions.CounterAction(player=self.stopping_player,game=self,counter_of=self.current_action)
            self.declare_action_to_inspect(counter)
        else:
            self.stopping_player = next(self.stopping_cycle)
            if self.stopping_player is not self.current_action.executor:
                self.stopping_player.stop_action(self.stop_action, self.current_action)
            else:
                self.current_action.do_action()

    def reveal_cards(self, player, amount,callback):
        temp_hand = list()
        for i in xrange(amount):
            temp_hand.append(self.deck.pop())
        player.swap_cards(temp_hand,self.return_cards)

    def return_cards(self,cards):
        for card in cards:
            self.deck.append(card)

    def pass_turn(self):
        this_turn = Coup.Turn(self.deck,self.current_action,self.stopping_action,self.inspecting_player)
        self.turns.append(this_turn)
        self.run_turn()

    class Turn:
        def __init__(self,deck,main_action,stopping_action,inspector):
            self.deck = tuple(deck)
            self.main_action = copy.copy(main_action)
            self.stopping_action = copy.copy(stopping_action) #just to make sure its by value, actually should be immutable
            if self.main_action.cancled: #only if the inspector was right
                self.inspector = copy.copy(inspector)
            else:
                self.inspector = None

    def output(self,output):
        print output
        print '\n'

    def declare_winner(self,winner):
        self.output("Player {} wins!".format(winner.num))
        # raise GameEndException()

    def demand_proof(self,action,inspector):
        # self.output("P{} is inspecting the {}".format(inspector.num,action.name))
        for card in action.executor.hand:
            if action.enabler_card == card:
                self.output("P{} speaks the truth!".format(str(action.executor.num)))
                return True
        self.output("P{} speaks Lies!".format(str(action.executor.num)))
        return False

    def damage_player(self, player,callback):
        self.damage_callback = callback #quick_fix
        player.discard_card(self.player_damaged)
        self.output("Damage P{}~!".format(str(player.num)))
        # callback()

    def player_damaged(self,cards):
        for player in self.players:
            if not player.hand:
                self.remove_player(player)
        self.damage_callback()

    def remove_player(self, player):
        self.output("Player {} Removed!".format(player.num))
        player.playing = False
        self.players.remove(player)
        self.num_of_players -=1
        self.game_over()

    def game_over(self):
            i=0
            for player in self.players:
                if player.playing:
                    i+=1
            if i is 1:
                self.is_playing = False
                for player in self.players:
                    if player.playing:
                        self.declare_winner(player)


# game = Coup([player.Player(),player.Player(),player.Player()],3)
#
# game.run_game()
