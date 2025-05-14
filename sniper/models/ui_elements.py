"""
UI elements for the Sniper Game.
"""
import pygame
from typing import Tuple, List, Dict, Any

from sniper.config.constants import const

class Button:
    """A button UI element with hover and click effects."""
    
    def __init__(self, x, y, width, height, text, color=(100, 100, 200), text_color=(255, 255, 255)):
        """Initialize the button."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.hover_color = self._get_lighter_color(color, 30)
        self.click_color = self._get_darker_color(color, 30)
        self.current_color = color
        self.text_color = text_color
        self.is_hovered = False
        self.is_clicked = False
        self.click_animation_time = 0
        
        # Blinking properties
        self.is_blinking = False
        self.blink_timer = 0
        self.blink_interval = 500  # ms
        self.blink_state = True  # True = visible, False = invisible
    
    def _get_lighter_color(self, color, amount):
        """Return a lighter version of the color."""
        return tuple(min(255, c + amount) for c in color)
    
    def _get_darker_color(self, color, amount):
        """Return a darker version of the color."""
        return tuple(max(0, c - amount) for c in color)
    
    def set_blinking(self, should_blink):
        """Set whether the button should blink."""
        self.is_blinking = should_blink
    
    def update_blink(self, delta_time):
        """Update the blink state based on delta time."""
        if self.is_blinking:
            self.blink_timer += delta_time
            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0
                self.blink_state = not self.blink_state
    
    def handle_event(self, event):
        """Handle mouse events for the button."""
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Update color based on hover state
        if self.is_hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.base_color
        
        # Handle click animation
        if self.is_clicked:
            self.click_animation_time += 1
            if self.click_animation_time >= 10:  # Animation duration
                self.is_clicked = False
                self.click_animation_time = 0
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_clicked = True
                self.click_animation_time = 0
                self.current_color = self.click_color
                return True  # Button was clicked
        
        return False
    
    def draw(self, surface, font):
        """Draw the button on the surface."""
        if self.is_blinking and not self.blink_state:
            # Skip drawing if blinking and in invisible state
            return
        
        # Apply click animation effect (shrink slightly when clicked)
        rect_to_draw = self.rect.copy()
        if self.is_clicked:
            animation_progress = self.click_animation_time / 10
            if animation_progress < 0.5:
                # Shrink during first half of animation
                shrink_amount = int(4 * (0.5 - animation_progress))
                rect_to_draw.inflate_ip(-shrink_amount, -shrink_amount)
            else:
                # Grow back during second half of animation
                grow_amount = int(4 * (animation_progress - 0.5))
                rect_to_draw.inflate_ip(grow_amount, grow_amount)
        
        # Draw button background
        pygame.draw.rect(surface, self.current_color, rect_to_draw)
        
        # Draw button border
        border_color = self._get_darker_color(self.current_color, 50)
        pygame.draw.rect(surface, border_color, rect_to_draw, 2)
        
        # Draw button text
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=rect_to_draw.center)
        surface.blit(text_surface, text_rect)