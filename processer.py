# import pyautogui
# import sys
# def main():
# 
# 
#     print(sys.argv)
#     if '-wr' in sys.argv:
#         white_reference()
#     if '-sp' in sys.argv:
#         take_spectrum()
#         
# def white_reference():
#     #import pyautogui
#     pyautogui.click(126,56)
#     
# def take_spectrum():
#     #import pyautogui
#     #old = pyautogui.screenshot(region=(800,200,3, 800))
#     pyautogui.press('space')
#     
#         
# if __name__=="__main__":
#     main()
dev=True
running=True

from pywinauto import Application
from pywinauto import findwindows
from pywinauto import mouse
from pywinauto import keyboard
import pyautogui

import sys
import time
import os
import imp

if dev:
    os.chdir('C:\Program Files\AutoSpec')
    sys.path.append('c:/users/rs3admin/hozak/python/autospec/')

import controls

if dev:
    imp.reload(controls)
    from controls import Menu


def main():
    path='C:\\Users\\RS3Admin\\hozak\\test'
    path_el=path.split('\\')
    print(path_el)
    #each run, specify a folder and take all the contents?
    app=Application()
    if running:
        app=Application().connect(process=2372)
    pid=app.process
    # if dev:
    #     close_extra_windows(pid)
    spec=app['ViewSpec Pro    Version 6.2'] 
    # spec.menu_select('File -> Open')
    # open=app['Select Input File(s)']
    # open.ToolBar2.double_click()
    # keyboard.SendKeys(path)
    # keyboard.SendKeys('{ENTER}')
    # open.directUIHWND.ShellView.click_input()
    # keyboard.SendKeys('^a')
    # keyboard.SendKeys('{ENTER}')
    
    # spec.menu_select('Setup -> Output Directory')
    # save=app['New Directory Path']
    # for el in path_el:
    #     if el=='C:': el='C:\\'
    #     save.ListBox.select(el)
    #     select_item(save.ListBox.rectangle())

def take_spectrum():
    #import pyautogui
    #old = pyautogui.screenshot(region=(800,200,3, 800))
    pyautogui.press('space')
    
def spectrum_save(menu, pid, path, base, start_num=1, numfiles=1, interval=0, comment=None, new_file_format=False):
    print(pid)
    try:
        menu.open_save_dialog()
    except:
        print('failed to open save dialog. Check connection with spetrometer.')
    save=wait_for_window(pid, 'Spectrum Save', 3)
    #time.sleep(2)
    # elements=findwindows.find_elements(process=pid)
    # save=None

    #   for el in elements:
    #     print(el.name)
    #     if el.name=='Spectrum Save':
    #         save=Application().connect(handle=el.handle)
    #
    save=wait_for_window(pid,'Spectrum Save',5)  
    if save==None: print('ERROR: Failed to open save dialog')
    

    spec=save.ThunderRT6Form
    spec.Edit6.set_edit_text(path)
    spec.ThunderRT6PictureBoxDC3.click_input()
    elements=findwindows.find_elements(process=pid)
    for el in elements:
        if el.name=='Message':
            print('wait for input')
    #sys.stdout=open('c:/users/rs3admin/hozak/log/identifiers.txt','w')
    #spec.print_control_identifiers()

def wait_for_window(pid, title, timeout):
    t0=time.clock()
    elements=findwindows.find_elements(process=pid)
    app=None
    while app==None and time.clock()-t0<timeout:
        for el in elements:
            if el.name==title:
                app=Application().connect(handle=el.handle)
    return app
    
def select_item(rectangle):
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
    
    print('rats no blue')
    
   # print(im.getpixel
    #look within listbox for blue pixels and double click on them (you've already selected the directory you want)
    

def close_windows():
    print('rats')

if __name__=="__main__":
    main()