print('foo')

# dev=True
# running=True
# 
# from pywinauto import Application
# from pywinauto import findwindows
# from pywinauto import mouse
# 
# import sys
# import time
# import os
# import imp
# 
# if dev:
#     os.chdir('C:\Program Files\AutoSpec')
#     sys.path.append('c:/users/rs3admin/hozak/python/autospec/')
# 
# import controls
# 
# if dev:
#     imp.reload(controls)
#     from controls import Menu

class SpectrometerController:

    def __init__(self, running=False):
        pass
        # self.app=Application()
        # if running:
        #     app=Application().connect(path=r"C:\Program Files\ASD\RS3\RS3.exe")
        # else:
        #     app=Application().start(path=r"C:\Program Files\ASD\RS3\RS3.exe")

        # self.spec=app.ThunderRT6Form
        # self.spec.draw_outline()
        # menu=Menu(pid,spec)
        # #spec.ThunderRT6PictureBox12.draw_outline()
        # # print(os.chdir('c:/users/rs3admin'))
        # # sys.stdout=open('c:/users/rs3admin/hozak/log/identifiers.txt','w')
        # # spec.print_control_identifiers()
        # spectrum_save(menu,pid, 'foo','foo2')
        # # spec.ThunderRT6UserControlDC.draw_outline()
        # # spec.ThunderRT6UserControlDC.Illuminate.draw_outline()
    
        
    # def white_reference(self):
    #     self.spec.set_focus()
    #     keyboard.send_keys('{F4}')
    #     
    # def take_spectrum(self):
    #     self.spec.set_focus()
    #     pyautogui.press('space')
    #     
    # def spectrum_save(self, menu, pid, path, base, start_num=1, numfiles=1, interval=0, comment=None, new_file_format=False):
    #     print(pid)
    #     try:
    #         menu.open_save_dialog()
    #     except:
    #         print('failed to open save dialog. Check connection with spetrometer.')
    #     save=wait_for_window(pid, 'Spectrum Save', 3)
    #     #time.sleep(2)
    #     # elements=findwindows.find_elements(process=pid)
    #     # save=None
    # 
    #     #   for el in elements:
    #     #     print(el.name)
    #     #     if el.name=='Spectrum Save':
    #     #         save=Application().connect(handle=el.handle)
    #     #
    #     save=wait_for_window(pid,'Spectrum Save',5)  
    #     if save==None: print('ERROR: Failed to open save dialog')
    #     
    # 
    #     spec=save.ThunderRT6Form
    #     spec.Edit6.set_edit_text(path)
    #     spec.ThunderRT6PictureBoxDC3.click_input()
    #     elements=findwindows.find_elements(process=pid)
    #     for el in elements:
    #         if el.name=='Message':
    #             print('wait for input')
    #     #sys.stdout=open('c:/users/rs3admin/hozak/log/identifiers.txt','w')
    #     #spec.print_control_identifiers()
    # 
    # def wait_for_window(pid, title, timeout):
    #     t0=time.clock()
    #     elements=findwindows.find_elements(process=pid)
    #     app=None
    #     while app==None and time.clock()-t0<timeout:
    #         for el in elements:
    #             if el.name==title:
    #                 app=Application().connect(handle=el.handle)
    #     return app
    # 
    # def close_windows():
    #     print('rats')
