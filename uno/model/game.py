from random import shuffle, choice
from uno.decks import decks
from uno.model.card import Card

class UnoGame:
    """Models an uno game. Uno is slightly different from tic-tac-toe and nim, in 
    that no player can see the entire game state. In particular, a player can't
    see other players' hands. Therefore, the state a player uses to choose an 
    action is different from the entire game state. 

    To represent this, UnoGame keeps track of the entire game's state, and provides 
    players a limited state representing what part of the game they can see.
    The state a player receives is:
    
    {
        "hand": [cards],
        "top_card": card,
        "opponent_hands": [integers],
        "clockwise": bool,
        "drawn_card: card or None,
    }

    A few details: The hand is a list of Card objects. The top card is also a Card.
    Opponent hands is just a list of integers representing how many cards are in 
    each opponent's hand--you don't get to see what's in the opponent's hand. 
    Clockwise is a boolean indicating whether play is going clockwise. 
    Finally, drawn card is the card which was just drawn, or None if a card was 
    not just drawn. This is important because after a player draws a card, she has
    the option to immediately play it if it is playable.
    """

    def __init__(self, players, deck_name="basic", start_cards=7):
        self.deck_name = deck_name
        self.start_cards = start_cards
        self.players = players
        self.reset()

    def reset(self):
        "Resets the game."
        self.messages = ["Welcome to Uno."]
        self.draw_pile = [Card(code) for code in decks[self.deck_name]]
        shuffle(self.draw_pile)
        self.current_player_index = 0
        self.hands = []
        self.clockwise = True
        self.drawn_card = None
        for player in range(self.num_players()):
            hand = [self.draw_card() for i in range(self.start_cards)]
            self.hands.append(hand)
        self.play_pile = [self.draw_card()]
        if self.top_card().is_wild():
            self.top_card().color = choice(["RED", "YELLOW", "GREEN", "BLUE"])

    def get_state(self):
        """Returns the game state as seen by the current player."""
        return {
            "hand": self.current_hand(),
            "top_card": self.top_card(),
            "opponent_hands": self.opponent_hands(),
            "clockwise": self.clockwise,
            "drawn_card": self.drawn_card,
        }
        
    def play_action(self, action):
        """Given a state and an action, returns the resulting state.
        Note that (unlike in tac-tac-tow), calling this method advances the
        game, resulting in cards being drawn, the direction of play changing, 
        etc. 
        """
        message = self.current_player().action_message(action)
        self.messages.append(message)
        self.drawn_card = None
        if action["action"] == "pass":
            self.end_of_turn()
        elif action["action"] == "draw":
            card = self.draw_card()
            self.current_hand().append(card)
            if card.is_playable(self.top_card()):
                self.drawn_card = card
            else:
                self.end_of_turn()
        elif action["action"] == "play":
            card = action["card"]
            if "color" in action.keys():
                card.color = action["color"]
            self.play_card(card, self.current_hand())
            self.end_of_turn()
            card.activate(self)
        return self.get_state()
                
    def get_actions(self):
        """Given a state, returns available actions.
        An action is a dictionary containing the key "action", 
        whose values may be "play,""draw," or "pass." ("pass" is only
        a valid action when the player has just drawn a card which could 
        be immediately played. If "action" is "play",
        the dictionary should also have a "card" key. If the card is 
        a wild card, then the dictionary should additinally have a 
        "color" key. Examples include:
            {"action": "draw"}
            {"action": "play", "card": "R4"}
            {"action": "play", "card": "X4", "color": "BLUE"}
            {"action": "pass"}
        """
        if self.is_over():
            return []
        actions = []
        if self.drawn_card:
            actions.append({"action": "pass"})
            if self.drawn_card.is_wild():
                for color in ["RED", "BLUE", "YELLOW", "GREEN"]:
                    actions.append({"action": "play", "card": self.drawn_card, "color": color})
            else:
                actions.append({"action": "play", "card": self.drawn_card})
        else:
            for card in self.current_hand():
                if card.is_playable(self.top_card()):
                    if card.is_wild():
                        for color in ["RED", "BLUE", "YELLOW", "GREEN"]:
                            actions.append({"action": "play", "card": card, "color": color})
                    else:
                        actions.append({"action": "play", "card": card})
            if len(actions) == 0:
                actions.append({"action": "draw"})
        return actions
            
    def is_over(self):
        "Returns whether the game has ended."
        for hand in self.hands:
            if len(hand) == 0:
                return True
        return False

    def winner(self):
        "Returns the winner"
        for hand, player in zip(self.hands, self.players):
            if len(hand) == 0:
                return player

    def get_reward(self, state):
        "The reward is 1 when you have won, -1 when you have lost, and 0 otherwise."
        if self.is_over():
            if self.current_player() == self.winner():
                return 1
            else: 
                return -1
        else:
            return 0

    def num_players(self):
        "Counts how many players are in the game."
        return len(self.players)

    def top_card(self):
        "Returns the top card in the play pile."
        return self.play_pile[-1]

    def current_player(self):
        "Returns the current player"
        return self.players[self.current_player_index]

    def next_player(self):
        "Returns the next player"
        return self.players[self.next_player_index()]

    def current_hand(self):
        "Returns the current player's hand"
        return self.hands[self.current_player_index]

    def draw_card(self):
        """Draws a card from the draw pile. 
        In case the draw pile is empty, shuffle the play pile (except the top card)
        into the draw pile. If the draw pile is still empty, raise an exception. 
        This should almost never happen with four or fewer players.
        Any wild cards have their "WILD" color restored. 
        """
        if len(self.draw_pile) == 0:
            self.draw_pile = self.play_pile
            self.play_pile = [self.draw_pile.pop()]
            shuffle(self.draw_pile)
            for card in self.draw_pile:
                if card.is_wild():
                    card.color = "WILD"
        if len(self.draw_pile) == 0:
            raise Exception("Ran out of cards!")
        return self.draw_pile.pop()

    def play_card(self, card, hand):
        "Plays a card, adding it to the play pile and removing it from the hand."
        self.play_pile.append(card)
        hand.remove(card)
        
    def opponent_hands(self):
        """Returns a list of integers showing how many cards are in
        each opponent's hand, going clockwise from the current player.
        """
        hands = []
        for i in range(1, self.num_players()):
            hand_index = (self.current_player_index + i) % self.num_players()
            cards_in_hand = len(self.hands[hand_index])
            hands.append(cards_in_hand)
        return hands

    def opponents(self):
        opponents= []
        for i in range(1, self.num_players()):
            index = (self.current_player_index + i) % self.num_players()
            opponents.append(self.players[index])
        return opponents
            
    def end_of_turn(self):
        "Records that the turn has ended by advanceing the current player"
        if len(self.current_hand()) == 1:
            self.messages.append(f"{self.current_player().name} has only one card left.")
        if not self.is_over():
            self.current_player_index = self.next_player_index()

    def next_player_index(self):
        "Returns the index of the next player"
        offset = 1 if self.clockwise else -1
        return (self.current_player_index + offset) % self.num_players()

