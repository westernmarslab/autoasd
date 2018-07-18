import time
import os
import imp
import sys
import datetime
import pexpect

dev=True
RS3_running=False
ViewSpecPro_running=False

if dev: 
    sys.path.append('c:/users/rs3admin/hozak/python/autoasd/')
    #os.system('del C:\\Kathleen\commands\*')

import asdcontrols

share_loc='C:\\Kathleen'
read_command_loc=share_loc+'\\commands\\from_control'
write_command_loc='share_loc+\\commands\\from_spec'

if dev:
    imp.reload(asdcontrols)
    from asdcontrols import RS3Controller
    from asdcontrols import ViewSpecProController

def main():
    #logpath='C:/Users/RS3Admin/hozak/log.txt'
    #logpath='C:/Kathleen/log/log.txt'      
    logdir=share_loc+'\\log\\'+datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    try:
        os.mkdir(logdir)
    except(FileExistsError):
        try:
            os.mkdir(logdir+'_2')
        except:
            print('Seriously?')
    logline='test'
    open(logdir+'\\'+logline,'w+').close()
    # with open(logpath, 'w+') as log:
    #     log.write('Intiating listener on spec compy')

    delme=os.listdir(read_command_loc)
    print(delme)
    for file in delme:
        
    spec_controller=RS3Controller(share_loc, logdir, running=RS3_running)
    process_controller=ViewSpecProController(logdir, running=ViewSpecPro_running)
    
    files0=os.listdir(read_command_loc)
    while True:
        
        files=os.listdir(read_command_loc)
        if files==files0:
            print('no change')
        else:
            for file in files:
                if file not in files:
                    cmd,params=filename_to_cmd(file)
                    print(cmd)
                    if cmd=='spectrum': spec_controller.take_spectrum()
                    elif cmd=='saveconfig':
                        save_path=params[0]
                        basename=params[1]
                        startnum=params[2]
                        spec_controller.spectrum_save(save_path, basename, startnum)
                    elif cmd=='wr': spec_controller.white_reference()
                    elif cmd=='opt': spec_controller.optimize()
                    elif cmd=='process':
                        params=cmd.split('_')
                        input_path=params[0]                            
                        output_path=params[1]
                        tsv_name=params[2]
                        #file=open(share_loc+'/commands/'+cmd,'r')
                        # input_path=file.readline().strip('\n')
                        # output_path=file.readline().strip('\n')
                        # tsv_name=file.readline().strip('\n')
                        process_controller.process(input_path, output_path, tsv_name)
            files0=files
        time.sleep(1)
        
def filename_to_cmd(filename):
    cmd=filename.split('&')[0][:-1]
    print(cmd)
    params=filename.split('&')[1:]
    for i, param in params:
        params[i]=param.replace('+','\\').replace(':','=')
    return cmd,params
    
if __name__=='__main__':
    main()