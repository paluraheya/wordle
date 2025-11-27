import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        # --- Background Musics ---
        self.menu_music = "music/bs.mp3"
        self.game_music = "music/bs2.mp3"

        # --- Preloaded SFX ---
        self.sfx = {
            "win": pygame.mixer.Sound("music/win.mp3"),
            "lose": pygame.mixer.Sound("music/lose.mp3")
        }
        self.music_volume = 0.3
        self.sfx_volume = 0.3

        for s in self.sfx.values():
            s.set_volume(self.sfx_volume)

        self.sound_enabled = True

    def play_music(self, file, loop=True):
        if not self.sound_enabled:
            return
        pygame.mixer.music.load(file)
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1 if loop else 0)

    def play_menu_music(self):
        self.play_music(self.menu_music)

    def play_game_music(self):
        self.play_music(self.game_music)

    def stop_music(self):
        pygame.mixer.music.stop()

  
    def play(self, name):
        if self.sound_enabled and name in self.sfx:
            self.sfx[name].play()

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            pygame.mixer.music.set_volume(0)
            for s in self.sfx.values():
                s.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.music_volume)
            for s in self.sfx.values():
                s.set_volume(self.sfx_volume)
