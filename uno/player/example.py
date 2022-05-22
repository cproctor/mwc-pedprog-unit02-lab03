from uno.player.reinforcement import ReinforcementLearningUnoPlayer

def div(num, den):
    "This is just division, but if den is 0, returns 0."
    return num/den if den else 0

class Eliza(ReinforcementLearningUnoPlayer):
    """An example player which can learn through reinforcement learning.
    """

    def get_feature_names(self):
        return [
            "wild_ratio", 
            "special_ratio", 
            "playable_ratio",
            "nonwild_colors",
            "next_player_hand_delta",
        ]

    def hand_size(self, state, action):
        "Counts the cards in the player's hand."
        return len(state['hand'])

    def wild_ratio(self, state, action):
        "Ratio of wild cards in the hand"
        wild = len([c for c in state['hand'] if c.is_wild()])
        return div(wild, self.hand_size(state, action))

    def special_ratio(self, state, action):
        "Ratio of special cards in the hand"
        special_ranks = ['S', 'D', 'R', 'W', 'X']
        special = len([c for c in state['hand'] if c.rank in special_ranks])
        return div(special, self.hand_size(state, action))

    def playable_ratio(self, state, action):
        """Ratio of cards playable on the card to be played.
        If the action isn't a play, returns 0.
        """
        if action['action'] == 'play':
            playable = len([c for c in state['hand'] if c.is_playable(action['card'])])
            return div(playable, self.hand_size(state, action))
        else:
            return 0

    def next_player_hand_delta(self, state, action):
        "Hand size of the next player"
        return state['opponent_hands'][0] - self.hand_size(state, action)

    def nonwild_colors(self, state, action):   
        "Counts how many nonwild colors are in the hand."
        colors = [c.color for c in state['hand'] if not c.is_wild()]
        return len(set(colors))
