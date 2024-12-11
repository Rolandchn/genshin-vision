

from os import stat 
from threading import Thread, Lock

import pyautogui
import cv2 as cv

from texture import Texture, Icons



class Detection:

    GameState = None
    TEXTURE = None
    lock = None
    stopped = True
    click_xy = [None, None]

    def __init__(self):
        self.lock = Lock()
        self.TEXTURE = Texture()


    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()


    def stop(self):
        self.stopped = True


    def run(self):
        while not self.stopped:
            with self.lock:
                GameState = self.get_state()
                self.GameState = GameState

                if GameState is not None:
                    self.click_xy = self.get_dialogue_button()


    def get_state(self):
        if self.is_mainscreen():
            return None
        
        elif self.is_dialogue_playing():
            if self.is_hangout_playing():
                return "hangout"
            
            return "dialogue"


    def is_mainscreen(self):
        return pyautogui.locateOnScreen(self.TEXTURE.button_texture[Icons.PAIMON_BUTTON.value], region=(27, 12, 70, 80), confidence=0.9)


    def is_hangout_playing(self):
        if stat('genshin_tool\hangout_script.txt').st_size == 0:
            return False

        if pyautogui.locateOnScreen(self.TEXTURE.button_texture[Icons.HANGOUT_BUTTON.value], region=(500, 300, 800, 500), confidence=0.8) is not None:

            bubbles_button_on = pyautogui.locateAllOnScreen(self.TEXTURE.button_texture[Icons.HANGOUT_BUTTON.value], region=(500, 300, 800, 500), grayscale=True, confidence=0.8)
            bubbles_button_on = [[x, y, w, h] for (x, y, w, h) in bubbles_button_on]

            bubbles_coordinates, weight = cv.groupRectangles(bubbles_button_on, 1, 0.3)

            self.click_xy = bubbles_coordinates

            return True
        
        return False


    def is_dialogue_playing(self):
        dialogue_button_on = pyautogui.locateOnScreen(self.TEXTURE.button_texture[Icons.PLAY_BUTTON.value], region=(51, 28, 40, 40), confidence=0.8, grayscale=True)

        if dialogue_button_on:
            return True

        for sub_icon in self.TEXTURE.subbutton_texture[Icons.PLAY_BUTTON.value]:
            dialogue_button_on = pyautogui.locateOnScreen(sub_icon, region=(51, 28, 40, 40), confidence=0.98, grayscale=True)
            if dialogue_button_on:
                return True
        
        return False
    
    
    def get_dialogue_button(self):
        bubble_button_on = pyautogui.locateOnScreen(self.TEXTURE.button_texture[Icons.BUBBLE_BUTTON.value], region=(1279, 325, 40, 500), confidence=0.8, grayscale=True)

        if bubble_button_on:
            x, y = bubble_button_on[:2]

        else:
            x, y = [None, None]

        return (x, y)
