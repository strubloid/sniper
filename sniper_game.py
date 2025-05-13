"""
Sniper Game - Main Entry Point

This is a bootstrap entry point that starts the game using the new modular structure.
"""
import os
import sys

# Add the project root to the path so we can import sniper module
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the main module and run the game
from sniper.main import main

if __name__ == "__main__":
    main()
