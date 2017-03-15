from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
import copy
from Coup import Coup
import player


class MenuScreen(Screen):
    pass


class SettingScreen(Screen, RelativeLayout):
    pass


class Log(ScrollView):
    text = StringProperty("")

    def __init__(self, **kwargs):
        super(Log, self).__init__(**kwargs)
        self._internal_text = ""

    def __iadd__(self, other):
        self._internal_text += other + '\n'
        self.text = self._internal_text
        # self.do_scroll


class GameScreen(Screen):
    # player_positions = [('center', 'bottom'), ('center', 'top'), ('left', 'center'), ('right', 'center')]
    # player_positions = [(0,0),(500,500),(100,100)]
    # player_places = [Blob(anchor_x=ps[0],anchor_y=ps[1]) for ps in player_positions]

    def on_pre_enter(self, *args):
        self.add_widget(GraphicalCoup(
            players=(player.RandomAI(), player.ThinkingAI(), player.RandomAI(), player.RandomAI(), player.RandomAI())))


class GraphicalCoup(RelativeLayout, Coup):
    # player_positions = [('center', 'bottom'), ('center', 'top'), ('left', 'center'), ('right', 'center')]
    # # player_positions = [(0,0),(500,500),(100,100)]
    # player_places = [Blob(anchor_x=ps[0], anchor_y=ps[1]) for ps in player_positions]

    def __init__(self, players, **kwargs):
        self.log = Log()
        Coup.__init__(self, players=players, deck_size=2, hand_size=2)
        RelativeLayout.__init__(self, **kwargs)
        self.add_widget(self.log)
        self.run_game()

    def output(self, output):
        super(GraphicalCoup, self).output(output)
        string = (str(output))
        # print string
        self.log.__iadd__(string)
        # self.text_label.refresh()

    def add_player(self, player):
        if player.strategy is "Human":
            player = GraphicalPlayer(coins=player.coins, num=player.num)
        # if player.strategy is "Random":
        #     player = GraphicalRandomAI(coins = player.coins, num = player.num)
        Coup.add_player(self, player)
        # player.pos
        # self.player_places[player.num].add_widget(player)

    def pass_turn(self):
        self.run_turn()

    def declare_action_to_inspect(self, action):
        self.announcment_label = Label(pos=(200, 200),
                                       text='Player {} is trying to {}!'.format(action.executor.num, str(action)))
        # self.add_widget(self.announcment_label)
        super(GraphicalCoup, self).declare_action_to_inspect(action)

    def declare_action_to_stop(self):
        super(GraphicalCoup, self).declare_action_to_stop()

    def declare_winner(self, winner):
        winner_label = Label(text='{} Player {} wins!'.format(winner.strategy,winner.num))
        self.add_widget(winner_label)
        super(GraphicalCoup, self).declare_winner(winner)


class CoupApp(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        # sm.add_widget(MenuScreen(name='menu'))
        # sm.add_widget(SettingScreen(name='settings'))
        sm.add_widget(GameScreen(name='game'))
        return sm


class GraphicalPlayer(player.HumanPlayer):
    #
    # def __init__(self, num=0, coins=2, **kwargs):
    #     player.Player.__init__(self, num=num, coins=coins)
    #     # Widget.__init__(self,**kwargs)
    #     self._num = 0
    #     self.num = num

    def pick_item(self, items, message, callback, pop=False):
        ButtonGenerator.generate_choice(items, self.game, callback, text=message)


class ButtonGenerator(BoxLayout):
    '''The widget recives a list of objects, and displays buttons that return the objects on touch'''

    def __init__(self, objects, callback, text='', **kwargs):
        super(ButtonGenerator, self).__init__(orientation='vertical', **kwargs)
        self.objects = objects
        self.size_hint_x = 0.4
        self.size_hint_y = 0.4
        self.pos = 400, 200
        self.add_widget(Label(text=text + '\n'))
        for obj in objects:
            new_button = ButtonGenerator.ReturningButton(given_object=obj, callback=callback)
            self.add_widget(new_button)

    @staticmethod
    def generate_choice(choices, game, callback, text=''):
        buttons = ButtonGenerator(choices, callback, text=text)
        game.add_widget(buttons)

    @staticmethod
    def close_choice(return_val, callback, buttons):
        buttons.parent.remove_widget(buttons)
        callback(return_val)

    class ReturningButton(Button):
        def __init__(self, given_object, callback, **kwargs):
            super(ButtonGenerator.ReturningButton, self).__init__(**kwargs)
            self.text = repr(given_object)
            self.bind(on_press=lambda x: ButtonGenerator.close_choice(return_val=given_object, callback=callback,
                                                                      buttons=self.parent))


CoupApp().run()
