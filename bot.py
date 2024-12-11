

from linecache import getline
from difflib  import SequenceMatcher
from pytesseract import *
from PIL import Image
from threading import Thread, Lock
from enum import Enum

import win32api, win32gui, win32ui, win32con
import time



class BotState(Enum):

    INITIALIZING = 0
    SEARCHING = 1
    RUNNING = 2


class Bot:
    
    INITIALIZING_SECONDE = 2
    index_hangout = 1

    GET_TASK = {}
    click_xy = [None, None]

    State = None
    GameState = None

    lock = None
    stopped = True


    def __init__(self):
        self.lock = Lock()
        self.State = BotState.INITIALIZING

        self.timestamp = time.time()
        self.index_hangout = 1

        self.GET_TASK = {
            "dialogue": self.skip_dialogue,
            "hangout": self.skip_hangout
        }


    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()


    def stop(self):
        self.stopped = True


    def run(self):
        while not self.stopped:
            if self.State == BotState.INITIALIZING:
                print("initializing...")
                
                if time.time() > self.timestamp + self.INITIALIZING_SECONDE: #timer
                    self.lock.acquire()
                    self.State = BotState.SEARCHING
                    self.lock.release()

            elif self.State == BotState.SEARCHING:
                print("searching...")

                task_found = self.GameState

                if task_found:
                    self.lock.acquire()
                    self.State = BotState.RUNNING
                    self.lock.release()

            elif self.State == BotState.RUNNING:
                print("running...")

                self.do_task(self.GameState)
                
                self.lock.acquire()
                self.State = BotState.SEARCHING
                self.lock.release()
            

    def update_info(self, GameState, click_xy):
        self.lock.acquire()
        self.GameState = GameState
        self.click_xy = click_xy
        self.lock.release()


    @staticmethod
    def click(x=None, y=None):
        if x is not None or y is not None:
            win32api.SetCursorPos((x, y))

        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


    def do_task(self, GameState):
        if GameState in self.GET_TASK:
            self.GET_TASK[GameState]()


    def skip_hangout(self):
        x, y = self.get_script_xy(self.click_xy)
        self.click(x, y)


    def skip_dialogue(self):
        x, y = self.click_xy
        self.click(x, y)


    @staticmethod
    def take_screenshot(location):
        # set this
        x, y = location[0], location[1]-20
        w, h = 700, 100 
        hwnd = None

        wDC = win32gui.GetWindowDC(hwnd)
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (w, h), dcObj, (x, y), win32con.SRCCOPY)

        # Save img
        dataBitMap.SaveBitmapFile(cDC, "hangout_dialogue.jpg")

        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
    

    def get_script(self):
        return getline('hangout_script.txt', self.index_hangout)
    

    def get_script_xy(self, list_location):
        def similar(a, b):
            return SequenceMatcher(None, a, b).ratio()

        pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        for location in list_location:
            self.take_screenshot(location)
            img = Image.open('hangout_dialogue.jpg')
            output = pytesseract.image_to_string(img)

            confidence = similar(self.get_script(), output)
            if confidence >= 0.8:
                self.index_hangout += 1

                return location[0], location[1]
            
        return None, None
    
    