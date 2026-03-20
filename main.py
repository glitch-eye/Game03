import pygame
from game import Game


def main():

    # initialize audio first (reduces sound latency)
    pygame.mixer.pre_init(44100, -16, 2, 512)

    # initialize pygame
    pygame.init()

    # create game
    game = Game()

    # load assets
    game.load_assets()

    # start game loop
    game.play()


if __name__ == "__main__":
    main()