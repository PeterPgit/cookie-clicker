'''
Module Name: prestige.py
Purpose: This module handles all gameplay aspects related to the prestige mechanism
Inputs: None
Output: None
Additional code sources: 
Developers: Peter Pham
Date: 12/1/2024
Last Modified: 12/8/2024
'''

import pygame
from buttons import LargeButton
from shop import ShopUpgrade

class Prestige:
    def __init__(self):
        self.prestige_count = 0
        self.golden_cookies = 0
        self.show_prestige_menu = False
        self.show_prestige_verify = False
        self.prestige_shop = Prestige_Shop()

    def prestige_check_menu(self, ui_manager):
        popup_width = int(ui_manager.WIDTH * 0.7)
        popup_height = int(ui_manager.HEIGHT * 1)
        popup_x = (ui_manager.WIDTH - popup_width) 
        popup_y = (ui_manager.HEIGHT - popup_height) // 2  # Center the popup vertically
        
        # Draw the popup background
        pygame.draw.rect(ui_manager.screen, (200, 200, 200), (popup_x, popup_y, popup_width, popup_height))

        title_font = pygame.font.SysFont(None, int(popup_height * 0.1))
        title_text = "Are you sure?"
        ui_manager.draw_text(title_text, title_font, (0, 0, 0), popup_x + popup_width // 2 - title_font.size(title_text)[0] // 2, popup_y + 10)

        button_labels = ["Confirm", "Cancel"]

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
            button = LargeButton(ui_manager.screen, button_x, button_y, label, button_width, button_height)
            button.draw(ui_manager.screen)

            # Handle the button click based on its label
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button pressed (0 = left, 1 = middle, 2 = right)

            # Ensure the click is only handled once (we prevent double-clicking the button)
            if button.is_clicked(mouse_pos) and mouse_pressed:
                if not hasattr(self, '_button_clicked') or not self._button_clicked:
                    self._button_clicked = True  # Lock the button to avoid multiple triggers
                    ui_manager.sound_manager.play_sound("menu-click")
                    if label == "Confirm":
                        if ui_manager.cookie_count > 10000000:
                            self.prestige(ui_manager)
                        self.show_prestige_verify = False
                    elif label == 'Cancel':
                        self.show_prestige_verify = False
                else:
                    # If the button was already clicked, do nothing (debounced)
                    pass

            # Reset the click lock when the mouse button is released
            if not mouse_pressed:
                if hasattr(self, '_button_clicked') and self._button_clicked:
                    self._button_clicked = False  # Unlock the button when the button is released

    def prestige(self, ui_manager):
        self.golden_cookies += ui_manager.cookie_count / 10000000
        ui_manager.cookie_count = 0
        ui_manager.upgrades_acquired = []

    def handle_prestige_click(self):
        self.show_prestige_menu = not self.show_prestige_menu  # Toggles the prestige menu

    def draw_prestige_menu(self, ui_manager):
            if self.show_prestige_verify:
                self.prestige_check_menu(ui_manager)
            elif self.show_prestige_menu:
                popup_width = int(ui_manager.WIDTH * 0.7)
                popup_height = int(ui_manager.HEIGHT * 1)
                popup_x = (ui_manager.WIDTH - popup_width) 
                popup_y = (ui_manager.HEIGHT - popup_height) // 2  # Center the popup vertically
                
                # Draw the popup background
                pygame.draw.rect(ui_manager.screen, (200, 200, 200), (popup_x, popup_y, popup_width, popup_height))

                # Draw the title of the popup
                title_font = pygame.font.SysFont(None, int(popup_height * 0.1))
                title_text = "Prestige Menu"
                ui_manager.draw_text(title_text, title_font, (0, 0, 0), popup_x + popup_width // 2 - title_font.size(title_text)[0] // 2, popup_y + 10)

                # Define the buttons and their labels
                button_labels = ["Prestige", "Close Menu"]
                
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
                    button = LargeButton(ui_manager.screen, button_x, button_y, label, button_width, button_height)
                    button.draw(ui_manager.screen)

                    # Handle the button click based on its label
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button pressed (0 = left, 1 = middle, 2 = right)

                    # Ensure the click is only handled once (we prevent double-clicking the button)
                    if button.is_clicked(mouse_pos) and mouse_pressed:
                        if not hasattr(self, '_button_clicked') or not self._button_clicked:
                            self._button_clicked = True  # Lock the button to avoid multiple triggers
                            ui_manager.sound_manager.play_sound("menu-click")
                            if label == "Close Menu":
                                self.show_prestige_menu = False  # Close the pop-up when the button is clicked
                            elif label == 'Prestige':
                                self.show_prestige_verify = True
                        else:
                            # If the button was already clicked, do nothing (debounced)
                            pass

                    # Reset the click lock when the mouse button is released
                    if not mouse_pressed:
                        if hasattr(self, '_button_clicked') and self._button_clicked:
                            self._button_clicked = False  # Unlock the button when the button is released


                font_size = int(ui_manager.WIDTH * 0.02)  # Dynamic font size based on width
                font = pygame.font.SysFont(None, font_size)
                ui_manager.draw_text(f"Golden Cookies: {self.golden_cookies:.2f}", font, (0,0,0), popup_x + 10, popup_y+100)

                self.golden_cookies = self.prestige_shop.draw_shop_items(ui_manager, self.golden_cookies)
                return True
            else:
                return False
            
    def get_shop_items(self):
        return self.prestige_shop.get_shop_items()

class Prestige_Shop:
    def __init__(self):
        self.prestige_upgrades = {
            'Golden Hands: 1': ShopUpgrade("Golden Hands", 1, 5000, None),
            'Golden Grandma: 3': ShopUpgrade("Golden Grandma", 3, 10000, None),
            'Golden Factory: 10': ShopUpgrade("Golden Factory", 10, 1000000, None)
        }
    
    def draw_shop_items(self, ui_manager, golden_cookies):
        popup_width = int(ui_manager.WIDTH * 0.7)
        popup_height = int(ui_manager.HEIGHT * 1)
        popup_x = (ui_manager.WIDTH - popup_width) 
        popup_y = (ui_manager.HEIGHT - popup_height) // 2  # Center the popup vertically

        # Set button properties
        button_width = int(popup_width * 0.3)  # Adjust the button width based on the popup size
        button_height = int(popup_height * 0.1)  # Set a reasonable button height

        # Calculate the vertical position of the buttons (one row of buttons at the bottom)
        button_y = popup_y + popup_height - button_height - 300
        
        # Space out the buttons horizontally based on the number of buttons
        spacing = (popup_width - len(self.prestige_upgrades) * button_width) // (len(self.prestige_upgrades) + 1)  # Space between buttons

        title_font = pygame.font.SysFont(None, int(popup_height * 0.1))
        title_text = "Prestige Shop:"
        ui_manager.draw_text(title_text, title_font, (0, 0, 0), popup_x + popup_width // 2 - title_font.size(title_text)[0] // 2, popup_y + 500)


        # Loop through the button labels and create the buttons
        for index, (key, item) in enumerate(self.prestige_upgrades.items()):
            # Calculate the x-position of the current button
            button_x = popup_x + (index + 1) * spacing + index * button_width
            button = LargeButton(ui_manager.screen, button_x, button_y, key, button_width, button_height)
            button.draw(ui_manager.screen)

            # Handle the button click based on its label
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button pressed (0 = left, 1 = middle, 2 = right)

            # Ensure the click is only handled once (we prevent double-clicking the button)
            if button.is_clicked(mouse_pos) and mouse_pressed:
                if not hasattr(self, '_button_clicked') or not self._button_clicked:
                    self._button_clicked = True  # Lock the button to avoid multiple triggers
                    price = int(item.base_cost)
                    print(golden_cookies, price)
                    if golden_cookies > price:
                        ui_manager.sound_manager.play_sound("shop")
                        item.purchased_count += 1
                        golden_cookies -= price
                else:
                    # If the button was already clicked, do nothing (debounced)
                    pass

            # Reset the click lock when the mouse button is released
            if not mouse_pressed:
                if hasattr(self, '_button_clicked') and self._button_clicked:
                    self._button_clicked = False  # Unlock the button when the button is released
        return golden_cookies
    
    def get_shop_items(self):
        return self.prestige_upgrades.items()