import os, re
import pygame
from concurrent.futures import ThreadPoolExecutor

class AssetLoader:

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

        self.image_futures = {}
        self.anim_futures = {}
        self.sound_futures = {}

        self.images = {}
        self.animations = {}
        self.sounds = {}
        self.music = {}

    # --------------------
    # IMAGE
    # --------------------

    def load_image(self, name, path):
        future = self.executor.submit(pygame.image.load, path)
        self.image_futures[name] = future

    # --------------------
    # ANIMATION FOLDER
    # --------------------

    def load_animation(self, name, folder):

        files = sorted([
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.endswith(".png")
        ],
        key=lambda x: int(re.search(r'\d+', os.path.basename(x)).group()))

        future = self.executor.submit(self._load_frames, files)
        self.anim_futures[name] = future

    def _load_frames(self, files):
        return [pygame.image.load(f) for f in files]

    # --------------------
    # SOUND EFFECT
    # --------------------

    def load_sound(self, name, path):
        future = self.executor.submit(pygame.mixer.Sound, path)
        self.sound_futures[name] = future

    # --------------------
    # MUSIC (store path)
    # --------------------

    def load_music(self, name, path):
        self.music[name] = path

    # --------------------
    # FINALIZE (MAIN THREAD)
    # --------------------

    def finalize(self):

        # images
        for name, future in self.image_futures.items():
            img = future.result()
            self.images[name] = img.convert_alpha()

        # animations
        for name, future in self.anim_futures.items():
            frames = future.result()
            self.animations[name] = [f.convert_alpha() for f in frames]

        # sounds
        for name, future in self.sound_futures.items():
            self.sounds[name] = future.result()

        # cleanup
        self.image_futures.clear()
        self.anim_futures.clear()
        self.sound_futures.clear()

    # --------------------
    # GETTERS
    # --------------------

    def get_image(self, name):
        return self.images[name]

    def get_animation(self, name):
        return self.animations[name]

    def get_sound(self, name):
        return self.sounds[name]

    def get_music(self, name):
        return self.music[name]

    # --------------------
    # LOADING STATUS
    # --------------------

    def done(self):

        futures = (
            list(self.image_futures.values())
            + list(self.anim_futures.values())
            + list(self.sound_futures.values())
        )

        return all(f.done() for f in futures)