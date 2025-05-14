"""
Pathfinding module - Contains algorithms for AI movement path calculation.
"""
from typing import List, Tuple, Set, Dict, Optional

from sniper.config.constants import const
from sniper.config.constants import debug_print
from sniper.models.characters import Character

class PathFinder:
    """Handles pathfinding for the AI."""
    
    @staticmethod
    def find_path(start: Tuple[int, int], end: Tuple[int, int], 
                 obstacles: List[Tuple[int, int]], player: Character) -> List[Tuple[int, int]]:
        """
        Find a path from start to end, avoiding obstacles and player.
        Uses A* algorithm for optimal pathfinding.
        """
        debug_print(f"Pathfinding from {start} to {end}")
        debug_print(f"Obstacles count: {len(obstacles)}")
        
        # Major bug fix: Only avoid the player position if they're not the target
        # This was preventing the AI from finding paths to attack the player
        player_pos = (int(player.x), int(player.y))
        if end == player_pos:
            obstacles_set = set(obstacles)  # Don't avoid player if it's the target
            debug_print("Target is player, not avoiding player position")
        else:
            obstacles_set = set(obstacles + [player_pos])
            debug_print("Adding player position to obstacles")
        
        # A* algorithm implementation
        open_set = {start}
        closed_set = set()
        
        # Track path and costs
        came_from = {}
        g_score = {start: 0}  # Cost from start to current node
        f_score = {start: PathFinder._manhattan_distance(start, end)}  # Estimated total cost
        
        iterations = 0
        max_iterations = const.GRID_WIDTH * const.GRID_HEIGHT  # Prevent infinite loops
        
        while open_set and iterations < max_iterations:
            iterations += 1
            
            # Find node with lowest f_score
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            
            # Goal check
            if current == end:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                debug_print(f"Path found with {len(path)} steps")
                return path[::-1]  # Reverse to get start-to-end
            
            # Process current node
            open_set.remove(current)
            closed_set.add(current)
            
            # Check neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Skip invalid positions
                if (neighbor[0] < 0 or neighbor[0] >= const.GRID_WIDTH or
                    neighbor[1] < 0 or neighbor[1] >= const.GRID_HEIGHT or
                    neighbor in obstacles_set or neighbor in closed_set):
                    continue
                
                # Calculate scores
                tentative_g = g_score[current] + 1
                
                # Add to open set if not there, or if we found a better path
                if neighbor not in open_set or tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + PathFinder._manhattan_distance(neighbor, end)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        
        # No path found
        if iterations >= max_iterations:
            debug_print("Pathfinding aborted after too many iterations")
        else:
            debug_print("No path found - no valid route to destination")
        return []
    
    @staticmethod
    def _manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two points."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])