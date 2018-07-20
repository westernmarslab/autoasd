from pywinauto import Application
from pywinauto import keyboard
from pywinauto import findwindows
import pyautogui
from pywinauto import mouse
import imp
import time
import datetime
import os

class RS3Controller:

    def __init__(self, share_loc, logdir, running=False):
        self.share_loc=share_loc
        self.app=Application()
        self.save_dir=''
        self.basename=''
        self.nextnum=None
        self.hopefully_saved_files=[]
        self.failed_to_open=False
        try:
            self.app=Application().connect(path=r"C:\Program Files\ASD\RS3\RS3.exe")
        except:
            self.app=Application().start("C:\Program Files\ASD\RS3\RS3.exe")
        print(str(datetime.datetime.now())+'\tConnected to RS3')
        self.spec=None
        self.spec_connected=False
        while not self.spec_connected:
            print('Waiting for RS³ to connect to spectrometer.')
            elements=findwindows.find_elements(process=self.app.process)
            for el in elements:
                if el.name=='RS³   18483 1': 
                    self.spec=self.app['RS³   18483 1']
                    self.spec_connected=True
            time.sleep(1)
        print('RS³ connected to spectrometer.')
        self.logdir=logdir
        #logpath=self.share_loc+'\log'+datetime.datetime.now().strftime(%Y-%m-%d-%H-%M)
        #self.log=open(share_loc+'\log'+datetime.datetime.now().strftime(%Y-%m-%d-%H-%M),'w')
        self.spec=self.app.ThunderRT6Form
        self.spec.draw_outline()
        self.pid=self.app.process
        self.menu=RS3Menu(self.spec)
        
    def take_spectrum(self):
        self.spec.set_focus()
        pyautogui.press('space')
        time.sleep(1)
        if self.basename != '' and self.save_dir != '' and self.nextnum !=None:
            hopeful=self.save_dir+'\\'+self.basename+'.'+self.nextnum
            self.nextnum=str(int(self.nextnum)+1)
            while len(self.nextnum)<3:
                self.nextnum='0'+self.nextnum
            self.hopefully_saved_files.append(hopeful)
        else: self.hopefully_saved_files.append('unknown')
        
        
    def white_reference(self):
        self.spec.set_focus()
        keyboard.SendKeys('{F4}')
        
    def optimize(self):
        self.spec.set_focus()
        keyboard.SendKeys('^O')
        
    def spectrum_save(self, dir, base, startnum, numfiles=1, interval=0, comment=None, new_file_format=False):
        self.save_dir=dir
        self.basename=base
        self.nextnum=str(startnum)

        while len(self.nextnum)<3:
            self.nextnum='0'+self.nextnum
        save=self.app['Spectrum Save']
        if save.exists()==False:
            self.menu.open_save_dialog()
        save=self.app['Spectrum Save']
        if save.exists()==False: 
            print('ERROR: Failed to open save dialog')
            self.failed_to_open=True
            return
        save.Edit6.set_edit_text(dir)
        save.Edit7.set_edit_text('')
        save.Edit5.set_edit_text(base)
        save.Edit4.set_edit_text(startnum)
        if save.is_enabled():
            save.set_focus()
            print('ok maybe these are not good keys')
            keyboard.SendKeys('{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{ENTER}')
        else:
            raise Exception('Save dialog not enabled')
        #save.ThunderRT6PictureBoxDC3.click_input()
        
        message=self.app['Message']
        if message.exists():
            self.app['Message'].set_focus()
            keyboard.SendKeys('{ENTER}')
            
        # message=self.app['Message']
        # if message.exists():
        #     pyautogui.alert('addess message in RS3 to continue')
        

class ViewSpecProController:
    def __init__(self, logdir, running=False):
        self.app=Application()
        self.logdir=logdir
        try:
            self.app=Application().connect(path=r"C:\Program Files\ASD\ViewSpecPro\ViewSpecPro.exe")
        except:
            self.app=Application().start("C:\Program Files\ASD\ViewSpecPro\ViewSpecPro.exe")
        self.spec=self.app['ViewSpec Pro    Version 6.2'] 
        self.pid=self.app.process
    
    def process(self, input_path, output_path, tsv_name):
        files=os.listdir(output_path)
        for file in files:
            if '.sco' in file:
                os.remove(output_path+'\\'+file)
        self.spec.menu_select('File -> Close')
        self.open_files(input_path)
        time.sleep(2)
        self.set_save_directory(output_path)
        self.splice_correction()
        self.ascii_export(output_path, tsv_name)
        self.spec.menu_select('File -> Close')
        files=os.listdir(output_path)
        for file in files:
            if '.sco' in file:
                os.remove(output_path+'\\'+file)
    
    def open_files(self, path):
        self.spec.menu_select('File -> Open')
        open=wait_for_window(self.app,'Select Input File(s)')
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

    def __init__(self, spec):
        self.spec=spec
        self.display_delta_x=125
        self.control_delta_x=180
        self.GPS_delta_x=235
        self.help_delta_x=270
        self.x_left=self.spec.rectangle().left
        y_form_top=self.spec.rectangle().top
        y_box_top=y_form_top+39
        # try:
        #     y_box_top=self.spec.ThunderRTCFormPictureBox10.rectangle().top
        # except:
        #     try:
        #         y_box_top=self.spec.ThunderRTCFormPictureBox11.rectangle().top
        #     except:
        #         y_box_top=self.spec.ThunderRTCFormPictureBox12.rectangle().top

        self.y_menu=int(y_box_top+(y_form_top-y_box_top)/4)

        
    def open_save_dialog(self):
        if self.spec.exists()==False:
            print('RS3 not found. Failed to open save menu')
            return
        self.spec.set_focus()
        #print('I think the left side of the window is: '+str(self.x_left))
        mouse.click(coords=(self.x_left+self.control_delta_x, self.y_menu))
        for i in range(10):
            keyboard.SendKeys('{DOWN}')
        keyboard.SendKeys('{ENTER}')
        
def wait_for_window(app, title, timeout=5):
    spec=app[title]
    i=0
    while spec.exists()==False and i<timeout:
        try:
            spec=self.app[title]
        except:
            i=i+1
            time.sleep(1)
    return spec