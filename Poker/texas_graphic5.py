import random
from collections import Counter
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

class Card:
    ACE, JACK, QUEEN, KING = 'A', 'J', 'Q', 'K'
    FACES = (ACE, '2', '3', '4', '5', '6', '7', '8', '9', '10', JACK, QUEEN, KING)
    SUITS = tuple(map(chr, (9824, 9827, 9829, 9830)))
    SPADE, CLUB, HEART, DIAMOND = SUITS  # ♠ ♣ ♥ ♦

    def __init__(self, suit, face):
        self._suit = suit
        self._face = face

    def __int__(self):
        if self._face == Card.JACK:
            return 11
        if self._face == Card.QUEEN:
            return 12
        if self._face == Card.KING:
            return 13

        return 1 if self._face == Card.ACE else int(self._face)

    def __str__(self):
        return self._suit + str(self._face)

    def __repr__(self):
        return __class__.__name__ + repr((self._suit, self._face))

class Deck:
    def __init__(self):
        self._deck = [Card(suit, face) for suit in Card.SUITS for face in Card.FACES]

    def show(self):
        return self._deck

    def shuffle(self):
        random.shuffle(self._deck)

    def __iter__(self):
        return iter(self._deck)

    def draw_cards(self, num_cards=1):
        if num_cards > len(self._deck):
            raise ValueError("Not enough cards in the deck")

        drawn_indices = random.sample(range(len(self._deck)), num_cards)
        drawn_cards = [self._deck.pop(i) for i in sorted(drawn_indices, reverse=True)]

        return drawn_cards

    def create_deck():
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        deck = [Card(suit, rank) for suit in suits for rank in ranks]
        return deck

class PokerGame:
    HAND_RANKINGS = ["Royal Flush", "Straight Flush", "Four of a Kind", "Full House", "Flush", "Straight",
                      "Three of a Kind", "Two Pairs", "One Pair", "High Card", "Straight (No Flush)"]

    def __init__(self):
        self.deck = Deck()
        self.players = []
        self.community_cards = []
        self.pot = 0
        self.current_highest_bet = 0
        self.raise_amount = 0
        self.current_player_index = 0
        self.small_blind_player = 'Player1'
        self.total_raise_amount = 0
        self.tie_flag = 0

    def add_player(self, player_name):
        self.players.append({'name': player_name, 'hand': [], 'money': 5000, 'decision': None, 'bet': 20})
    
    def get_active_players(self):
        return [player['name'] for player in self.players if player['money'] > 0 and player['decision']!='fold']
    
    def get_money(self, player_name):
        for player in self.players:
            if player['name'] == player_name:
                return player['money']
        return None

    def get_bet(self,player_name):
        for player in self.players:
            if player['name'] == player_name:
                return player['bet']
        return None
    
    def get_pot(self):
        return self.pot
    
    def set_tie_flag(self,value):
        self.tie_flag = value
    
    def get_tie_flag(self):
        return self.tie_flag
    
    def get_player_by_name(self, player_name):
        for player in self.players:
            if player['name'] == player_name:
                return player
        return None 

    def get_player_decision(self):
        current_player = self.players[self.current_player_index]
        decision = gui.enable_button()

        return decision, current_player['bet']
        
    def increment_current_player_index(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    def get_index(self):
        return self.current_player_index
    
    def evaluate_hand(self, private_cards, community_cards):
        all_cards = private_cards + community_cards

        values = [card.__int__() for card in all_cards]
        suits = [card._suit for card in all_cards]

        # Count occurrences of each value and suit
        value_counts = Counter(values)
        suit_counts = Counter(suits)

        # Check for flush
        is_flush = any(count >= 5 for count in suit_counts.values())
        flush_suit = [suit for suit, count in suit_counts.items() if count >= 5]

        # Check for straight
        sorted_values = sorted(set(values))
        is_straight = any(sorted_values[i:i+5] == list(range(sorted_values[i], sorted_values[i]+5))
                        for i in range(len(sorted_values) - 4))

        if is_straight and is_flush:
            if 14 in sorted_values:
                return "Royal Flush", flush_suit[0]
            else:
                return "Straight Flush", flush_suit[0]
        elif 4 in value_counts.values():
            return "Four of a Kind", max(value_counts, key=value_counts.get)
        elif 3 in value_counts.values() and 2 in value_counts.values():
            three_of_a_kind=''
            two_of_a_kind=''
            for key, value in value_counts.items():
                if value == 2:
                    two_of_a_kind=key
                elif value==3:
                    three_of_a_kind=key
            return "Full House", [three_of_a_kind, two_of_a_kind]
        elif is_flush:
            return "Flush", flush_suit[0]
        elif is_straight:
            return "Straight", None
        elif 3 in value_counts.values():
            return "Three of a Kind", max(value_counts, key=value_counts.get)
        elif list(value_counts.values()).count(2) >= 2:
            pairs = [value for value, count in value_counts.items() if count == 2]
            return "Two Pairs", pairs
        elif list(value_counts.values()).count(2) == 1:
            return "One Pair", max(value_counts, key=value_counts.get)
        else:
            return "High Card", max(values) 

    def deal_hands(self, num_cards=2):
        for player in self.players:
            player['hand'] = self.deck.draw_cards(num_cards)

    def deal_community_cards(self, num_cards):
        revealed_cards = self.deck.draw_cards(num_cards)
        self.community_cards.extend(revealed_cards)

    def determine_winner(self):
        active_players = [player for player in self.players if player['money'] > 0 and player['decision']!='fold'] 
        best_hands = [(player['name'], self.evaluate_hand(player['hand'], self.community_cards)) for player in active_players]
        tied_players = [player for player in best_hands if player[1][0] == best_hands[0][1][0]]

        if len(tied_players)<2:
            best_hands.sort(key=lambda x: (self.HAND_RANKINGS.index(x[1][0]), x[0]))

        if len(tied_players) > 1:  # There is a tie
            # Compare high cards
            values = []
            suits = []
            for player in active_players:
                values.append([card.__int__() for card in player['hand']])
                suits.append([card._suit for card in player['hand']])

            i = 0
            for pair in values:
                if max(pair) != min(pair):
                        suits[i].remove(suits[i][pair.index(min(pair))])
                        pair.remove(min(pair))
                i+=1

            high_cards_values = values
  

            if values[0]>values[1]:  
                winner_info = tied_players[0]
                player_name = winner_info[0]

                hand_type = suits[0][0]
                hand_values = values[0][0]
                winner = (player_name, (hand_type, hand_values))

                # Distribute money to winner
                self.get_player_by_name(player_name)['money'] += self.get_pot()

                return winner
            elif values[1]>values[0]:
                winner_info = tied_players[1]
                player_name = winner_info[0]
                hand_type = suits[1][0]
                hand_values = values[1][0]
                winner = (player_name, (hand_type, hand_values))

                # Distribute money to winner
                self.get_player_by_name(player_name)['money'] += self.get_pot()

                return winner
            else:
                # Find the player with the highest high card
                winner = tied_players[high_cards_values.index(max(high_cards_values))]
                player_name = (' and '.join(player[0] for player in tied_players))
                hand_type = winner[1][0]
                hand_values = winner[1][1]
                winner = (player_name, (hand_type, hand_values))
                game.set_tie_flag(1)

                #return money because of tie
                split_amount = self.get_pot()/len(active_players)
                for player in active_players:
                    player['money']+=split_amount

                return winner

        self.get_player_by_name(best_hands[0][0])['money']+=self.get_pot()

        # No tie, return the winner
        return best_hands[0]
    
    # game and betting logic for before dealing 3 community cards
    def decision_cycle(self, raise_amount):

        active_players = [player for player in self.players if player['money'] > 0]  # Filter out players with no money
        gui.set_submitted_flag(0)

        while len(active_players) >= 2:

            

            current_player = self.players[self.current_player_index]  
            max_bet = max(player['bet'] for player in self.players)

            print(f"{current_player['name']}'s hand: {current_player['hand']}")
     
            current_player['decision'], current_player['bet'] = self.get_player_decision()
            print(current_player['name'], 'start', current_player['decision'])

            if current_player['decision'] == 'fold':
                current_player['money'] -= current_player['bet']
                current_player['bet'] = 0
            elif current_player['decision'] == 'call':
                self.pot += abs(self.total_raise_amount - current_player['bet'])
                current_player['money'] -= abs(self.total_raise_amount - current_player['bet'])
                current_player['bet'] = max_bet
            elif current_player['decision'] == 'raise':
                self.total_raise_amount += raise_amount  # Update the total raise amount
                current_player['bet'] = self.total_raise_amount
                self.pot += current_player['bet']
                current_player['money'] -= current_player['bet']
            elif current_player['decision'] == 'hold':
                while current_player['bet'] == 10:
                    current_player['decision'], current_player['bet'] = self.get_player_decision()
                    current_player['bet'] = 20
                    break
                current_player['money']-=current_player['bet']
               
            max_bet = max(player['bet'] for player in self.players)
            if all(player['bet'] == max_bet for player in active_players) and self.get_index()+1==len(active_players):
                gui.increment_round()
                gui.set_submitted_flag(0)
                self.deal_community_cards(3)
                self.current_player_index = 0
                self.total_raise_amount = 0
                for player in active_players:
                    player['bet'] = 0
                break
            
            if all(player['bet'] == max_bet for player in active_players):
                for player in active_players:
                    player['bet'] = 0
 
            if self.current_player_index+1 == len(active_players):
                self.current_player_index = 0
                break
            
            self.increment_current_player_index()  
            break

        active_players = [player for player in self.players if player['money'] > 0 and player['decision']!='fold']  # Filter out players with no money

        if len(active_players)==1:
            for i in range(5-len(self.community_cards)):
                self.deal_community_cards(1)
            gui.update_community_cards_display()
            gui.set_round(5)
            gui.end_round()
            current_player['decision'] = None
            self.current_player_index = 0
            gui.restart_game()


    def first_bet(self):
        # Input small blind amount
        small_blind_amount = 10

        # Input big blind amount
        big_blind_amount = 20
        self.current_highest_bet = big_blind_amount

        # Set small blind player (Player1)
        self.players[0]['bet'] = small_blind_amount
        self.current_highest_bet = small_blind_amount

        # Set big blind player (Player2)
        self.players[1]['bet'] = big_blind_amount
        self.current_highest_bet = big_blind_amount

        # Display initial pot
        self.pot = small_blind_amount + big_blind_amount
        self.get_player_by_name('Player1')['money']-=small_blind_amount
        self.get_player_by_name('Player2')['money']-=big_blind_amount

    # game and betting logic for after community cards are distributed
    def betting_round(self, raise_amount):
        active_players = [player for player in self.players if player['money'] > 0]  # Filter out players with no money

        gui.set_submitted_flag(0)

        while len(active_players) >= 2:

            current_player = self.players[self.current_player_index]  
            max_bet = max(player['bet'] for player in self.players)
            current_player['decision'], current_player['bet'] = self.get_player_decision()

            if current_player['decision'] == 'fold':
                current_player['money'] -= current_player['bet']
                current_player['bet'] = 0
            elif current_player['decision'] == 'call':
                self.pot += abs(self.total_raise_amount - current_player['bet'])
                current_player['money'] -= abs(self.total_raise_amount - current_player['bet'])
                current_player['bet'] = max_bet
            elif current_player['decision'] == 'raise':
                self.total_raise_amount += raise_amount  # Update the total raise amount
                current_player['bet'] = self.total_raise_amount 
                self.pot += current_player['bet']
                current_player['money'] -= current_player['bet']
            elif current_player['decision'] == 'hold':
                current_player['money']-=current_player['bet']
               
            max_bet = max(player['bet'] for player in self.players)
            if all(player['bet'] == max_bet for player in active_players) and self.get_index()+1==len(active_players):
                gui.increment_round()
                gui.set_submitted_flag(0)
                if gui.get_round()==5:
                    gui.set_round(6)
                    gui.end_round()
                    self.current_player_index = 0
                    gui.restart_game()
                else:
                    self.deal_community_cards(1)
                    gui.update_community_cards_display()
                    self.current_player_index = 0
                    self.total_raise_amount = 0
                    for player in active_players:
                        player['bet'] = 0
                break
 
            if self.current_player_index+1 == len(active_players):
                self.current_player_index = 0
                break
            self.increment_current_player_index()  
            break

        active_players = [player for player in self.players if player['money'] > 0 and player['decision']!='fold']  # Filter out players with no money

        if len(active_players)==1:
            for i in range(5-len(self.community_cards)):
                self.deal_community_cards(1)
            gui.update_community_cards_display()
            gui.set_round(5)
            gui.end_round()
            current_player['decision'] = None
            self.current_player_index = 0
            gui.restart_game()

class PokerGameGUI:
    SUIT_MAPPING = {
        '♠': 'Spades',
        '♣': 'Clubs',
        '♥': 'Hearts',
        '♦': 'Diamonds'
    }
    def __init__(self, game):
        self.game = game
        self.root = tk.Tk()
        self.root.title('Poker Game')
        self.root.geometry("1200x1200")
        self.raise_amount = 0
        self.round = 1
        self.action = ""
        self.winner_label = tk.Label(self.root)
        self.player_turn_label = tk.Label(self.root,text="") 

        # Initialize the Entry and Button widgets
        self.number_entry = tk.Entry(self.root, width=10)
        self.number_entry.pack_forget()

        self.submit_button = tk.Button(self.root, text="Submit", command=self.process_input)
        self.submit_button.pack_forget()

        # Create an IntVar to act as a flag for submission
        self.submitted_flag = tk.IntVar(self.root,value=0)
        self.hold_flag = tk.IntVar(self.root,value=0)

        self.card_images = self.load_card_images()
        
        self.setup_gui()
        
        self.game.first_bet()
        self.update_bets_and_pot()
        self.deal_initial_cards()
        self.update_hand_display()

    def set_round(self, value):
        self.round = value

    def restart_game(self):
        result = messagebox.askyesno("Restart Game", "Do you want to restart the game?")
        if result:
            self.set_round(1)
            game.community_cards = []
            game.deck = Deck()
            
            self.deal_initial_cards()
            self.call_button.config(state=tk.NORMAL)
            self.fold_button.config(state=tk.NORMAL)
            self.winner_label.config(text="")
            game.first_bet()
            
            self.update_hand_display()
            self.update_bets_and_pot()
            
            messagebox.showinfo("Game Restarted", "The game has been restarted.")
        else:
            self.root.destroy()
    
    def increment_round(self):
        self.round+=1

    def get_round(self):
        return self.round

    def delete_frames(self):
        for element in self.player_hand_frame.winfo_children():
            element.destroy()

        for element in self.community_frame.winfo_children():
            element.destroy()

        for element in self.dealer_hand_frame.winfo_children():
            element.destroy()

    def disable_user_interaction(self):
        self.call_button.config(state=tk.DISABLED)
        self.hold_button.config(state=tk.DISABLED)
        self.raise_button.config(state=tk.DISABLED)
        self.fold_button.config(state=tk.DISABLED)

    def end_round(self):
        self.disable_user_interaction()

        winner = game.determine_winner()

        if game.get_tie_flag()==1:
            self.winner_label = tk.Label(self.root, text=f"Tie between {winner[0]} with {winner[1]}")
            self.winner_label.place(x=640, y=850) 
            game.set_tie_flag(0)
        else:
            self.winner_label = tk.Label(self.root, text=f"Winner: {winner[0]} with {winner[1]}")
            self.winner_label.place(x=640, y=850) 

    def process_input(self):
        try:
            # Get the entered number from the Entry widget
            entered_number = int(self.number_entry.get())
            while entered_number > game.get_player_by_name(game.get_active_players()[game.current_player_index])['money']:
                self.number_entry.pack_forget()
                self.submit_button.pack_forget()
                self.number_entry = tk.Entry(self.root, width=10)
                self.submit_button = tk.Button(self.root, text="Submit", command=self.process_input)

                # Pack the widgets
                self.number_entry.pack(pady=5)
                self.submit_button.pack()
                entered_number = int(self.number_entry.get())
            self.result_label.config(text="")

            self.raise_amount = entered_number

            self.submitted_flag.set(1)

        except ValueError:
            # Handle the case where the entered value is not a valid integer
            self.result_label.config(text="Invalid input. Please enter a number.")

    def run(self):
        self.root.mainloop()

    def load_card_images(self):
        card_images = {}
        for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
            for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
                filename = f'{rank}_of_{suit}.png'  
                # path = os.path.join('/Users/chloesun/Downloads/playing-cards-master', filename)
                path = os.path.join(os.path.dirname(__file__), 'playing-cards-master', f'{rank}_of_{suit}.png')
                image = Image.open(path)
                image = image.resize((70, 120), Image.LANCZOS)

                photo = ImageTk.PhotoImage(image)
                card_key = f"{rank}_of_{suit}"
                card_images[card_key] = photo  

        # Store card_images at the class level
        self.card_images = card_images

        return card_images
    
    def setup_gui(self):
        # Create GUI features
        self.player_hand_label = tk.Label(self.root, text="")
        self.player1_bet_label = tk.Label(self.root,text="")
        self.player1_money_label = tk.Label(self.root,text="")
        self.community_cards_label = tk.Label(self.root, text="")
        self.pot_label = tk.Label(self.root,text="")
        self.dealer_hand_label = tk.Label(self.root, text="")
        self.player2_bet_label = tk.Label(self.root,text="")
        self.player2_money_label = tk.Label(self.root,text="")
        self.player_score_label = tk.Label(self.root, text="")
        self.dealer_score_label = tk.Label(self.root, text="")
        self.insturction_label = tk.Label(self.root)
        self.result_label = tk.Label(self.root, text="")
        
        self.fold_button = tk.Button(self.root, text="Fold", command= self.Fold)
        self.raise_button = tk.Button(self.root, text="Raise", command=self.Raise)
        self.call_button = tk.Button(self.root, text="Call", command= self.Call)
        self.hold_button = tk.Button(self.root, text="Hold", command= self.Hold)
        self.hold_button.config(state=tk.DISABLED)
        self.raise_button.config(state=tk.DISABLED)

        self.player_hand_label.pack()
        self.player1_bet_label.pack()
        self.player1_money_label.pack()
        self.player_hand_frame = tk.Frame(self.root) #frames to hold card images
        self.player_hand_frame.pack()
        self.community_cards_label.pack()
        self.pot_label.pack()
        self.community_frame = tk.Frame(self.root)
        self.community_frame.pack()
        self.player_score_label.pack()
        self.dealer_hand_label.pack()
        self.player2_bet_label.pack()
        self.player2_money_label.pack()
        self.dealer_hand_frame = tk.Frame(self.root)
        self.dealer_hand_frame.pack()
        self.dealer_score_label.pack()
        self.insturction_label.pack()
        self.fold_button.pack()
        self.raise_button.pack()
        self.call_button.pack()
        self.hold_button.pack()
        self.result_label.pack()

    def get_submitted_flag(self):
        return self.submitted_flag.get()
    
    def update_bets_and_pot(self):
        # Update the text of the labels with the current bet and pot values
        self.player1_bet_label.config(text=f"Player 1 Bet: ${game.get_bet('Player1')}") 
        self.player1_money_label.config(text=f"Player 1 Money: ${game.get_money('Player1')}")
        self.player2_bet_label.config(text=f"Player 2 Bet: ${game.get_bet('Player2')}")
        self.player2_money_label.config(text=f"Player 2 Money: ${game.get_money('Player2')}")
        self.pot_label.config(text=f"Pot: ${game.get_pot()}")
        self.player_turn_label = tk.Label(self.root,text=f"{game.get_player_by_name(game.get_active_players()[game.current_player_index])['name']}'s turn")
        self.player_turn_label.place(x=690,y=0)

    def Fold(self):
        self.action = 'fold'
        self.process_call()
        self.process_user_input()   
    
    def process_call(self):
        self.submitted_flag.set(1)

    def Raise(self):
        self.raise_amount = 0
        self.action = 'raise'

        self.number_entry = tk.Entry(self.root, width=10)
        self.submit_button = tk.Button(self.root, text="Submit", command=self.process_input)

        # Pack the widgets
        self.number_entry.pack(pady=5)
        self.submit_button.pack()

        # Configure the Submit Button to call process_input when clicked
        self.submit_button.configure(command=self.process_input)

        # Delete existing content in Entry widget
        self.number_entry.delete(0, tk.END)

        # Call the function to process user input
        self.process_user_input()

    def process_user_input(self,*args):
        if self.round==1:
            if self.get_submitted_flag() == 0:
                self.root.wait_variable(self.submitted_flag)

            self.number_entry.destroy()
            self.submit_button.destroy()
            self.player_turn_label.pack_forget()

            game.decision_cycle(self.raise_amount)
            self.update_bets_and_pot()
            if self.round!=5:
                self.update_hand_display()
        elif self.round==2:
            if self.get_submitted_flag() == 0:
                self.root.wait_variable(self.submitted_flag)
            self.number_entry.destroy()
            self.submit_button.destroy()
            self.player_turn_label.pack_forget()
            self.update_hand_display()
            
            game.betting_round(self.raise_amount)
            self.update_bets_and_pot()
            
        elif self.round==3:
            if self.get_submitted_flag() == 0:
                self.root.wait_variable(self.submitted_flag)

            self.number_entry.destroy()
            self.submit_button.destroy()
            self.player_turn_label.pack_forget()

            gui.update_hand_display()
            game.betting_round(self.raise_amount)
            self.update_bets_and_pot()
        elif self.round==4:
            if self.get_submitted_flag() == 0:
                self.root.wait_variable(self.submitted_flag)

            self.number_entry.destroy()
            self.submit_button.destroy()
            self.player_turn_label.pack_forget()
            gui.update_hand_display()
            game.betting_round(self.raise_amount)
            self.update_bets_and_pot()
        elif self.round==5:
            if self.get_submitted_flag() == 0:
                self.root.wait_variable(self.submitted_flag)

            self.number_entry.destroy()
            self.submit_button.destroy()
            self.player_turn_label.pack_forget()
            gui.update_hand_display()
            game.betting_round(self.raise_amount)
            self.update_bets_and_pot()


    def Call(self):
        self.action = 'call'
        self.process_call()
        self.process_user_input()   

    def Hold(self):
        self.action = 'hold'
        self.process_call()
        self.process_user_input()
        
    
    def enable_button(self):  
        self.raise_button.config(state = tk.NORMAL)
        self.call_button.config(state = tk.NORMAL)
        self.fold_button.config(state = tk.NORMAL)
        self.hold_button.config(state = tk.NORMAL)
        return self.action

    def set_submitted_flag(self, value):
        self.submitted_flag.set(value)
    
    def update_community_cards_display(self):
        for element in self.community_frame.winfo_children():
            element.destroy()

        # Label for the community cards
        community_hand_text = ", ".join([str(card) for card in game.community_cards])
        community_cards_label = tk.Label(self.community_frame, text=f"Community Cards: {community_hand_text}")
        community_cards_label.pack(side=tk.TOP)

        for card in self.game.community_cards:
            suit_name = self.SUIT_MAPPING.get(card._suit, card._suit)
            tk.Label(self.community_frame, image=self.card_images[f"{card._face}_of_{suit_name}"]).pack(side=tk.LEFT)

    def update_hand_display(self):
        # Clear the current hand frames
        for element in self.player_hand_frame.winfo_children():
            element.destroy()

        for element in self.community_frame.winfo_children():
            element.destroy()

        for element in self.dealer_hand_frame.winfo_children():
            element.destroy()

        # Create frames for the dealer and the second player
        dealer_frame = tk.Frame(self.dealer_hand_frame)
        dealer_frame.pack(side=tk.TOP, pady=5)  # Adjust pady as needed
        

        community_frame = tk.Frame(self.community_frame)
        community_frame.pack(side=tk.TOP, pady=5)

        player1_frame = tk.Frame(self.player_hand_frame)
        player1_frame.pack(side=tk.TOP, pady=5)  # Adjust pady as needed
        
        dealer_hand_text = ", ".join([str(card) for card in self.game.players[1]['hand']])
        dealer_hand_label = tk.Label(dealer_frame, text=f"Player 2's Hand: {dealer_hand_text}")
        dealer_hand_label.pack(side=tk.TOP)  # Place it at the top

        # Label for the community cards
        community_hand_text = ", ".join([str(card) for card in self.game.community_cards])
        community_cards_label = tk.Label(community_frame, text=f"Community Cards: {community_hand_text}")
        community_cards_label.pack(side=tk.TOP)

        player_hand_text = ", ".join([str(card) for card in self.game.players[0]['hand']])
        player_hand_label = tk.Label(player1_frame, text=f"Player 1's Hand: {player_hand_text}")
        player_hand_label.pack(side=tk.TOP)

        # Show images for the first player 
        for card in (self.game.players[1]['hand']):  # Reverse the order
            suit_name = self.SUIT_MAPPING.get(card._suit, card._suit)
            tk.Label(dealer_frame, image=self.card_images[f"{card._face}_of_{suit_name}"]).pack(side=tk.LEFT)

        # Show images for the community cards
        for card in self.game.community_cards:
            suit_name = self.SUIT_MAPPING.get(card._suit, card._suit)
            tk.Label(self.community_frame, image=self.card_images[f"{card._face}_of_{suit_name}"]).pack(side=tk.LEFT)

        # Show images for the second player
        for card in self.game.players[0]['hand']:  # Assuming the second player is the second in the list
            suit_name = self.SUIT_MAPPING.get(card._suit, card._suit)
            tk.Label(player1_frame, image=self.card_images[f"{card._face}_of_{suit_name}"]).pack(side=tk.LEFT)
        
    def deal_initial_cards(self):
        for player in self.game.players: 
            self.game.deal_hands()

if __name__ == "__main__":
    game = PokerGame()
    game.add_player('Player1')
    game.add_player('Player2')
    gui = PokerGameGUI(game)
    gui.run()