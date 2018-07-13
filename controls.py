from pywinauto import Application
from pywinauto import findwindows
from pywinauto import mouse
from pywinauto import keyboard

#print('foo')

class Menu:

    def __init__(self, pid, spec):
        #spec.print_control_identifiers()
        #spec.ThunderRT6PictureBox38.draw_outline()
        print('foo')
        self.pid=pid
        self.display_delta_x=125
        self.control_delta_x=180
        self.GPS_delta_x=235
        self.help_delta_x=270
        self.x_left=spec.rectangle().left
        y_form_top=spec.rectangle().top
        y_box_top=spec.ThunderRTCFormPictureBox12.rectangle().top
        self.y_menu=int(y_box_top+(y_form_top-y_box_top)/4)

        
    def open_save_dialog(self):
        self.spec.set_focus()
        mouse.click(coords=(self.x_left+self.control_delta_x, self.y_menu))
        for i in range(10):
            keyboard.SendKeys('{DOWN}')
        keyboard.SendKeys('{ENTER}')
        