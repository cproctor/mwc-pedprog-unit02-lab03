class Card:
    def __init__(self, code):
        self.code = code
        self.color = self.decode_color()
        self.rank = self.decode_rank()

    def __str__(self):
        return self.code

    def __repr__(self):
        return f"<Card {self.code}>"

    def is_playable(self, top_card):
        "Determines whether this card can be played onto the top card."
        if self.color == top_card.color:
            return True
        elif self.rank == top_card.rank:
            return True
        elif self.color == "WILD":
            return True
        else:
            return False

    def decode_color(self):
        if self.code[0] == "R":
            return "RED"
        elif self.code[0] == "B": 
            return "BLUE"
        elif self.code[0] == "Y":
            return "YELLOW"
        elif self.code[0] == "G":
            return "GREEN"
        elif self.code[0] == "W":
            return "WILD"

    def decode_rank(self):
        if self.code[1].isdigit():
            return self.code[1]
        elif self.code[1] == "S":
            return "S"
        elif self.code[1] == "D":
            return "D"
        elif self.code[1] == "R":
            return "R"
        elif self.code[1] == "W":
            return "W"
        elif self.code[1] == "X":
            return "X"
            
    def is_wild(self):
        return self.code[0] == "W"

    def activate(self, game):
        "Activates the card's special ability by making a change to the game."
        if self.rank == "S":
            player = game.current_player()
            game.messages.append(f"{player.name}'s turn is skipped!")
            game.end_of_turn()




