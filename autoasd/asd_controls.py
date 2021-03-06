from pywinauto import Application
from pywinauto import keyboard
from pywinauto import findwindows
import warnings
import pyautogui
from pywinauto import mouse
import imp
import time
import datetime
import os

computer='desktop'

if computer=='new' or computer =='desktop':
    IMG_LOC='img2'
elif computer=='old':
    IMG_LOC='img'

global COLORS
COLORS={'status':None, 'file_highlight':''}
global INDEXNUMLEN
if computer=='old':
    COLORS['file_highlight']=(51,153,255)
    COLORS['status']=(0,0,168)
    INDEXNUMLEN=3
elif computer=='new' or computer=='desktop':
    COLORS['file_highlight']=(0,120,215)
    INDEXNUMLEN=5

warnings.simplefilter('ignore', category=UserWarning)

class RS3Controller:

    def __init__(self, share_loc,RS3_loc):
        self.RS3_loc=RS3_loc
        self.share_loc=share_loc
        self.app=Application()
        self.save_dir=''
        self.basename=''
        self.nextnum=None
        self.hopefully_saved_files=[]
        self.failed_to_open=False
        self.numspectra=None
        self.wr_success=False
        self.wr_failure=False
        self.opt_complete=False
        self.interval=0.25
        
        try:
            #print(errortime)
            self.app=Application().connect(path=RS3_loc)
        except:
            print('\tStarting RS³')
            self.app=Application().start(RS3_loc)
        print('\tConnected to RS3')
        self.spec=None
        self.spec_connected=False
        self.spec=self.app.ThunderRT6Form
        self.spec.draw_outline()
        self.pid=self.app.process
        self.menu=RS3Menu(self.app)
    
    def check_connectivity(self):
        try:
            top_window=top=self.app.top_window()
        except Exception as e:
            print(e)
            return False
        try:
            top_element=findwindows.find_element(handle=top_window.handle)
            if top_element.name=='TCP Servers Not Found.\r\nCheck Connection':
                return False
            elif top_element.name=='Check Connection':
                return False
            elif top_element.name=='Searching for TCP Servers...':
                return False
            elif top_element.name=='TCP Servers Not Found.':
                return False
            elif top_element.name=='Check Connection':
                return False
            elif top_element.name=='Connecting...':
                print('Connecting...')
                return False
                
            elif 'Initializing' in top_element.name:
                print('Initializing...')
                return False

            elif 'Unable to connect' in top_element.name:
                return False
            elif top_element.name=='RS³':
                return False
            elif 'was lost' in top_element.name:
                return False
            elif top_element.name=='':
                return True
            elif top_element.name=='About':
                print('About, returning false')
                return False
            elif top_element.name=='Unable to collect at current gain and offset values.  Please optimize instrument.':
                print('Optimize instrument before collecting data.')
                return True
            elif top_element.name=='Type mismatch':
                return False
                
            elif 'Connected to' in top_element.name:
                return True
            elif top_element.name=='RS³   18483 1':
                return True
                
            else:
                if 'Initial' in top_element.name:
                    print('Why is this initializing unexpected?')
                print('unexpected name:')
                print(top_element.name)
                return True
                
        except Exception as e:
            print(e)
            return True

        
    def take_spectrum(self, filename):
        self.spec.set_focus()
        time.sleep(1)
        pyautogui.press('space')
        
        self.hopefully_saved_files.append(filename) #Know to expect this file in the data directory
        
        self.nextnum=str(int(self.nextnum)+1)
        while len(self.nextnum)<INDEXNUMLEN:
             self.nextnum='0'+self.nextnum
                
        
    def white_reference(self):
        self.spec.set_focus()
        keyboard.SendKeys('{F4}')
        start_timeout=10
        t=0
        started=False
        while not started and t<start_timeout:
            loc=find_image(IMG_LOC+'/status_color.png', rect=self.spec.ThunderRT6PictureBoxDC6.rectangle())
            if loc != None:
                started=True
            else:
                time.sleep(self.interval)
                t+=self.interval
        if t>=start_timeout:
            print('wr failed')
            self.wr_failure=True
            return
        print('wr started')
        finish_timeout=10+int(self.numspectra)/9
        t=0
        finished=False
        while not finished and t<finish_timeout:
            loc=find_image(IMG_LOC+'/white_status.png', rect=self.spec.ThunderRT6PictureBoxDC6.rectangle())
            if loc != None:
                finished=True
            else:
                time.sleep(self.interval)
                t+=self.interval
        if t>= finish_timeout:
            self.wr_failure=True
            print('wr failed')
            return
        time.sleep(2)#This is important! Otherwise the spectrum won't be saved because the spacebar will get pushed before RS3 is ready for it.
        print('wr succeeded')
        self.wr_success=True

        
    #When you press optimize, first look for the word 'optimizing', then wait for the status bar to be white 
    #for a few seconds. After that happens, wait for blue to turn up again in the status bar, and at that
    #point you are ready to take a spectrum.
    def optimize(self):
        self.opt_complete=False
        self.spec.set_focus()
        keyboard.SendKeys('^O')
        
        started=False
        t=0
        timeout=30
        while not started and t<timeout:
            loc=find_image(IMG_LOC+'/optimizing.png', rect=self.spec.ThunderRT6Frame3.rectangle())
            if loc != None:
                started=True
                print('Initialized optimization')
            else:
                t+=.1 #Note there is no sleeping. If we sleep, we might miss the words appearing on the screen, which aren't always there for long.
                if t%5==0: print(t)
        if not started:
            print('opt timed out')
            raise Exception('Optimization timed out')

        time.sleep(int(self.numspectra)/100) #make sure we don't find the white status bar while it is still getting set up instead of after it completes.
        finished=False
        t=0
        timeout=10+int(self.numspectra)/9
        while not finished and t<timeout:
            loc=find_image(IMG_LOC+'/white_status.png', rect=self.spec.ThunderRT6PictureBoxDC5.rectangle())
            if loc != None:
                print('Found white status')
                while not finished and t<timeout:

                    loc=find_image(IMG_LOC+'/white_status.png', rect=self.spec.ThunderRT6PictureBoxDC5.rectangle())
                    if loc!=None:
                        finished=True
                    else:
                        time.sleep(self.interval)
                        t=t+self.interval
            else:
                time.sleep(self.interval)
                t=t+self.interval
        if not finished:
            print('opt timed out 1')
            raise Exception('Optimization timed out')
        print('Completed optimization')
            
        ready=False
        t=0
        timeout=10+int(self.numspectra)/9
        while not ready and t<timeout:
            loc=find_image(IMG_LOC+'/status_color.png', rect=self.spec.ThunderRT6PictureBoxDC5.rectangle())
            if loc != None:
                ready=True
            else:
                time.sleep(self.interval)
                t=t+self.interval
        if not ready:
            print('opt timed out 2')
            raise Exception('Optimization timed out')
        sleep=int(self.numspectra)/500+1
        time.sleep(sleep)
        print('Instrument ready')
        self.opt_complete=True

    
    def instrument_config(self, numspectra):
        pauseafter=False
        if self.numspectra==None or int(self.numspectra)<20 or True:
            pauseafter=True
        self.numspectra=numspectra
        

        config=self.app['Instrument Configuration']
        if config.exists()==False:
            self.menu.open_control_dialog([IMG_LOC+'/rs3adjustconfig.png',IMG_LOC+'/rs3adjustconfig2.png'])
        
        
        t=0
        while config.exists()==False and t<10:
            print('waiting for instrument config panel')
            time.sleep(self.interval)
            t+=self.interval
            
        if config.exists()==False:
            print('ERROR: Failed to open instrument configuration dialog')
            self.failed_to_open=True
            return
            
        config.Edit3.set_edit_text(str(numspectra)) #probably done twice to set numspectra for wr and taking spectra.
        config.Edit.set_edit_text(str(numspectra))
        config.set_focus()
        config.ThunderRT6PictureBoxDC.click_input()
        if pauseafter: 
            time.sleep(2)
        print('Instrument configuration set with '+str(numspectra)+' spectra being averaged')

        
    def spectrum_save(self, dir, base, startnum, numfiles=1, interval=0, comment=None, new_file_format=False):
        self.save_dir=dir
        self.basename=base
        self.nextnum=str(startnum)

        while len(self.nextnum)<INDEXNUMLEN:
            self.nextnum='0'+self.nextnum
        save=self.app['Spectrum Save']
        if save.exists()==False:
            self.menu.open_control_dialog([IMG_LOC+'/rs3specsave.png',IMG_LOC+'/rs3specsave2.png'])
        for _ in range(int(2.5/self.interval)):
            save=self.app['Spectrum Save']
            if save.exists():
                break
            else:
                print('no spectrum save yet')
                time.sleep(self.interval)
                
        if save.exists()==False: 
            print('ERROR: Failed to open save dialog')
            raise Exception
            return
        save.Edit6.set_edit_text(dir)
        save.Edit7.set_edit_text('')
        save.Edit5.set_edit_text(base)
        save.Edit4.set_edit_text(startnum)

        save.set_focus()
        okfound=False
        controls=[save.ThunderRT6PictureBoxDC3,save.ThunderRT6PictureBoxDC2, save.ThunderRT6PictureBox]
        while True:
            for control in controls:
                control.draw_outline()
                rect=control.rectangle()
                loc=find_image(IMG_LOC+'/rs3ok.png', rect=rect)
                if loc != None:
                    control.click_input()
                    okfound=True
                    break
            if okfound:
                break
            print('searching for OK button')
            time.sleep(0.5)
        
        message=self.app['Message']
        if message.exists():
            self.app['Message'].set_focus()
            keyboard.SendKeys('{ENTER}')
            
        # message=self.app['Message']
        # if message.exists():
        #     pyautogui.alert('addess message in RS3 to continue')
        

class ViewSpecProController:

    def __init__(self, share_loc, ViewSpecPro_loc):
        self.app=Application()
        #self.logdir=logdir
        self.ViewSpecPro_loc=ViewSpecPro_loc
        self.share_loc=share_loc

        try:
            self.app=Application().connect(path=self.ViewSpecPro_loc)
        except:
            print('Starting ViewSpec Pro')
            self.app=Application().start(ViewSpecPro_loc)
        self.spec=self.app['ViewSpec Pro    Version 6.2'] 
        self.pid=self.app.process
        if self.spec.exists(): print('\tConnected to ViewSpec Pro')
    def reset(self):
        while self.app.Dialog.exists():
            self.app.Dialog.close()
    def process(self, input_path, output_path, tsv_name):
        files=os.listdir(output_path)
        for file in files:
            if '.sco' in file:
                os.remove(output_path+'\\'+file)
        print('processing files')
        self.spec.menu_select('File -> Close')
        self.open_files(input_path)
        time.sleep(1)
        
        self.set_save_directory(output_path)
        self.splice_correction()
        self.ascii_export(output_path, tsv_name)
        
        print('Processing complete. Cleaning directory.')
        self.spec.menu_select('File -> Close')
        files=os.listdir(output_path)
        for file in files:
            if '.sco' in file:
                os.remove(output_path+'\\'+file)
        
        print('Finished.')
    
    def open_files(self, path):
        print('Opening files from '+path)
        self.spec.menu_select('File -> Open')
        open=wait_for_window(self.app,'Select Input File(s)')
        open.set_focus()
        open['Address Band Root'].toolbar.button(0).click()
        #open['Address Band Root'].edit.set_edit_text(path)
        keyboard.SendKeys(path)
        open['Address Band Root'].edit.set_focus()
        keyboard.SendKeys('{ENTER}')
        print('opened files!')
        time.sleep(0.5) #Of this and next two sleeps, not sure if 1 or all is needed.
        #Make sure *.0** files are visible instead of just *.asd. Note that this won't work if you have over 100 files!!
        open.ComboBox2.select(0).click()
        time.sleep(0.5)
        open.ComboBox2.select(0).click()
        time.sleep(0.5)
        open.directUIHWND.ShellView.set_focus()
        keyboard.SendKeys('^a')
        keyboard.SendKeys('{ENTER}')
    
    def set_save_directory(self,path, force=False):
        print('setting save directory')
        print(path)
        dict=self.spec.menu().get_properties()
        print(dict)
        output_text=dict['menu_items'][3]['menu_items']['menu_items'][1]['text']
        print(output_text)
        self.spec.menu_select('Setup -> '+output_text)
        print('next')
        timeout=30
        save=None
        while timeout>0 and save==None:
            try:
                save=self.app['New Directory Path']
            except:
                time.sleep(3)
                timeout-=3
        path_el=path.split('\\')

        if path_el[0].upper()=='C:':
            for el in path_el:
                if el.upper()=='C:': 
                    #On some versions of Windows, ListBox will have c:\\, in others it has C:\\. Try both.
                    try:
                        save.ListBox.select('c:\\')
                    except:
                        save.ListBox.select('C:\\')
                else:
                    save.ListBox.select(el)
                print('Selecting '+el)
                self.select_item(save.ListBox.rectangle())
                print('Done')
        else:
            print('Invalid directory (must save to C drive)')
            # path_el=['C:\\','Users','RS3Admin','Temp']
            # for el in path_el:
            #     save.ListBox.select(el)
            #     self.select_item(save.ListBox.rectangle())
        save.OKButton.click()
        print('Clicked ok.')
        #If a dialog box comes up asking if you want to set the default input directory the same as the output, click no. Not sure if there is a different dialog box that could come up, so this doesn't seem very robust.
        try:
            self.app['Dialog'].Button2.click()
        except:
            pass
        #print('save directory set!')
        
    
    def splice_correction(self):
        print('Applying splice correction.')
        delay=self.spec.ListBox.item_count()/40+0.5 #We'll wait this long before clicking a button later.
        print(delay)
        self.select_all()
        self.spec.menu_select('Process -> Splice Correction')
        self.app['Splice Correct Gap'].set_focus()
        self.app['Splice Correct Gap'].button1.click_input()
        time.sleep(delay) #Needs to be longer depending on how many files you are processing.
        try:
            self.app['ViewSpecPro'].set_focus()
            self.app['ViewSpecPro'].button1.draw_outline()
            self.app['ViewSpecPro'].button1.click_input()
        except:
            print('Could not find dialog. Retrying')
            tries_remaining=100
            while tries_remaining>0:
                time.sleep(5)
                try:
                    self.app['ViewSpecPro'].set_focus()
                    self.app['ViewSpecPro'].button1.draw_outline()
                    self.app['ViewSpecPro'].button1.click_input()
                    tries_remaining=-1
                except:
                    print('Could not find dialog. Retrying')
                    tries_remaining-=1
                
        
    def ascii_export(self, path, tsv_name):
        print('Doing ASCII export.')
        self.select_all()
        self.spec.menu_select('Process -> ASCII Export')
        export=self.app['ASCII Export']
        export.ReflectanceRadioButton.check()
        export.AbsoluteCheckBox.check()
        export.OutputToASingleFileCheckBox.check()
        export.set_focus()
        time.sleep(2)
        export.Button2.click_input()
        
        save=self.app['Select Ascii File']
        save.set_focus()
        save.ToolBar2.double_click()
        keyboard.SendKeys(path)
        keyboard.SendKeys('{ENTER}')
        save.edit.set_edit_text(tsv_name)
        save.set_focus()
        time.sleep(2)
        save.OKButton.click_input()
        time.sleep(5)
        try:
            self.app['Dialog'].OKButton.click()
        except:
            time.sleep(30)
            try:
                print('Retrying')
                self.app['Dialog'].OKButton.click()
            except:
                timeout=800
                while 'Dialog' not in self.app and timeout>0:
                    print('Still looking...')
                    time.sleep(10)
                    timeout-=10
                self.app['Dialog'].OKButton.click()
        
        
    def select_all(self):
        for i in range(self.spec.ListBox.item_count()):
            self.spec.ListBox.select(i)
        
        
    def select_item(self,rectangle):
        #set start position at center top of listbox
        im=pyautogui.screenshot()
        x=rectangle.left+0.5*(rectangle.right-rectangle.left)
        x=int(x)
        y=rectangle.top

        
        while y<rectangle.bottom:
            if pyautogui.pixelMatchesColor(x,y,COLORS['file_highlight']):
                pyautogui.click(x=x,y=y, clicks=2)
                print('click')
                return
            y=y+3

class RS3Menu:

    def __init__(self, app):
        self.app=app
        self.display_delta_x=125
        self.control_delta_x=180
        self.GPS_delta_x=235
        self.help_delta_x=270


    def open_control_dialog(self, menuitems, timeout=10):
        self.spec=self.app['RS³   18483 1']
        if self.spec.exists()==False:
            print('RS3 not found. Failed to open save menu')
            return
        self.spec.set_focus()
        time.sleep(0.25) #Not sure if this is needed. On desktop, was clicking inside pyzo sometimes.
        x_left=self.spec.rectangle().left
        y_top=self.spec.rectangle().top
        
        while x_left<-10 or y_top<-10:
            x_left=self.spec.rectangle().left
            y_top=self.spec.rectangle().top
            time.sleep(0.25)
            
        width=300
        height=50
        controlregion=(x_left, y_top, width, height)

        loc=None
        found=False
        for _ in range(10*timeout):
            loc=find_image(IMG_LOC+'/rs3control.png',loc=controlregion)
            print(loc)
            if loc==None:
                print('Searching for image 2')
                loc=find_image(IMG_LOC+'/rs3control2.png',loc=controlregion)
                time.sleep(0.25)
            else:


                x=loc[0]+controlregion[0]
                y=loc[1]+controlregion[1]
                mouse.click(coords=(x,y))
                menuregion=(x, y, 100, 300)
                
                #Now that you've opened the menu, find the menu item.
                for _ in range(4*timeout):
                    loc2=find_image(menuitems[0], loc=menuregion)
                    if loc2==None and len(menuitems)>1:
                        loc2=find_image(menuitems[1], loc=menuregion)
                    if loc2 != None:
                        x=loc2[0]+menuregion[0]
                        y=loc2[1]+menuregion[1]
                        mouse.click(coords=(x,y))
                        found=True
                        break
                    else:
                        print('Searching for menu item')
                        time.sleep(0.25)
                #mouse.click(coords=(self.x_left+self.control_delta_x, self.y_menu))
                # for i in range(number):
                #     keyboard.SendKeys('{DOWN}')
                # keyboard.SendKeys('{ENTER}')
                break
        if not found:
            print('Menu item not found')
            raise Exception('Menu item not found')

        
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
    
def find_image(image, rect=None, loc=None):

    if rect != None:
        screenshot=pyautogui.screenshot(region=(rect.left, rect.top, rect.width(), rect.height()))
    else:
        screenshot=pyautogui.screenshot(region=loc)
    location=pyautogui.locate(image, screenshot)
    return location
