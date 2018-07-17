from pywinauto import Application
from pywinauto import keyboard
from pywinauto import findwindows
import pyautogui
import imp
import time

class RS3Controller:

    def __init__(self, running=False):
        self.app=Application()
        if running:
            app=Application().connect(path=r"C:\Program Files\ASD\RS3\RS3.exe")
        else:
            app=Application().start("C:\Program Files\ASD\RS3\RS3.exe")

        self.spec=app.ThunderRT6Form
        self.spec.draw_outline()
        self.pid=app.process
        #self.menu=RS3Menu(self.pid,self.spec)
        
    def take_spectrum(self):
        self.spec.set_focus()
        pyautogui.press('space')
        
    def white_reference(self):
        self.spec.set_focus()
        keyboard.send_keys('{F4}')
        
    def optimize(self):
        self.spec.set_focus()
        keyboard.send_keys('^O')
        
    def spectrum_save(self, path, base, start_num, numfiles=1, interval=0, comment=None, new_file_format=False):
        try:
            self.menu.open_save_dialog()
        except:
            print('failed to open save dialog. Check connection with spetrometer.')
        save=wait_for_window(self.pid, 'Spectrum Save', 3)
        if save==None: print('ERROR: Failed to open save dialog')
        
    
        spec=save.ThunderRT6Form
        spec.Edit6.set_edit_text(path)
        spec.ThunderRT6PictureBoxDC3.click_input()
        elements=findwindows.find_elements(process=self.pid)
        for el in elements:
            if el.name=='Message':
                print('wait for input')
        

class ViewSpecProController:
    def __init__(self, running=False):
        self.app=Application()
        if running:
            self.app=Application().connect(path=r"C:\Program Files\ASD\ViewSpecPro\ViewSpecPro.exe")
        else:
            self.app=Application().start("C:\Program Files\ASD\ViewSpecPro\ViewSpecPro.exe")
        self.spec=self.app['ViewSpec Pro    Version 6.2'] 
        self.pid=self.app.process
    
    def process(self, input_path, output_path, tsv_name):
        self.open_files(input_path)
        self.set_save_directory(output_path)
        self.splice_correction()
        self.ascii_export(output_path, tsv_name)
        self.spec.menu_select('File -> Close')
        # if path_el[0]=='C:'or path_el[0]=='c:':
        #     os.system('dir')
    
    def open_files(self, path):
        self.spec.menu_select('File -> Open')
        open=self.app['Select Input File(s)']
        open.set_focus()
        open['Address Band Root'].toolbar.button(0).click()
        #open['Address Band Root'].edit.set_edit_text(path)
        keyboard.SendKeys(path)
        open['Address Band Root'].edit.set_focus()
        keyboard.SendKeys('{ENTER}')
        
        #Make sure *.0** files are visible instead of just *.asd. Note that this won't work if you have over 100 files!!
        open.ComboBox2.select(1).click()
        open.ComboBox2.select(1).click()
        open.directUIHWND.ShellView.set_focus()
        keyboard.SendKeys('^a')
        keyboard.SendKeys('{ENTER}')
    
    def set_save_directory(self,path):
        time.sleep(2)
        self.spec.menu_select('Setup -> Output Directory')
        save=self.app['New Directory Path']
        path_el=path.split('\\')
        if path_el[0]=='C:'or path_el[0]=='c:':
            for el in path_el:
                if el=='C:': el='C:\\'
                save.ListBox.select(el)
                self.select_item(save.ListBox.rectangle())
        else:
            print('Invalid directory (must save to C drive)')
            # path_el=['C:\\','Users','RS3Admin','Temp']
            # for el in path_el:
            #     save.ListBox.select(el)
            #     self.select_item(save.ListBox.rectangle())
        save.OKButton.click()
        #If a dialog box comes up asking if you want to set the default input directory the same as the output, click no. Not sure if there is a different dialog box that could come up, so this doesn't seem very robust.
        try:
            self.app['Dialog'].Button2.click()
        except:
            pass
        
    
    def splice_correction(self):
        self.select_all()
        self.spec.menu_select('Process -> Splice Correction')
        self.app['Splice Correct Gap'].set_focus()
        self.app['Splice Correct Gap'].button1.click_input()
        self.app['ViewSpecPro'].set_focus()
        self.app['ViewSpecPro'].button1.click_input()
        
    def ascii_export(self, path, tsv_name):
        self.select_all()
        self.spec.menu_select('Process -> ASCII Export')
        export=self.app['ASCII Export']
        export.ReflectanceRadioButton.check()
        export.AbsoluteCheckBox.check()
        export.OutputToASingleFileCheckBox.check()
        export.set_focus()
        export.Button2.click_input()
        
        save=self.app['Select Ascii File']
        save.set_focus()
        save.ToolBar2.double_click()
        keyboard.SendKeys(path)
        keyboard.SendKeys('{ENTER}')
        save.edit.set_edit_text(tsv_name)
        save.set_focus()
        save.OKButton.click_input()
        self.app['Dialog'].OKButton.click()
        
        
    def select_all(self):
        for i in range(self.spec.ListBox.ItemCount()):
            self.spec.ListBox.select(i)
    
    def wait_for_window(self, title, timeout):
        t0=time.clock()
        elements=findwindows.find_elements(process=self.pid)
        spec=None
        while self.app==None and time.clock()-t0<timeout:
            for el in elements:
                if el.name==title:
                    spec=self.app[title]#=Application().connect(handle=el.handle)
        return spec
        
    def select_item(self,rectangle):
        #set start position at center top of listbox
        im=pyautogui.screenshot()
        x=rectangle.left+0.5*(rectangle.right-rectangle.left)
        x=int(x)
        y=rectangle.top
        color=(51,153,255)
        
        while y<rectangle.bottom:
            if pyautogui.pixelMatchesColor(x,y,color):
                pyautogui.click(x=x,y=y, clicks=2)
                return
            y=y+5

class RS3Menu:

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