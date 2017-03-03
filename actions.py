from abc import abstractmethod, ABCMeta
import card


class Action:
    __metaclass__ = ABCMeta

    def __init__(self, player, game=None):
        self.executor = player
        self.enabler_card = None
        self.stopper_card = None
        self.cost = 0
        self.name = "MISSING NAME"
        self.stopped = False
        self.canceled = False
        self.game = game

    @abstractmethod
    def do_action(self):
        self.stopped = False
        self.canceled = False
        self.game.pass_turn()

    def is_valid(self):
        return True

    def __repr__(self):
        return self.name + '\n'

    def __str__(self):
        return "P{} does {} \n".format(self.executor.num,self.name)

class Steal(Action):
    def __init__(self, player, game=None):
        super(Steal, self).__init__(player)
        self.enabler_card = card.Card('Captain')
        self.stopper_card = card.Card('Captain')
        self.name = "Steal"

    def do_action(self):
        self.game = self.game
        self.executor.pick_target(callback=self.next_action)

    def is_valid(self):
        for player in self.game.players:
            if player is not self.executor and player.coins >= 2:
                return True
        return False

    def next_action(self,target):
        if target.coins <=0:
            print "no coins"
            self.executor.pick_target(callback=self.next_action)
        else:
            target.coins -= 2
            self.executor.coins += 2
            super(Steal, self).do_action()



class CounterAction(Action):
    def __init__(self, player, counter_of,game=None):
        super(CounterAction, self).__init__(player,game)
        self.counter_of = counter_of
        self.enabler_card = counter_of.stopper_card
        self.name = "Counter"

    def do_action(self):
        super(CounterAction, self).do_action()

    def __str__(self):
        return "{} {}".format(self.name, self.counter_of.name)


class Income(Action):
    def __init__(self, player, game=None):
        super(Income, self).__init__(player)
        self.name = "Income"

    def do_action(self):
        self.executor.coins += 1
        super(Income, self).do_action()

class ForeignAid(Action):
    def __init__(self, player, game=None):
        super(ForeignAid, self).__init__(player)
        self.name = "Foreign Aid"
        self.stopper_card = card.Card('Duke')

    def do_action(self):
        self.executor.coins += 2
        super(ForeignAid, self).do_action()

class Coup(Action):
    def __init__(self, player, game=None):
        super(Coup, self).__init__(player)
        self.name = "Coup"
        self.cost = 7

    def do_action(self):
        self.executor.pick_target(callback=self.next_action)

    def next_action(self,target):
        self.executor.coins-=self.cost
        self.game.damage_player(target,super(Coup, self).do_action)
        # super(Coup, self).do_action()
    def is_valid(self):#TODO was here
        return self.executor.coins>=self.cost
class Assassinate(Coup):
    def __init__(self, player, game=None):
        super(Assassinate, self).__init__(player)
        self.name = "Assassinate"
        self.cost = 3
        self.enabler_card = card.Card('Assassin')
        self.stopper_card = card.Card('Countess')


class Tax(Action):
    def __init__(self, player, game=None):
        super(Tax, self).__init__(player)
        self.name = "Tax"
        self.enabler_card = card.Card('Duke')

    def do_action(self):
        self.executor.coins += 3
        super(Tax, self).do_action()
class Exchange(Action):
    def __init__(self, player, game=None):
        super(Exchange, self).__init__(player)
        self.name = "Exchange"
    def do_action(self):
        self.game.reveal_cards(amount=2,player=self.executor, callback=self.next_action)

    def next_action(self,cards):
        self.game
