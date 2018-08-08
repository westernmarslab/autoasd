import time
import os
import imp
import sys
import datetime
import pexpect

dev=True
computer='new'
RS3_running=True
ViewSpecPro_running=False
timeout=5
share_loc=''
RS3_loc=''
ViewSpecPro_loc=''


if computer == 'old': 
    sys.path.append('c:/users/rs3admin/hozak/python/autoasd/')
    #os.system('del C:\\Kathleen\commands\*')
    os.chdir('c:/users/rs3admin/hozak/python/autoasd')
    share_loc='C:\\Kathleen'
    RS3_loc=r"C:\Program Files\ASD\RS3\RS3.exe"
    ViewSpecPro_loc=r"C:\Program Files\ASD\ViewSpecPro\ViewSpecPro.exe"
    
elif computer =='new':
    sys.path.append('C:\\users\\hozak\\Python\\Autoasd')
    os.chdir('C:\\users\\hozak\\Python\\Autoasd')
    share_loc='C:\\SpecShare'
    RS3_loc=r"C:\Program Files (x86)\ASD\RS3\RS3.exe"
    ViewSpecPro_loc=r"C:\Program Files (x86)\ASD\ViewSpecPro\ViewSpecPro.exe"

import asdcontrols

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
        
    spec_controller=RS3Controller(share_loc, RS3_loc, logdir, running=RS3_running)
    process_controller=ViewSpecProController(ViewSpecPro_loc,logdir, running=ViewSpecPro_running)
    
    files0=os.listdir(read_command_loc)
    print('time to listen!')
    data_files_to_ignore=[]
    while True:
        data_files=[]
        try:
            data_files=os.listdir(spec_controller.save_dir)
        except:
            pass
        expected_files=[]

        for file in spec_controller.hopefully_saved_files:
            expected_files.append(file.split('\\')[-1])
        for file in data_files:
            #print('This file is here:'+file)
            if file not in data_files_to_ignore:
                if file not in expected_files:
                    #print('And it is not expected.')
                    with open(write_command_loc+'\\unexpectedfile'+str(cmdnum)+'&'+file,'w+') as f:
                            pass
                    
                    cmdnum+=1
                    data_files_to_ignore.append(file)

            #print("this is a sloppy way to catch an exception when spec_controller.save_dir doesn't exist")
                            
                        
        files=os.listdir(read_command_loc)
        if files!=files0:
            print('***************')
            for file in files:
                if file not in files0:
                    print(file)
                    cmd,params=filename_to_cmd(file)
                    #os.remove(read_command_loc+'\\'+file)
                    if 'spectrum' in cmd: 
                        old=len(spec_controller.hopefully_saved_files)
                        if spec_controller.save_dir=='':
                            with open(write_command_loc+'\\noconfig'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            continue
                        print('spectra config: '+str(spec_controller.numspectra))
                        if spec_controller.numspectra==None:
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            continue
                        if False:
                            filename=spec_controller.save_dir+'\\'+spec_controller.basename+'.'+spec_controller.nextnum
                        elif True:
                            filename=spec_controller.save_dir+'\\'+spec_controller.basename+spec_controller.nextnum+'.asd'
                        exists=False
                        print('here I am about to check if it is a file in the spectrum '+spec_controller.save_dir+'\\'+filename)
                        os.listdir(spec_controller.save_dir)
                        if os.path.isfile(spec_controller.save_dir+'\\'+filename):
                            exists=True
                            print('here I am!')
                            with open(write_command_loc+'\\fileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            files0=files
                            continue
                        print('telling spec controller to take a spectrum')
                        spec_controller.take_spectrum(filename)
                        wait=True
                        while wait:
                            time.sleep(0.2)
                            new=len(spec_controller.hopefully_saved_files)
                            if new>old:
                                wait=False
                        saved=False
                        t0=time.clock()
                        t=time.clock()
                        while t-t0<int(spec_controller.numspectra)*4 and saved==False:
                            saved=os.path.isfile(filename)
                            time.sleep(0.2)
                            t=time.clock()
                        print(filename+' saved and found?:'+ str(saved))
                        spec_controller.numspectra=str(int(spec_controller.numspectra)-1)
                        spec_controller.numspectra=str(int(spec_controller.numspectra)+1)
                        if saved:
                            filestring=cmd_to_filename('savedfile'+str(cmdnum),[filename])
                        else:
                            spec_controller.hopefully_saved_files.pop(-1)
                            print(type(spec_controller.numspectra))
                            spec_controller.numspectra=str(int(spec_controller.numspectra)-1)
                            filestring=cmd_to_filename('failedtosavefile'+str(cmdnum),[filename])
                            
                        with open(write_command_loc+'\\'+filestring,'w+') as f:
                            pass
                        cmdnum+=1
                    elif 'saveconfig' in cmd:
                        save_path=params[0]
                        basename=params[1]
                        startnum=params[2]
                        filename=save_path+'\\'+basename+'.'+startnum
                        if os.path.isfile(filename):
                            print('Cannot set saveconfig: '+filename+' already exists.')
                            with open(write_command_loc+'\\fileexists'+str(cmdnum),'w+') as f:
                                pass
                            files0=files
                            cmdnum+=1
                            #continue
                            skip_spectrum()
                            #files0=files
                            continue
                        spec_controller.spectrum_save(save_path, basename, startnum)
                            
                        if spec_controller.failed_to_open:
                            spec_controller.failed_to_open=False
                            with open(write_command_loc+'\\saveconfigerror'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            #files0=files
                            #continue
                            skip_spectrum()
                        else:
                            with open(write_command_loc+'\\saveconfigsuccess'+str(cmdnum),'w+') as f:
                                pass
                                cmdnum+=1
                            
                    elif 'wr' in cmd: spec_controller.white_reference()
                    elif 'opt' in cmd: spec_controller.optimize()
                    elif 'process' in cmd:
                        input_path=params[0]                            
                        output_path=params[1]
                        tsv_name=params[2]
                        filename=output_path+'\\'+tsv_name
                        print(filename)
                        if os.path.isfile(filename):
                            print('do not process')
                            with open(write_command_loc+'\\processerror'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            continue
                        try:
                            print('trying to process')
                            process_controller.process(input_path, output_path, tsv_name)

                        except:
                            process_controller.reset()
                            with open(write_command_loc+'\\processerror'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    elif 'instrumentconfig' in cmd:
                        spec_controller.instrument_config(params[0])
                    elif 'ignorefile' in cmd:
                        print('hooray!')
                        data_files_to_ignore.append('hooray!')
                    elif 'rmfile' in cmd:
                        print('not actually removing anything!')
        time.sleep(0.5)
        files0=files
        
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

def skip_spectrum():
    time.sleep(2)
    print('remove spec commands')
    files=os.listdir(read_command_loc)
    #print(files)
    for file in files:
        if 'spectrum' in file:
            os.remove(read_command_loc+'\\'+file)
    #print(os.listdir(read_command_loc))
    time.sleep(1)

if __name__=='__main__':
    main()