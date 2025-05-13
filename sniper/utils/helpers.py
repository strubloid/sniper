"""
Helper utilities for the Sniper Game.
"""
import os
import sys
import pygame
from typing import Optional, Tuple

from sniper.config.constants import const

def load_image(filename: str, transparent_color: Optional[Tuple[int, int, int]] = None) -> pygame.Surface:
    """
    Load an image from the assets directory.
    
    Args:
        filename: Name of the file to load
        transparent_color: Color to use as transparent background (if any)
        
    Returns:
        Pygame surface containing the loaded image
    """
    try:
        fullpath = os.path.join(const.ASSETS_DIR, filename)
        image = pygame.image.load(fullpath)
        
        if transparent_color:
            image = image.convert()
            image.set_colorkey(transparent_color)
        else:
            image = image.convert_alpha()
            
        return image
    except pygame.error as e:
        sys.stderr.write(f"Error loading image '{filename}': {e}\n")
        raise

def scale_to_fit(surface: pygame.Surface, target_width: int, target_height: int) -> pygame.Surface:
    """
    Scale a surface to fit within the target dimensions while preserving aspect ratio.
    
    Args:
        surface: Surface to scale
        target_width: Maximum width
        target_height: Maximum height
        
    Returns:
        Scaled surface
    """
    width, height = surface.get_size()
    
    # Calculate scale factor to fit within target dimensions
    scale_factor = min(target_width / width, target_height / height)
    
    # Calculate new dimensions
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    
    # Scale the surface
    return pygame.transform.scale(surface, (new_width, new_height))

def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """
    Calculate Manhattan distance between two points.
    
    Args:
        pos1: First position (x, y)
        pos2: Second position (x, y)
        
    Returns:
        Manhattan distance between pos1 and pos2
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])