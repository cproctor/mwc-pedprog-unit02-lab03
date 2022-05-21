from uno.player.reinforcement import ReinforcementLearningUnoPlayer

class Eliza(ReinforcementLearningUnoPlayer):
    """An example player which can learn through reinforcement learning.
    """

    def get_feature_names(self):
        return [
            "cards_in_hand",
            "wild_cards_in_hand",
            "nonwild_colors",
        ]

    def cards_in_hand(self, state, action):
        "Counts the cards in the player's hand."
        return len(state['hand'])

    def wild_cards_in_hand(self, state, action):
        "Counts wild cards in the player's hand."
        return len([c for c in state['hand'] if c.is_wild()])

    def nonwild_colors(self, state, action):   
        "Counts how many nonwild colors are in the hand."
        colors = [c.color for c in state['hand'] if not c.is_wild()]
        return len(set(colors))
