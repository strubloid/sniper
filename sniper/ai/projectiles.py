"""
Projectile management module - Handles creation and management of projectiles.
"""
from typing import List

from sniper.config.constants import debug_print
from sniper.models.characters import Character
from sniper.models.projectiles import Projectile

class ProjectileManager:
    """Handles projectile creation and management."""
    
    @staticmethod
    def create_projectile(shooter: Character, target: Character, 
                        projectiles: List[Projectile]) -> bool:
        """Create a projectile from shooter toward target's direction."""
        # Calculate direction vector
        dx, dy = 0, 0
        
        if shooter.x == target.x:  # Same column
            dy = 1 if target.y > shooter.y else -1
        elif shooter.y == target.y:  # Same row
            dx = 1 if target.x > shooter.x else -1
        
        # Create projectile if we have a valid direction
        if dx != 0 or dy != 0:
            # Start projectile slightly ahead of the enemy in the firing direction
            # This prevents the enemy from getting hit by its own projectile
            spawn_x = shooter.x + (0.5 * dx)
            spawn_y = shooter.y + (0.5 * dy)
            
            debug_print(f"AI SHOOTING in direction ({dx}, {dy}) from ({spawn_x}, {spawn_y})")
            projectiles.append(
                Projectile(
                    spawn_x, spawn_y, dx, dy, 
                    shooter.sniper_type.color, shooter
                )
            )
            shooter.shots_left -= 1
            return True
        
        debug_print("Failed to shoot - no valid direction calculated")
        return False