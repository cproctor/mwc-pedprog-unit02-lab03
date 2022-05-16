class SmartUnoPlayer:

    def __init__(self, name):
        self.name = name
        self.is_automated = True
    
    def choose_action(self, state, actions):
        if self.can_play_card(actions):
            for action in actions:
                if action["action"] == "play" and not action["card"].is_wild():
                    return action
        return actions[0]

    def can_play_card(self, actions):
        return any([a["action"] == "play" for a in actions])

    def action_message(self, action):
        return ""
