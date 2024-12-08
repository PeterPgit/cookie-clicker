'''
Module Name: game.py
Purpose: This module is the main game code for the Cookie clicker game.
Inputs: None
Output: None
Additional code sources: 
Developers: Ian Wilson, Andrew Uriell, Peter Pham, Michael Oliver, Jack Youngquist
Date: 10/24/2024
Last Modified: 12/7/2024
'''

import pygame
import sys
import time
import math #functions handle floating points up to 10e308, if larger number precision is needed switch to gmpy2
import random
from datetime import datetime

# imports necessary functions and classes from the other python files
from shop import ShopUpgrade, shop_items, shop_upgrades
from cookie import Cookie
from save_game import save
from load_game import load
from sound import SoundManager
from cursor import Cursor
from prestige import *

# Initialize pygame's video system
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)  # Color for partition lines
BUTTON_COLOR = (100, 100, 255)  # Color for buttons

# directory for accessing the assets for the game
ASSETS_FILEPATH = './assets'

# gets the font for rendering text
def get_font(size):
    return pygame.font.SysFont(None, size)

from buttons import Button, SmallButton, LargeButton

# UIManager class responsible for rendering the screen of the game and handling some of the backend such as shop items and user balances
class UIManager:
    def __init__(self, achievement_manager, prestige):
        self.WIDTH = pygame.display.Info().current_w # sets the width to the current window's width for calculation purposes
        self.HEIGHT = pygame.display.Info().current_h # sets the height to the current window's height for calculation purposes
        self.cookie_count = 0
        self.upgrades_acquired = []
        # initializes the shop's items
        self.shop_items = shop_items
        # initializes the shop's upgrades
        self.shop_upgrades = shop_upgrades
        # Set up screen to dynamically fetch the display's width and height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)  # Allows resizing
        pygame.display.set_caption("Cookie Clicker")
        self.buttons = self.create_buttons() # renders the buttons on the screen
        self.font_size = int(self.WIDTH * 0.03)  # Dynamic font size based on width
        self.font = get_font(self.font_size)
        self.show_main_menu = True
        self.show_saves_menu = False
        self.show_new_game_menu = False
        self.selected_save = None #used to store what save we are using, used/changed when starting new game or loading game
        #self.new_game_slot = None #used to pass whick save text file to write to when starting new game
        self.show_settings_popup = False
        self.settings_pick = None
        self.main_menu_buttons = self.create_main_menu_buttons()  # Initialize with buttons
        self.save_button = SmallButton(self.WIDTH - int(self.WIDTH * 0.1), self.HEIGHT - int(self.HEIGHT * 0.1), "Save")
        self.sound_manager = SoundManager()
        self.no_cursor = pygame.mouse.set_visible(False)
        self.base_cookie_per_click = 1 # Start with 1 base cookie per click
        self.click_multiplier = 1.0     # Multiplier starts at 1.0 (no effect initially)
        self.cookie_per_click = self.base_cookie_per_click * self.click_multiplier
        self.scroll_offset = 0  # Initialize scroll offset
        self.max_scroll_offset = 0  # Initialize max scroll offset
        self.scroll_speed = 20  # Initialize scroll speed
        self.show_popup = False
        self.bonus_cookies = 0
        self.show_popup_cookie_earned = False
        self.achievement_manager = achievement_manager  # Initialize AchievementManager
        self.notification_duration = 3  # Duration to display each notification in seconds
        self.notification_start_time = None
        self.active_event_popup = None
        self.event_popup_end_time = None
        self.last_played_timestamp = None
        self.prestige = prestige


    """Check if a specific button was clicked based on label and mouse position."""
    def button_clicked(self, label, mouse_pos):
        self.sound_manager.play_sound("menu-click")
        for button in self.main_menu_buttons:
            if button.text == label and button.is_clicked(mouse_pos):
                return True
        return False
    
    """Create main menu buttons and positions them on the screen."""
    def create_main_menu_buttons(self):
        button_labels = [("Continue", 'assets/menu/continue_button/continue_button_rectangle2.png'),
                         ("New Game", 'assets/menu/new_button/new_button_rectangle1.png'),
                         ("Settings", 'assets/menu/options_button/options_button_rectangle2.png'),
                         ("Exit", 'assets/menu/exit_button/exit_button_rectangle2.png')]
        buttons = []
        # renders each button on the screen with hardcoded position coordinates
        for idx, label in enumerate(button_labels):
            y_pos = int(self.HEIGHT * 0.2) + idx * int(self.HEIGHT * 0.18)
            button_width = int(self.WIDTH * 0.3)
            button_height = int(self.HEIGHT * 0.2)
            x_pos = (self.WIDTH - button_width) // 2
            button = LargeButton(self.screen, x_pos, y_pos, label[0], button_width, button_height, label[1])
            buttons.append(button)
        return buttons
    
    # Function to draw text
    def draw_text(self, text, font, color, x, y):
        text_obj = font.render(text, True, color)
        self.screen.blit(text_obj, (x, y)) # blit is used to draw an object onto the screen

    # function to render the buttons on the screen for each of the shop's items
    def create_buttons(self):
        buttons = []
        all_shop_items = {**self.shop_items, **self.shop_upgrades}
        button_height = int(self.HEIGHT * 0.07)
        button_margin = int(self.HEIGHT * 0.01)  # Add a margin between buttons
        total_height = len(all_shop_items) * (button_height + button_margin)
        self.max_scroll_offset = max(0, total_height - int(self.HEIGHT * 0.8))  # Calculate max scroll offset

        for idx, (k, v) in enumerate(all_shop_items.items()):
            # Check affordability before adding the button
            current_price = int(v.base_cost * (1.15 ** v.purchased_count))  # Calculate the price
            if self.cookie_count < current_price:  # Skip if player cannot afford
                continue

            button_width = int(self.WIDTH * 0.15)
            button_y = int(self.HEIGHT * 0.15) + idx * (button_height + button_margin) - self.max_scroll_offset
            button = LargeButton(
                self.screen, 
                self.WIDTH - int(self.WIDTH * 0.25), 
                button_y, 
                v.name, button_width, button_height,
                v.image
            )
            buttons.append((button, v))
        return buttons


    # function to handle to cookies earned per click
    def handle_cookie_click(self):
        self.cookie_count += self.cookie_per_click
        self.sound_manager.play_sound("click")
        # print(f"Cookie clicked! Total cookies: {self.cookie_count}")  # Log message for cookie clicks
        self.buttons = self.create_buttons()

    # function to handle the purchase of upgrades from the shop
    def handle_shop_click(self, mouse_pos):
        for button, item in self.buttons:
            if button.is_clicked(mouse_pos):
                # Calculate the current price
                current_price = int(item.base_cost * (1.15 ** item.purchased_count))

                # Handle custom price increment for Click Multipliers and Increase Clicks (commented out for now)

                #if item.name.startswith("Click Multiplier") or item.name.startswith("Increase Click"):
                #    current_price = item.base_cost

                # Only proceed if the player has enough cookies
                if self.cookie_count >= current_price:
                    # Deduct the cookie count and update purchase state
                    self.cookie_count -= current_price
                    item.purchased_count += 1  # Increment the purchase count

                    # Custom price increment for "Click Multiplier 1"
                    if item.name == "Click Multiplier 1":
                        item.base_cost += 1000

                    # Custom price increment for "Click Multiplier 2"
                    if item.name == "Click Multiplier 2":
                        item.base_cost += 2500

                    # Custom price increment for "Click Multiplier 3"
                    if item.name == "Click Multiplier 3":
                        item.base_cost += 5000

                    # Custom price increment for "Increase Click 1"
                    if item.name == "Increase Click 1":
                        item.base_cost += 50

                    # Custom price increment for "Increase Click 2"
                    if item.name == "Increase Click 2":
                        item.base_cost += 150

                    # Custom price increment for "Increase Click 3"
                    if item.name == "Increase Click 3":
                        item.base_cost += 300

                    # Add the item to upgrades_acquired if not already in the list
                    if item not in self.upgrades_acquired:
                        self.upgrades_acquired.append(item)

                    # Update button text with the new calculated price
                    button.text = f"{current_price} cookies"

                    # Apply any effects (CPC or CPS) associated with the item
                    if item.name.startswith("Click Multiplier"):
                        self.click_multiplier *= item.cpc
                    elif item.name.startswith("Increase Click"):
                        self.base_cookie_per_click += item.cpc
                    elif item.cpc is not None:
                        self.base_cookie_per_click += item.cpc

                    # Recalculate cookies per click
                    self.cookie_per_click = self.base_cookie_per_click * self.click_multiplier
                    self.sound_manager.play_sound("shop")

                    # Refresh the buttons after purchase to show/hide based on affordability
                    button.text = f"{self.simplify_number(current_price)} cookies"
                    self.buttons = self.create_buttons()  # Ensure dynamic update of button prices


    # returns the amount of cookies the user should be earning per second based on the purchased items
    def cookies_per_second(self):
        return sum(item.cps * item.purchased_count for item in self.shop_items.values() if item.cps != None) + \
        sum(item.cps * item.purchased_count for (key,item) in self.prestige.get_shop_items() if item.cps != None)
    
    # generates Latin suffix from number given by simplify number
    def get_suffix(self, illion):
        """
        Dynamically generates the suffix for a given index, using a Latin prefix lists.
        Includes short forms for Million, Billion, etc., as part of the prefixes, Latin prefixes for tens and units in the tens.
        """

        first_latin_units = [
            "m", "b", "tr", "quadr", "quint", "sext", "sept", 
            "oct", "non"
        ]
        n_latin_units = [
            "un", "duo", "tre", "quattuor", "quin", "se", "septen", 
            "octo", "novem"
        ]
        latin_tens = [
            "dec", "vigint", "trigint", "quadragint", "quinquagint", 
            "sexagint", "septuagint", "octogint", "nonagint"
        ]
        if illion < 10:
            return f"{first_latin_units[illion-1]}illion"
        elif illion < 100:
            digit_list = [int(digit) for digit in str(illion)]
            if illion % 10 == 0:
                return f"{latin_tens[digit_list[0]-1]}illion"
            else:
                return f"{n_latin_units[digit_list[1]-1]}{latin_tens[digit_list[0]-1]}illion"
        elif illion == 100:
            return "centillion"
        #largest suffix pygame can generate up to
        elif illion == 101:
            return "uncentillion"
    
    #Uses get_suffix to round and generate latin names for large numbers
    def simplify_number(self, num):
        if num < 1_000_000: # no need for latin suffix if less than 1 million
            return f"{num:.1f}"

        # Get the base-10 exponent using math.log10
        exponent = math.log10(num)
        
        #try block for if the number reaches beyond pygames range
        try:
            # Calculate the index for suffix (group every 3 powers of 10)
            suffix_index = int(exponent // 3) - 1  # Subtract 1 for searching through array (0-9)
        except:
            return "Infinity"
        # Adjust number to the corresponding magnitude
        scaled_num = num / (10 ** ((suffix_index + 1) * 3))  # Adjust for skipped indices

        # Dynamically generate suffix
        suffix = self.get_suffix(suffix_index)

        return f"{scaled_num:.3f} {suffix.capitalize()}" #return the number rounded to 3 decimal places with latin suffix following


    # renders the user's balance on the top left of the screen
    def draw_stats(self, screen):
        self.draw_text(f"Cookies: {self.simplify_number(self.cookie_count)}", self.font, BLACK, int(self.WIDTH * 0.01), int(self.HEIGHT * 0.01))
        self.draw_text(f"{self.simplify_number(self.cookies_per_second())} cookies per second", self.font, BLACK, int(self.WIDTH * 0.01), int(self.HEIGHT * 0.05))

    # renders the purchased item's to the middle column.
    def draw_upgrades(self, screen):
        font_size = int(self.WIDTH * 0.03)  # Dynamic font size based on width
        font = get_font(font_size)
        self.draw_text("Upgrades Acquired:", font, BLACK, int(self.WIDTH * 0.4), int(self.HEIGHT * 0.05))

        # Draw the "Pop-up Menu" button (to the right of the upgrades text)
        button_width = int(self.WIDTH * 0.1)
        button_height = int(self.HEIGHT * 0.05)
        button_x = int(self.WIDTH * 0.5) + 150  # Position it to the right of the text
        button_y = int(self.HEIGHT * 0.005)
        self.popup_button = LargeButton(screen, button_x, button_y, "Open Menu", button_width, button_height)

        # Draw the button on the screen
        self.popup_button.draw(screen)

        font_size = int(self.WIDTH * 0.015)  # Dynamic font size based on width
        font = get_font(font_size)
        if self.upgrades_acquired:
            for idx, upgrade in enumerate(self.upgrades_acquired):
                if upgrade.cpc is None:
                    self.draw_text(f"{upgrade.name} (CPS: {upgrade.cps}): {upgrade.purchased_count}", font, BLACK, int(self.WIDTH * 0.4), int(self.HEIGHT * 0.15) + idx * int(self.HEIGHT * 0.05))
                else:
                    self.draw_text(f"{upgrade.name} (CPC: {upgrade.cpc}): {upgrade.purchased_count}", font, BLACK, int(self.WIDTH * 0.4), int(self.HEIGHT * 0.15) + idx * int(self.HEIGHT * 0.05))

    def draw_popup_cookie_earned(self, screen):
        if self.show_popup_cookie_earned:
            popup_width = int(self.WIDTH * 0.7)
            popup_height = int(self.HEIGHT * 0.3)
            popup_x = (self.WIDTH - popup_width) // 2
            popup_y = (self.HEIGHT - popup_height) // 2  # Center the popup vertically and horizontally

            # Draw the popup background
            pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
            pygame.draw.rect(screen, BLACK, (popup_x, popup_y, popup_width, popup_height), 3)  # Border

            # Draw the title of the popup
            title_font = get_font(int(popup_height * 0.1))
            title_text = "Welcome Back!"
            self.draw_text(
                title_text, 
                title_font, 
                BLACK, 
                popup_x + popup_width // 2 - title_font.size(title_text)[0] // 2, 
                popup_y + 10
            )

            # Display bonus cookies earned
            message_font = get_font(int(popup_height * 0.08))
            message_text = f"You've earned {self.simplify_number(self.bonus_cookies)} cookies while you were away ({self.cookies_per_second()} cookies per offline hour)!"
            self.draw_text(
                message_text, 
                message_font, 
                BLACK, 
                popup_x + popup_width // 2 - message_font.size(message_text)[0] // 2, 
                popup_y + popup_height // 2 - message_font.size(message_text)[1] // 2
            )

            # Display bonus cookies earned
            message_font = get_font(int(popup_height * 0.08))
            message_text = f"Time Last Played: {datetime.fromtimestamp(float(self.last_played_timestamp)).strftime('%Y-%m-%d %H:%M:%S CST')}"
            self.draw_text(
                message_text, 
                message_font, 
                BLACK, 
                popup_x + popup_width // 2 - message_font.size(message_text)[0] // 2, 
                popup_y + popup_height // 2 - message_font.size(message_text)[1] // 2 + 25
            )

            # Define and draw the "Close" button
            button_width = int(popup_width * 0.2)
            button_height = int(popup_height * 0.15)
            button_x = popup_x + popup_width // 2 - button_width // 2
            button_y = popup_y + popup_height - button_height - 10
            close_button = LargeButton(screen, button_x, button_y, "Close", button_width, button_height)
            close_button.draw(screen)

            # Handle button click
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]

            if close_button.is_clicked(mouse_pos) and mouse_pressed:
                if not hasattr(self, '_button_clicked') or not self._button_clicked:
                    self._button_clicked = True
                    self.show_popup_cookie_earned = False  # Close the popup

            if not mouse_pressed and hasattr(self, '_button_clicked'):
                self._button_clicked = False  # Reset the click lock



    # Modify this method to handle button clicks properly in the popup menu
    def draw_popup_menu(self, screen):
        if self.show_popup:
            popup_width = int(self.WIDTH * 0.7)
            popup_height = int(self.HEIGHT * 1)
            popup_x = (self.WIDTH - popup_width) 
            popup_y = (self.HEIGHT - popup_height) // 2  # Center the popup vertically
            
            # Draw the popup background
            pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))

            # Draw the title of the popup
            title_font = get_font(int(popup_height * 0.1))
            title_text = "Options"
            self.draw_text(title_text, title_font, BLACK, popup_x + popup_width // 2 - title_font.size(title_text)[0] // 2, popup_y + 10)

            # Define the buttons and their labels
            button_labels = ["Save Game", "Close Menu", "Toggle Sound", "Quit"]
            
            # Set button properties
            button_width = int(popup_width * 0.2)  # Adjust the button width based on the popup size
            button_height = int(popup_height * 0.1)  # Set a reasonable button height

            # Calculate the vertical position of the buttons (one row of buttons at the bottom)
            button_y = popup_y + popup_height - button_height - 10
            
            # Space out the buttons horizontally based on the number of buttons
            spacing = (popup_width - len(button_labels) * button_width) // (len(button_labels) + 1)  # Space between buttons

            # Loop through the button labels and create the buttons
            for index, label in enumerate(button_labels):
                # Calculate the x-position of the current button
                button_x = popup_x + (index + 1) * spacing + index * button_width
                button = LargeButton(screen, button_x, button_y, label, button_width, button_height)
                button.draw(screen)

                # Handle the button click based on its label
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button pressed (0 = left, 1 = middle, 2 = right)

                # Ensure the click is only handled once (we prevent double-clicking the button)
                if button.is_clicked(mouse_pos) and mouse_pressed:
                    if not hasattr(self, '_button_clicked') or not self._button_clicked:
                        self._button_clicked = True  # Lock the button to avoid multiple triggers
                        self.sound_manager.play_sound("menu-click")
                        if label == "Save Game":
                            save(self, self.selected_save)  # Handle the save game action
                        elif label == "Close Menu":
                            self.show_popup = False  # Close the pop-up when the button is clicked
                        elif label == "Toggle Sound":
                            self.sound_manager.toggle_sound()  # Toggle sound on/off
                            self.sound_manager.play_music()
                        elif label == "Quit":
                            print("I quit")
                            pygame.quit()  # Quit the game
                            quit()  # Close the game completely
                    else:
                        # If the button was already clicked, do nothing (debounced)
                        pass

                # Reset the click lock when the mouse button is released
                if not mouse_pressed:
                    if hasattr(self, '_button_clicked') and self._button_clicked:
                        self._button_clicked = False  # Unlock the button when the button is released

            # Draw achievements
            self.draw_achievements(screen, popup_x, popup_y + int(popup_height * 0.1), popup_width)

            # Draw analytics
            self.draw_analytics(screen, popup_x, popup_y + int(popup_height * 0.3), popup_width)
        
            return True
        else:
            return False

    def draw_achievements(self, screen, x, y, width):
        #print(f"Achievements state: {self.achievement_manager.achievements}")
        font_size = int(self.WIDTH * 0.02)  # Dynamic font size based on width
        font = get_font(font_size)
        self.draw_text("Achievements:", font, BLACK, x + 10, y)

        # Access the current state of achievements
        for idx, (name, data) in enumerate(self.achievement_manager.achievements.items()):
            status = "Unlocked" if data["achieved"] else "Locked"
            # print(f"Drawing {name}: {status}")  # Debug print
            achievement_text = f"{name}: {status}"
            self.draw_text(achievement_text, font, BLACK, x + 10, y + (idx + 1) * int(self.HEIGHT * 0.05))

    # draws the save file analytics
    def draw_analytics(self, screen, x, y, width):
        font_size = int(self.WIDTH * 0.02)  # Dynamic font size based on width
        font = get_font(font_size)
        self.draw_text("Analytics:", font, BLACK, x + 10, y)

        stats = {
            "Cookies": f'{self.simplify_number(self.cookie_count)}',
            "Cookies Per Click": f'{self.simplify_number(self.cookie_per_click)}',
            "Cookies Per Second": f'{self.simplify_number(self.cookies_per_second())}'
        }
        purchases = {
            "Extra Hands": self.shop_items["Extra Hands"].purchased_count,
            "Cursor": self.shop_items["Cursor"].purchased_count,
            "Grandma": self.shop_items["Grandma"].purchased_count,
            "Farm": self.shop_items["Farm"].purchased_count,
            "Factory": self.shop_items["Factory"].purchased_count,
            "Click Multiplier 1": self.shop_upgrades["Click Multiplier 1"].purchased_count,
            "Click Multiplier 2": self.shop_upgrades["Click Multiplier 2"].purchased_count,
            "Click Multiplier 3": self.shop_upgrades["Click Multiplier 3"].purchased_count,
            "Increase Click 1": self.shop_upgrades["Increase Click 1"].purchased_count,
            "Increase Click 2": self.shop_upgrades["Increase Click 2"].purchased_count,
            "Increase Click 3": self.shop_upgrades["Increase Click 3"].purchased_count
        }
        # prints save stats
        for idx, (name, purchased_count) in enumerate(stats.items()):
            text = f"{name}: {purchased_count}"
            self.draw_text(text, font, BLACK, x + 10, y + (idx + 1) * int(self.HEIGHT * 0.05))

        # prints save purchase stats
        for idx, (name, purchased_count) in enumerate(purchases.items()):
            text = f"{name}: {purchased_count}"
            self.draw_text(text, font, BLACK, x + 500, y + (idx + 1) * int(self.HEIGHT * 0.05))

    # draws the shop section of the screen
    def draw_shop(self, screen):
        font_size = int(self.WIDTH * 0.03)
        font = get_font(font_size)
        self.draw_text("Shop:", font, BLACK, int(self.WIDTH * 0.75), int(self.HEIGHT * 0.05))
        
        # Draw shop items
        font_size = int(self.WIDTH * 0.015) #change shop text size
        font = get_font(font_size)
        for button, item in self.buttons:
            if 0 <= button.y <= self.HEIGHT:  # Only draw buttons within the visible area
                current_price = int(item.base_cost * (1.15 ** item.purchased_count))
                button.text = f"{self.simplify_number(current_price)} cookies"
                button.draw(screen, font)



    def draw_event_popup(self, screen):
        if self.active_event_popup and time.time() < self.event_popup_end_time:
            popup_width = int(self.WIDTH * 0.5)
            popup_height = int(self.HEIGHT * 0.1)
            popup_x = (self.WIDTH - popup_width) // 2
            popup_y = int(self.HEIGHT * 0.1)

            # Draw the popup background
            pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
            pygame.draw.rect(screen, BLACK, (popup_x, popup_y, popup_width, popup_height), 2)  # Border

            # Draw the event text
            font = get_font(int(self.HEIGHT * 0.05))
            self.draw_text(self.active_event_popup, font, BLACK, popup_x + 10, popup_y + 10)
        else:
            self.active_event_popup = None  # Clear the popup when time expires


    # Draws vertical lines to partition the screen
    def draw_partitions(self, screen):
        pygame.draw.line(screen, GRAY, (self.WIDTH * 0.33, 0), (self.WIDTH * 0.33, self.HEIGHT), 2)  # Left partition
        pygame.draw.line(screen, GRAY, (self.WIDTH * 0.66, 0), (self.WIDTH * 0.66, self.HEIGHT), 2)  # Right partition    

    # renders the main menu screen when the user starts the game
    def draw_main_menu(self):
        # Draw the title
        #title_font = get_font(int(self.HEIGHT * 0.1))
        #self.draw_text("KU Cookie Clicker", title_font, BLACK, self.WIDTH // 2 - title_font.size("KU Cookie Clicker")[0] // 2, int(self.HEIGHT * 0.1))

        # Draw menu buttons
        for button in self.main_menu_buttons:
            button.font = get_font(0)
            button.draw(self.screen)


    # placeholder for rendering the save slots screen
    def draw_save_slots_popup(self, screen):
        if self.show_saves_menu:
            popup_width = int(self.WIDTH * 0.98)
            popup_height = int(self.HEIGHT * 0.98)
            popup_x = (self.WIDTH - popup_width) // 2
            popup_y = (self.HEIGHT - popup_height) // 2  # Center the popup vertically
            
            # Draw the popup background
            pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))

            # Draw the title of the popup
            title_font = get_font(int(popup_height * 0.1))
            title_text = "Save Slots"
            self.draw_text(title_text, title_font, BLACK, popup_x + popup_width // 2 - title_font.size(title_text)[0] // 2, popup_y + 10)

            # Define the buttons and their labels
            button_labels = ["Save 1", "Save 2", "Save 3", "Close"]
            
            # Set button properties
            button_width = int(popup_width * 0.2)  # Adjust the button width based on the popup size
            button_height = int(popup_height * 0.1)  # Set a reasonable button height

            # Calculate the vertical position of the buttons (one row of buttons at the bottom)
            button_y = popup_y + popup_height - button_height - 10
            
            # Space out the buttons horizontally based on the number of buttons
            spacing = (popup_width - len(button_labels) * button_width) // (len(button_labels) + 1)  # Space between buttons

            # Loop through the button labels and create the buttons
            for index, label in enumerate(button_labels):
                # Calculate the x-position of the current button
                button_x = popup_x + (index + 1) * spacing + index * button_width
                button = LargeButton(screen, button_x, button_y, label, button_width, button_height)
                button.draw(screen)

                # Handle the button click based on its label
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button pressed (0 = left, 1 = middle, 2 = right)

                # Ensure the click is only handled once (we prevent double-clicking the button)
                if button.is_clicked(mouse_pos) and mouse_pressed:
                    print("Trying a button")
                    if not hasattr(self, '_button_clicked') or not self._button_clicked:
                        self._button_clicked = True  # Lock the button to avoid multiple triggers
                        self.sound_manager.play_sound("menu-click")
                        if label == "Save 1":
                            self.selected_save = 'save1.txt'
                        elif label == "Save 2":
                            self.selected_save = 'save2.txt'
                        elif label == "Save 3":
                            self.selected_save = 'save3.txt'
                        elif label == "Close":
                            self.show_saves_menu = False  # Close the pop-up when the button is clicked
                            
                    else:
                        # If the button was already clicked, do nothing (debounced)
                        pass

                # Reset the click lock when the mouse button is released
                if not mouse_pressed:
                    if hasattr(self, '_button_clicked') and self._button_clicked:
                        self._button_clicked = False  # Unlock the button when the button is released

    def draw_new_game_popup(self, screen):
        if self.show_new_game_menu:
            popup_width = int(self.WIDTH * 0.98)
            popup_height = int(self.HEIGHT * 0.98)
            popup_x = (self.WIDTH - popup_width) // 2
            popup_y = (self.HEIGHT - popup_height) // 2  # Center the popup vertically
            
            # Draw the popup background
            pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))

            # Draw the title of the popup
            title_font = get_font(int(popup_height * 0.1))
            title_text = "New Game"
            self.draw_text(title_text, title_font, BLACK, popup_x + popup_width // 2 - title_font.size(title_text)[0] // 2, popup_y + 10)

            # Define the buttons and their labels
            button_labels = ["Save 1", "Save 2", "Save 3", "Close"]
            
            # Set button properties
            button_width = int(popup_width * 0.2)  # Adjust the button width based on the popup size
            button_height = int(popup_height * 0.1)  # Set a reasonable button height

            # Calculate the vertical position of the buttons (one row of buttons at the bottom)
            button_y = popup_y + popup_height - button_height - 10
            
            # Space out the buttons horizontally based on the number of buttons
            spacing = (popup_width - len(button_labels) * button_width) // (len(button_labels) + 1)  # Space between buttons

            # Loop through the button labels and create the buttons
            for index, label in enumerate(button_labels):
                # Calculate the x-position of the current button
                button_x = popup_x + (index + 1) * spacing + index * button_width
                button = LargeButton(screen, button_x, button_y, label, button_width, button_height)
                button.draw(screen)

                # Handle the button click based on its label
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button pressed (0 = left, 1 = middle, 2 = right)

                # Ensure the click is only handled once (we prevent double-clicking the button)
                if button.is_clicked(mouse_pos) and mouse_pressed:
                    print("Trying a button")
                    if not hasattr(self, '_button_clicked') or not self._button_clicked:
                        self._button_clicked = True  # Lock the button to avoid multiple triggers
                        self.sound_manager.play_sound("menu-click")
                        if label == "Save 1":
                            self.selected_save = 'save1.txt'
                        elif label == "Save 2":
                            self.selected_save = 'save2.txt'
                        elif label == "Save 3":
                            self.selected_save = 'save3.txt'
                        elif label == "Close":
                            self.show_new_game_menu = False  # Close the pop-up when the button is clicked
                    else:
                        # If the button was already clicked, do nothing (debounced)
                        pass

                # Reset the click lock when the mouse button is released
                if not mouse_pressed:
                    if hasattr(self, '_button_clicked') and self._button_clicked:
                        self._button_clicked = False  # Unlock the button when the button is released
                        
    def handle_new_game_click(self):
        """Toggles the visibility of the save slots"""
        self.show_new_game_menu = not self.show_new_game_menu
    def handle_save_slot_click(self):
        """Toggles the visibility of the save slots"""
        self.show_saves_menu = not self.show_saves_menu #toggle saves menu pop-up

    def handle_popup_click(self):
        """Toggles the visibility of the pop-up menu."""
        self.show_popup = not self.show_popup  # Toggle the pop-up menu
    
    def handle_setting_popup_click(self):
        """Toggles the visibility of the pop-up menu."""
        self.show_settings_popup = not self.show_settings_popup  # Toggle the pop-up menu
        
    # renders the settings screen -- TWEAK ME
    def draw_settings_popup(self, screen):
        if self.show_settings_popup:
            popup_width = int(self.WIDTH * 0.98)
            popup_height = int(self.HEIGHT * 0.98)
            popup_x = (self.WIDTH - popup_width) // 2
            popup_y = (self.HEIGHT - popup_height) // 2  # Center the popup vertically
            
            # Draw the popup background
            pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))

            # Draw the title of the popup
            title_font = get_font(int(popup_height * 0.1))
            title_text = "Settings"
            self.draw_text(title_text, title_font, BLACK, popup_x + popup_width // 2 - title_font.size(title_text)[0] // 2, popup_y + 10)

            # Add control explanations
            control_font = get_font(int(popup_height * 0.05))
            control_texts = [
                "Controls:",
                "- Click the large cookie to earn cookies",
                "- Use the in-game menu to save the game",
                "- Press 'ESC' to toggle the main menu",
                "- Purchase shop items to increase Cookies Per Click (CPC) and Cookies Per Second (CPS)"
            ]
            for i, text in enumerate(control_texts):
                self.draw_text(text, control_font, BLACK, popup_x + 20, popup_y + int(popup_height * 0.15) + i * int(popup_height * 0.06))

            # Define the buttons and their labels
            button_labels = ["Save Game", "Toggle Music", "Toggle Sound", "Close Menu"]
            
            # Set button properties
            button_width = int(popup_width * 0.2)  # Adjust the button width based on the popup size
            button_height = int(popup_height * 0.1)  # Set a reasonable button height

            # Calculate the vertical position of the buttons (one row of buttons at the bottom)
            button_y = popup_y + popup_height - button_height - 10
            
            # Space out the buttons horizontally based on the number of buttons
            spacing = (popup_width - len(button_labels) * button_width) // (len(button_labels) + 1)  # Space between buttons

            # Loop through the button labels and create the buttons
            for index, label in enumerate(button_labels):
                # Calculate the x-position of the current button
                button_x = popup_x + (index + 1) * spacing + index * button_width
                button = LargeButton(screen, button_x, button_y, label, button_width, button_height)
                button.draw(screen)

                # Handle the button click based on its label
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button pressed (0 = left, 1 = middle, 2 = right)

                # Ensure the click is only handled once (we prevent double-clicking the button)
                if button.is_clicked(mouse_pos) and mouse_pressed:
                    if not hasattr(self, '_button_clicked') or not self._button_clicked:
                        self._button_clicked = True  # Lock the button to avoid multiple triggers
                        self.sound_manager.play_sound("menu-click")
                        if label == "Save Game":
                            self.settings_pick = 1  # Handle the save game action
                        elif label == "Toggle Music":
                            self.settings_pick = 2  
                        elif label == "Toggle Sound":
                            self.settings_pick = 3  
                            #self.sound_manager.play_music()
                        elif label == "Close Menu":
                            self.settings_pick = 4  # Quit the game
                            #quit()  # Close the game completely
                    else:
                        # If the button was already clicked, do nothing (debounced)
                        pass

                # Reset the click lock when the mouse button is released
                if not mouse_pressed:
                    if hasattr(self, '_button_clicked') and self._button_clicked:
                        self._button_clicked = False  # Unlock the button when the button is released


    # renders the sliders used in the settings menu
    def draw_slider(self, label, x, y, popup_width, popup_height):
        slider_width = int(popup_width * 0.6)
        slider_height = int(popup_height * 0.1)

        # Draw label
        slider_font = get_font(int(slider_height * 0.5))
        text_surface = slider_font.render(label, True, BLACK)
        self.screen.blit(text_surface, (x, y))

        # Draw slider bar
        pygame.draw.rect(self.screen, BLACK, (x + int(popup_width * 0.2), y, slider_width, slider_height // 5))

        # Draw mute checkbox
        checkbox_side = slider_height
        checkbox_x = x + int(popup_width * 0.8)
        checkbox_y = y
        pygame.draw.rect(self.screen, BLACK, (checkbox_x, checkbox_y, checkbox_side, checkbox_side))


    def draw_gambling_popup(self, screen, random_event_manager):
        if random_event_manager.show_gambling_popup:
            popup_width = int(self.WIDTH * 0.7)
            popup_height = int(self.HEIGHT * 0.3)
            popup_x = (self.WIDTH - popup_width) // 2
            popup_y = (self.HEIGHT - popup_height) // 2

            # Draw the popup background
            pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
            pygame.draw.rect(screen, BLACK, (popup_x, popup_y, popup_width, popup_height), 3)  # Border

            # Draw the title of the popup
            title_font = get_font(int(popup_height * 0.1))
            title_text = "Gambling Event!"
            self.draw_text(
                title_text,
                title_font,
                BLACK,
                popup_x + popup_width // 2 - title_font.size(title_text)[0] // 2,
                popup_y + 10
            )

            # Display the options: "Risk It" and "Nah"
            button_width = int(popup_width * 0.2)
            button_height = int(popup_height * 0.15)
            button_y = popup_y + popup_height - button_height - 10

            # Risk It button
            risk_button_x = popup_x + popup_width // 2 - button_width - 10
            risk_button = LargeButton(screen, risk_button_x, button_y, "Risk It", button_width, button_height)
            risk_button.draw(screen)

            # Nah button
            nah_button_x = popup_x + popup_width // 2 + 10
            nah_button = LargeButton(screen, nah_button_x, button_y, "Nah", button_width, button_height)
            nah_button.draw(screen)

            # Handle button click
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]

            if risk_button.is_clicked(mouse_pos) and mouse_pressed:
                if not hasattr(self, '_button_clicked') or not self._button_clicked:
                    random_event_manager.resolve_gambling_event(self, risk=True)  # Handle risk
                    self._button_clicked = True

            if nah_button.is_clicked(mouse_pos) and mouse_pressed:
                if not hasattr(self, '_button_clicked') or not self._button_clicked:
                    random_event_manager.resolve_gambling_event(self, risk=False)  # Handle no risk
                    self._button_clicked = True

            if not mouse_pressed:
                self._button_clicked = False  # Reset the click lock


        
    def draw_scroll_bar(self, screen):
        bar_width = int(self.WIDTH * 0.02)
        bar_height = int(self.HEIGHT * 0.8)
        bar_x = self.WIDTH - bar_width - 10
        bar_y = int(self.HEIGHT * 0.15)
        
        # Draw the scroll bar background
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Calculate the scroll handle position
        handle_height = max(20, bar_height * (bar_height / (bar_height + self.max_scroll_offset)))
        
        # Prevent division by zero
        if self.max_scroll_offset > 0:
            handle_y = bar_y + (self.scroll_offset / self.max_scroll_offset) * (bar_height - handle_height)
        else:
            handle_y = bar_y  # Default position if no scrolling is needed
        
        # Draw the scroll handle
        pygame.draw.rect(screen, BLACK, (bar_x, handle_y, bar_width, handle_height))

    def run_main_menu(self):
        # Display either the main menu, saves, or settings based on flags
        if self.show_main_menu:
            self.draw_main_menu()
        elif self.show_saves_menu:
            self.draw_save_slots()  
        elif self.show_new_game_menu:
            self.draw_new_game_popup()
        elif self.show_settings_popup:
            self.draw_settings_popup()

    def start_new_game(self):
        # Reset cookie count and upgrades
        self.cookie_count = 0
        self.upgrades_acquired = []

        # Reset each shop item's purchase count and price
        for item in self.shop_items.values():
            item.purchased_count = 0
            item.cost = item.base_cost  # Reset to the initial base price

        # Reset each shop upgrade's purchase count and price
        for upgrade in self.shop_upgrades.values():
            upgrade.purchased_count = 0
            upgrade.cost = upgrade.base_cost  # Reset to the original price

        # Reset cookies per click and multiplier
        self.base_cookie_per_click = 1
        self.click_multiplier = 1.0
        self.cookie_per_click = self.base_cookie_per_click * self.click_multiplier

        # Reset any other game-related state, such as showing main menu or other flags
        self.show_main_menu = False

    def draw_notifications(self, screen):
        if self.achievement_manager.notifications:
            if self.notification_start_time is None:
                self.notification_start_time = time.time()

            current_time = time.time()
            if current_time - self.notification_start_time < self.notification_duration:
                notification = self.achievement_manager.notifications[0]
                font_size = int(self.WIDTH * 0.03)
                font = get_font(font_size)
                text_surface = font.render(notification, True, BLACK)
                text_rect = text_surface.get_rect(center=(self.WIDTH // 2, self.HEIGHT * 0.1))
                pygame.draw.rect(screen, GRAY, text_rect.inflate(20, 20))  # Background for the notification
                screen.blit(text_surface, text_rect)
            else:
                self.achievement_manager.notifications.pop(0)
                self.notification_start_time = None

    def draw_prestige_menu_button(self):
        # Draw the "Pop-up Menu" button (to the right of the upgrades text)
        button_width = int(self.WIDTH * 0.1)
        button_height = int(self.HEIGHT * 0.05)
        button_x = int(self.WIDTH * 0.25) + 150  # Position it to the right of the text
        button_y = int(self.HEIGHT * 0.005)

        self.prestige_button = LargeButton(self.screen, button_x, button_y, "Prestige Menu", button_width, button_height)

        # Draw the button on the screen
        self.prestige_button.draw(self.screen)

class AchievementManager:
    def __init__(self):
        self.achievements = {
            "First Click": {"description": "Make your first click", "achieved": False},
            "100 Cookies": {"description": "Collect 100 cookies", "achieved": False},
            # Add more achievements as needed
        }
        self.notifications = []  # List to store active notifications

    def check_achievements(self, cookie_count):
        if cookie_count >= 1 and not self.achievements["First Click"]["achieved"]:
            self.achievements["First Click"]["achieved"] = True
            self.notifications.append("Achievement Unlocked: First Click!")
            print("First Click achievement unlocked!")  # Debug print
        if cookie_count >= 100 and not self.achievements["100 Cookies"]["achieved"]:
            self.achievements["100 Cookies"]["achieved"] = True
            self.notifications.append("Achievement Unlocked: 100 Cookies!")
            print("100 Cookies achievement unlocked!")  # Debug print
        # Add more checks as needed

    def get_notifications(self):
        return self.notifications

    def clear_notifications(self):
        self.notifications.clear()

class RandomEventManager:
    def __init__(self):
        self.events = ["Golden Cookie", "Cookie Storm", "Gambling"]
        self.active_events = {}  # Track active events and their end times
        self.event_multipliers = {}  # Track multipliers for each active event
        self.show_gambling_popup = False
        self.event_lock = False  # Lock to prevent overlapping events



    def trigger_event(self, ui_manager):
        if hasattr(self, "event_lock") and self.event_lock:  # Prevent overlapping events
            print("Event lock is active; skipping event.")
            return

        self.event_lock = True
        event = random.choice(self.events)
        golden_duration = 10  # Golden Cookie timer
        storm_duration = 15 # Storm Cookie timer

        if event == "Golden Cookie":
            print("Golden Cookie appeared! 10x clicks for 10 seconds!")
            self.active_events["Golden Cookie"] = time.time() + golden_duration
            self.event_multipliers["Golden Cookie"] = 10
            ui_manager.cookie_per_click *= self.event_multipliers["Golden Cookie"]

            # Set the event popup
            ui_manager.active_event_popup = "Golden Cookie! 10x clicks for 10 seconds!"
            ui_manager.event_popup_end_time = time.time() + 3  # Show for 3 seconds

        elif event == "Cookie Storm":
            print("Cookie Storm activated! Double cookies per click for 15 seconds!")
            self.active_events["Cookie Storm"] = time.time() + storm_duration
            self.event_multipliers["Cookie Storm"] = 2
            ui_manager.cookie_per_click *= self.event_multipliers["Cookie Storm"]

            # Set the event popup
            ui_manager.active_event_popup = "Cookie Storm! Double cookies for 15 seconds!"
            ui_manager.event_popup_end_time = time.time() + 3  # Show for 3 seconds

        elif event == "Gambling":
            print("Gambling Event! Risk it all!")
            self.show_gambling_popup = True  # Show gambling popup


    def is_event_active(self, event):
        """Check if a specific event is active."""
        return event in self.active_events and time.time() < self.active_events[event]

    def clear_event(self, event, ui_manager):
        if event in self.active_events and time.time() >= self.active_events[event]:
            print(f"Ending event '{event}' at time {time.time()}")

            if event in self.event_multipliers:
                ui_manager.cookie_per_click /= self.event_multipliers[event]
                del self.event_multipliers[event]

            del self.active_events[event]

            self.event_lock = False  # Release the lock when the event ends


    def clear_expired_events(self, ui_manager):
        for event in list(self.active_events.keys()):
            if not self.is_event_active(event):
                self.clear_event(event, ui_manager)

        # Reset the event lock after clearing all expired events
        if not self.active_events:  # No active events remain
            self.event_lock = False

    def resolve_gambling_event(self, ui_manager, risk):
        if risk:
            if random.random() <= 0.80:  # 80% chance to double cookies
                ui_manager.cookie_count *= 5
                print("Lucky! Your cookies quintupled!")
            else:
                ui_manager.cookie_count = 0
                print("Unlucky! You lost your cookies!")
        else:
            print("You chose not to gamble!")

        # Close the popup
        self.show_gambling_popup = False

        # Reset the event lock
        self.event_lock = False

class CookieAnalytics:
    def __init__(self):
        self.total_cookies = 0
        self.clicks = 0

    def update(self, cookies_gained, clicks):
        self.total_cookies += cookies_gained
        self.clicks += clicks

    def display_stats(self):
        print(f"Total Cookies: {self.total_cookies}")
        print(f"Total Clicks: {self.clicks}")

# Main game class
class Game:
    # initializes the UI and time keeping functions
    def __init__(self):
        self.achievement_manager = AchievementManager()
        self.prestige = Prestige()
        self.ui_manager = UIManager(self.achievement_manager, self.prestige)
        self.cookie = Cookie(f"{ASSETS_FILEPATH}/cookie.png", 0.2, self.ui_manager.WIDTH, self.ui_manager.HEIGHT)
        self.random_event_manager = RandomEventManager()  # Initialize RandomEventManager
        self.last_time = time.time()
        self.last_event_time = time.time()
        self.clock = pygame.time.Clock()
        self.cursor = Cursor(f"{ASSETS_FILEPATH}/cursor/cursor1.png", 1, 64, 64)
        self.background_image = pygame.image.load(f"{ASSETS_FILEPATH}/background/background.png") #background image
        self.background_image = pygame.transform.scale(self.background_image, (self.ui_manager.WIDTH, self.ui_manager.HEIGHT))#scale background image
        self.ig_background_image = pygame.image.load(f"{ASSETS_FILEPATH}/background/in_game_background.png") #in game background
        self.ig_background_image = pygame.transform.scale(self.ig_background_image, (self.ui_manager.WIDTH, self.ui_manager.HEIGHT))#scale in game background image
        self.sound_manager = SoundManager()
        

    # checks each event that occurs in pygame and updates the game accordingly.
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and self.ui_manager.selected_save != None:
                    save(self.ui_manager, self.ui_manager.selected_save)
                elif event.key == pygame.K_l and self.ui_manager.selected_save != None:
                    load(self.ui_manager, self.ui_manager.selected_save)
                elif event.key == pygame.K_ESCAPE:
                    self.ui_manager.show_main_menu = not self.ui_manager.show_main_menu
                    self.ui_manager.show_saves_menu = False
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.ui_manager.show_main_menu and not self.ui_manager.show_settings_popup and not self.ui_manager.show_saves_menu and not self.ui_manager.show_new_game_menu:
                    # Handle main menu button clicks
                    if self.ui_manager.button_clicked("Continue", mouse_pos):
                        self.ui_manager.handle_save_slot_click()
                    elif self.ui_manager.button_clicked("New Game", mouse_pos):
                        self.ui_manager.handle_new_game_click()
                    elif self.ui_manager.button_clicked("Settings", mouse_pos):
                        self.ui_manager.handle_setting_popup_click()
                    elif self.ui_manager.button_clicked("Exit", mouse_pos):
                        pygame.quit()
                        sys.exit()

                elif self.ui_manager.show_saves_menu and self.ui_manager.show_main_menu:
                    self.ui_manager.draw_save_slots_popup(self.ui_manager.screen)
                    if self.ui_manager.selected_save == 'save1.txt':
                        self.ui_manager = UIManager(self.achievement_manager, self.prestige) # recreates a new UIManager to populate with the save file's data
                        self.ui_manager.selected_save = 'save1.txt'
                        # Load the game state when Continue is clicked
                        load(self.ui_manager, self.ui_manager.selected_save) # if == None: a save file doesnt exist, create a new save
                        self.ui_manager.show_main_menu = False  # Hide the main menu after loading
                    elif self.ui_manager.selected_save == 'save2.txt':
                        self.ui_manager = UIManager(self.achievement_manager, self.prestige) # recreates a new UIManager to populate with the save file's data
                        self.ui_manager.selected_save = 'save2.txt'
                        # Load the game state when Continue is clicked
                        load(self.ui_manager, self.ui_manager.selected_save) # if == None: a save file doesnt exist, create a new save
                        self.ui_manager.show_main_menu = False  # Hide the main menu after loading
                    elif self.ui_manager.selected_save == 'save3.txt':
                        self.ui_manager = UIManager(self.achievement_manager, self.prestige) # recreates a new UIManager to populate with the save file's data
                        self.ui_manager.selected_save = 'save3.txt'
                        # Load the game state when Continue is clicked
                        load(self.ui_manager, self.ui_manager.selected_save) # if == None: a save file doesnt exist, create a new save
                        self.ui_manager.show_main_menu = False  # Hide the main menu after loading
                               
                elif self.ui_manager.show_new_game_menu and self.ui_manager.show_main_menu:
                    self.ui_manager.draw_new_game_popup(self.ui_manager.screen)
                    if self.ui_manager.selected_save == 'save1.txt':
                        self.ui_manager.start_new_game()  # Start a new game with initial values
                        self.ui_manager.show_main_menu = False
                        self.ui_manager.handle_new_game_click()
                    elif self.ui_manager.selected_save == 'save2.txt':
                        self.ui_manager.start_new_game()  # Start a new game with initial values
                        self.ui_manager.show_main_menu = False
                        self.ui_manager.handle_new_game_click()
                    elif self.ui_manager.selected_save == 'save3.txt':
                        self.ui_manager.start_new_game()  # Start a new game with initial values
                        self.ui_manager.show_main_menu = False
                        self.ui_manager.handle_new_game_click()
                
                elif self.ui_manager.show_settings_popup and self.ui_manager.show_main_menu:
                    self.ui_manager.draw_settings_popup(self.ui_manager.screen)
                    if self.ui_manager.settings_pick == 1: # Handle the save game action
                        try:
                            save(self.ui_manager, self.ui_manager.selected_save)
                        except:
                            pass
                    elif self.ui_manager.settings_pick == 2: # Toggle music on/off
                        self.sound_manager.music_playing = not self.sound_manager.music_playing
                        self.sound_manager.toggle_music = True
                    elif self.ui_manager.settings_pick == 3: # Toggle sound on/off
                        self.ui_manager.sound_manager.toggle_sound()
                    elif self.ui_manager.settings_pick == 4: # Close the pop-up when the button is clicked
                        self.ui_manager.show_settings_popup = False

                else:
                    # Handle game-related clicks
                    if self.cookie.rect.collidepoint(mouse_pos):
                        self.ui_manager.handle_cookie_click()
                        self.achievement_manager.check_achievements(self.ui_manager.cookie_count)
                        self.cookie.animate()
                        self.ui_manager.draw_text(f"+{self.ui_manager.simplify_number(self.ui_manager.cookie_per_click)}", self.ui_manager.font, BLACK, int(mouse_pos[0]-26), int(mouse_pos[1]-30))
                    
                    # Moved functionality into the popup menu 
                    # Check if save button is clicked - IMPORTANT make this a function 
                    #if self.ui_manager.save_button.is_clicked(mouse_pos):
                    #    self.ui_manager.handle_save_click()
                    #    save(self.ui_manager)  # Call save function
                    
                    if self.ui_manager.popup_button.is_clicked(mouse_pos):
                        self.ui_manager.handle_popup_click()
                    
                    if self.ui_manager.prestige_button.is_clicked(mouse_pos):
                        self.prestige.handle_prestige_click()

                    #if not self.ui_manager.draw_popup_menu and not self.prestige.draw_prestige_menu:
                    else:
                        self.ui_manager.handle_shop_click(mouse_pos)
                self.cursor.animate()

            # Handle window resizing
            if event.type == pygame.VIDEORESIZE:
                self.ui_manager.WIDTH, self.ui_manager.HEIGHT = event.w, event.h
                self.ui_manager.screen = pygame.display.set_mode((self.ui_manager.WIDTH, self.ui_manager.HEIGHT), pygame.RESIZABLE)
                self.cookie = Cookie(f"{ASSETS_FILEPATH}/cookie.png", 0.2, self.ui_manager.WIDTH, self.ui_manager.HEIGHT)
                self.ui_manager = UIManager(self.achievement_manager, self.prestige)

            # Handle mouse wheel scrolling
            if event.type == pygame.MOUSEWHEEL:
                self.ui_manager.scroll_offset -= event.y * self.ui_manager.scroll_speed
                self.ui_manager.scroll_offset = max(0, min(self.ui_manager.scroll_offset, self.ui_manager.max_scroll_offset))

    # Begins the game and runs in a continuous loop
    def run(self):
        self.sound_manager.play_music()
        while True:
            current_time = time.time()
            
            # Update cookies per second every second
            if current_time - self.last_time >= 1:
                self.ui_manager.cookie_count += self.ui_manager.cookies_per_second()
                self.last_time = current_time

            # Trigger a new random event every minute
            if current_time - self.last_event_time >= 60:
                print("Attempting to trigger an event...")  # Debugging
                self.random_event_manager.trigger_event(self.ui_manager)
                self.last_event_time = current_time

            # Clear expired events
            self.random_event_manager.clear_expired_events(self.ui_manager)

            # Render the game elements
            if self.ui_manager.show_main_menu:
                self.ui_manager.screen.blit(self.background_image, (0, 0))
                self.ui_manager.run_main_menu()
                self.ui_manager.draw_settings_popup(self.ui_manager.screen)
                self.ui_manager.draw_save_slots_popup(self.ui_manager.screen)
                self.ui_manager.draw_new_game_popup(self.ui_manager.screen)

            else:
                self.ui_manager.screen.blit(self.ig_background_image, (0, 0))
                pygame.draw.rect(self.ui_manager.screen, (212, 179, 127), ((self.ui_manager.WIDTH - int(self.ui_manager.WIDTH * 0.25)) // 2, int(self.ui_manager.HEIGHT * 0.1), int(self.ui_manager.WIDTH * 0.25), int(self.ui_manager.HEIGHT * 0.8)))
                self.cookie.draw(self.ui_manager.screen)
                self.ui_manager.draw_stats(self.ui_manager.screen)
                self.ui_manager.draw_upgrades(self.ui_manager.screen)
                self.ui_manager.draw_shop(self.ui_manager.screen)
                self.ui_manager.draw_partitions(self.ui_manager.screen)
                self.cookie.update_rotation()
                self.cookie.draw_shimmer(self.ui_manager.screen)
                self.cookie.update_shimmer()

                # Draw popups, menus, and notifications
                self.ui_manager.draw_popup_cookie_earned(self.ui_manager.screen)
                self.ui_manager.draw_notifications(self.ui_manager.screen)
                self.ui_manager.draw_event_popup(self.ui_manager.screen)  # Draw the event popup here
                if self.ui_manager.draw_popup_menu(self.ui_manager.screen):
                    pass
                elif self.prestige.draw_prestige_menu(self.ui_manager):
                    pass
                else:
                    self.ui_manager.draw_prestige_menu_button()

                # Draw the gambling popup if it's active
                if self.random_event_manager.show_gambling_popup:
                    self.ui_manager.draw_gambling_popup(self.ui_manager.screen, self.random_event_manager)


            # Handle events and update display
            self.handle_events()
            self.cursor.update()
            self.cursor.draw()
            self.cursor.update_sprite()
            pygame.display.flip()
            self.clock.tick(30)  # Limit the game to 30 ticks per second
            if self.sound_manager.toggle_music:
                self.sound_manager.play_music()
                self.sound_manager.toggle_music = False
