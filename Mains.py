
# Generic Import
import pygame
import os

# Project Specific Import

# This is the baseline class for any state in the game.
class _State(object):

    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.game_data = {}
        self.music = None
        self.music_title = None
        self.previous_music = None

    def get_event(self, event):
        pass

    def startup(self, current_time, game_data):
        self.game_data = game_data
        self.start_time = current_time

    def cleanup(self):
        self.done = False
        return self.game_data

    def update(self, surface, keys, current_time):
        pass


