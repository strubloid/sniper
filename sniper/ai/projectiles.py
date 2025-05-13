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
            debug_print(f"AI SHOOTING in direction ({dx}, {dy}) from ({shooter.x}, {shooter.y})")
            projectiles.append(
                Projectile(
                    shooter.x, shooter.y, dx, dy, 
                    shooter.sniper_type.color, shooter
                )
            )
            shooter.shots_left -= 1
            return True
        
        debug_print("Failed to shoot - no valid direction calculated")
        return False