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
    app=Application()
    if running:
        app=Application().connect(title='RS³',class_name='ThunderRT6Main')
    spec=app.ThunderRT6Form
    spec.draw_outline()
    menu=Menu(spec)
    #spec.ThunderRT6PictureBox12.draw_outline()
    # print(os.chdir('c:/users/rs3admin'))
    # sys.stdout=open('c:/users/rs3admin/hozak/log/identifiers.txt','w')
    # spec.print_control_identifiers()
    spectrum_save(menu, 'foo','foo2')
    # spec.ThunderRT6UserControlDC.draw_outline()
    # spec.ThunderRT6UserControlDC.Illuminate.draw_outline()
    
        
def white_reference():
    #import pyautogui
    pyautogui.click(126,56)
    
def take_spectrum():
    #import pyautogui
    #old = pyautogui.screenshot(region=(800,200,3, 800))
    pyautogui.press('space')
    
def spectrum_save(menu, path, base, start_num=1, numfiles=1, interval=0, comment=None, new_file_format=False):
    print('going to save')
    menu.open_save_dialog()
    time.sleep(1)
    save=Application().connect(class_name='ThunderRT6FormDC',title='Spectrum Save')
    process_id=save.process
    spec=save.ThunderRT6Form
    spec.Edit6.set_edit_text(path)
    spec.ThunderRT6PictureBoxDC3.click_input()
    elements=findwindows.find_elements(process=process_id)
    for el in elements:
        if el.name=='Message':
            print('wait for input')
    sys.stdout=open('c:/users/rs3admin/hozak/log/identifiers.txt','w')
    spec.print_control_identifiers()
        
if __name__=="__main__":
    main()