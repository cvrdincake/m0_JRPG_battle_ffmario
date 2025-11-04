"""Main entry point for the JRPG Battle game."""

import sys
import pygame
from src.game import Game


def main() -> None:
    """Entry point for the game."""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
