from pywinauto import Application
from pywinauto import keyboard
import pyautogui
import imp

import controls
imp.reload(controls)
from controls import Menu

class SpectrometerController:

    def __init__(self, running=False):
        self.app=Application()
        if running:
            app=Application().connect(path=r"C:\Program Files\ASD\RS3\RS3.exe")
        else:
            app=Application().start(path=r"C:\Program Files\ASD\RS3\RS3.exe")

        self.spec=app.ThunderRT6Form
        self.spec.draw_outline()
        pid=app.process
        #self.menu=Menu(pid,self.spec)
        
    def take_spectrum(self):
        self.spec.set_focus()
        pyautogui.press('space')
        
    def white_reference(self):
        self.spec.set_focus()
        keyboard.send_keys('{F4}')
        
    def optimize(self):
        self.spec.set_focus()
        keyboard.send_keys('^O')