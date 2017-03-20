class Card:
    # card_dict = {'None': None, 'Captain': 1, 'Duke': 2, 'Assassin': 3, 'Countess': 4,'Ambassador': 5}
    # card_names = {0: 'None', 1: 'Captain', 2: 'Duke', 3: 'Assassin', 4: 'Countess', 5: 'Ambassador'}
    card_dict = {'None': None, 'Captain': 1, 'Duke': 2, 'Assassin': 3, 'Countess': 4}
    card_names = {0: 'None', 1: 'Captain', 2: 'Duke', 3: 'Assassin', 4: 'Countess'}
    # card_dict = {'None': None, 'Captain': 1, 'Duke': 2, 'Assassin': 3, 'Countess': 4, 'Ambassador': 5}
    num_of_types = len(card_names)

    def __init__(self, type):
        if isinstance(type, str):
            self.type = Card.card_dict[type]
        if 0 < type < Card.num_of_types:
            self.type = type

    def __repr__(self):
        return "{}".format(Card.card_names[self.type])

    def __eq__(self, other):
        """overriding =="""
        return self.type == other.type

    def __hash__(self):
        """lets the cards be a dictionary key (hashable)"""
        return hash(Card.card_names[self.type])