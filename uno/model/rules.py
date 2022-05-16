class UnoRules:
    """Represents the rules of Uno, using the language of states, actions, 
    and rewards.
    """

    def get_next_state(self, state, action):
        "Given a state and an action, returns the resulting state."

    def get_actions(self, state):
        """Given a state, returns available actions.
        An action is a dictionary containing the key "action", 
        whose values may be "play" or "draw". If "action" is "play",
        the dictionary should also have a c
        """
        actions = []
        for card in state["hand"]:
            if card.is_playable(
            

    def is_over(self):
        "Returns whether the game has ended."
        for hand in self.hands:
            if len(hand) == 0:
                return True
        return False

    def get_reward(self, state):
        "The reward is 1 when you have won, -1 when you have lost, and 0 otherwise."
        if self.is_over():
            if len(state["hand"]) == 0:
                return 1
            else: 
                return -1
        else:
            return 0


