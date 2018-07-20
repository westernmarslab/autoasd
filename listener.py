import time
import os
import imp
import sys
import datetime
import pexpect

dev=True
RS3_running=True
ViewSpecPro_running=False
timeout=5


if dev: 
    sys.path.append('c:/users/rs3admin/hozak/python/autoasd/')
    #os.system('del C:\\Kathleen\commands\*')

import asdcontrols

share_loc='C:\\Kathleen'
read_command_loc=share_loc+'\\commands\\from_control'
write_command_loc=share_loc+'\\commands\\from_spec'
if dev:
    imp.reload(asdcontrols)
    from asdcontrols import RS3Controller
    from asdcontrols import ViewSpecProController

def main():
    cmdnum=0
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
    for file in delme:
        os.remove(read_command_loc+'\\'+file)
    
    delme=os.listdir(write_command_loc)
    for file in delme:
        os.remove(write_command_loc+'\\'+file)
        
    spec_controller=RS3Controller(share_loc, logdir, running=RS3_running)
    process_controller=ViewSpecProController(logdir, running=ViewSpecPro_running)
    
    files0=os.listdir(read_command_loc)
    print('time to listen!')
    data_files_to_ignore=[]
    while True:
        if spec_controller.save_dir!='':
            data_files=os.listdir(spec_controller.save_dir)
            for file in data_files:
                if file not in data_files_to_ignore:
                    if file not in spec_controller.hopefully_saved_files:
                        with open(write_command_loc+'\\unexpectedfile'+str(cmdnum)+'&'+file,'w+') as f:
                                pass
                        #cmdnum+=1
                            
                        
        
        files=os.listdir(read_command_loc)
        if files!=files0:
            for file in files:
                if file not in files0:
                    print('here is the file and what it is parsed to:')
                    print(file)
                    cmd,params=filename_to_cmd(file)
                    print(params)
                    os.remove(read_command_loc+'\\'+file)
                    if 'spectrum' in cmd: 
                        old=len(spec_controller.hopefully_saved_files)
                        spec_controller.take_spectrum()
                        wait=True
                        while wait:
                            time.sleep(1)
                            new=len(spec_controller.hopefully_saved_files)
                            if new>old:
                                wait=False
                        filename=spec_controller.hopefully_saved_files[-1]
                        saved=False
                        t0=time.clock()
                        t=time.clock()
                        if filename != 'unknown':
                            print(filename)
                            while t-t0<timeout and saved==False:
                                saved=os.path.isfile(filename)
                                time.sleep(1)
                                t=time.clock()
                        print('file saved and found?:'+ str(saved))
                        print('here is the filename I am trying to put in a command string:')
                        print(filename)
                        if saved:
                            filestring=cmd_to_filename('savedfile'+str(cmdnum),[filename])
                        else:
                            filestring=cmd_to_filename('failedtosavefile'+str(cmdnum),[filename])
                        print('here is my command string:')
                        print(filestring)
                            
                        with open(write_command_loc+'\\'+filestring,'w+') as f:
                            pass
                        cmdnum+=1
                    elif 'saveconfig' in cmd:
                        save_path=params[0]
                        basename=params[1]
                        startnum=params[2]
                        try:
                            spec_controller.spectrum_save(save_path, basename, startnum)
                        except:
                            with open(write_command_loc+'\\saveconfigerror'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                    elif 'wr' in cmd: spec_controller.white_reference()
                    elif 'opt' in cmd: spec_controller.optimize()
                    elif 'process' in cmd:
                        input_path=params[0]                            
                        output_path=params[1]
                        tsv_name=params[2]
                        try:
                            process_controller.process(input_path, output_path, tsv_name)

                        except:
                            with open(write_command_loc+'\\processerror'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                    elif 'ignorefile' in cmd:
                        print('hooray!')
                        data_files_to_ignore.append('hooray!')
                    elif 'rmfile' in cmd:
                        print('not actually removing anything!')
                            
            files0=files
        time.sleep(1)
        
def filename_to_cmd(filename):
    cmd=filename.split('&')[0]
    params=filename.split('&')[1:]
    i=0
    for param in params:
        params[i]=param.replace('+','\\').replace('=',':')
        i=i+1
    return cmd,params
    
def cmd_to_filename(cmd, params):
    filename=cmd
    i=0
    for param in params:
        filename=filename+'&'+param.replace('\\','+').replace(':','=')
        i=i+1
    return filename
    
if __name__=='__main__':
    main()