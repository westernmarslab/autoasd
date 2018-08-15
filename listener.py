import time
import os
import imp
import sys
import datetime
import pexpect

dev=True
computer='new'
#computer='new'
RS3_running=True
ViewSpecPro_running=False
timeout=5
share_loc=''
RS3_loc=''
ViewSpecPro_loc=''



if computer == 'old': 
    sys.path.append('c:/users/rs3admin/hozak/python/autoasd/')
    #os.system('del C:\\SpecShare\commands\*')
    os.chdir('c:/users/rs3admin/hozak/python/autoasd')
    share_loc='C:\\SpecShare'
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
    #logpath='C:/SpecShare/log/log.txt'      
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
    process_controller=ViewSpecProController(share_loc, ViewSpecPro_loc,logdir, running=ViewSpecPro_running)
    
    files0=os.listdir(read_command_loc)
    print('time to listen!')

    wait_for_saveconfig_before_doing_instrument_config=False
    instrument_config_num=None
    
    data_files_to_ignore=[]
    while True:
        
        file=check_for_unexpected(spec_controller.save_dir, spec_controller.hopefully_saved_files, data_files_to_ignore)
        while file !=None:
            data_files_to_ignore.append(file)
            with open(write_command_loc+'\\unexpectedfile'+str(cmdnum)+'&'+file,'w+') as f:
                    pass
            cmdnum+=1
            print('outside save config, seeing unexpected file')
            file=check_for_unexpected(spec_controller.save_dir, spec_controller.hopefully_saved_files, data_files_to_ignore)

            #print("this is a sloppy way to catch an exception when spec_controller.save_dir doesn't exist")
                            
                        
        files=os.listdir(read_command_loc)
        if wait_for_saveconfig_before_doing_instrument_config==True:
            spec_controller.instrument_config(instrument_config_num)
            wait_for_saveconfig_before_doing_instrument_config=False
            instrument_config_num=None
        if files!=files0:
            print('***************')
            for file in files:
                if file not in files0:
                    print(file)
                    cmd,params=filename_to_cmd(file)
                    #os.remove(read_command_loc+'\\'+file)
                    if 'spectrum' in cmd: 
                        if wait_for_saveconfig_before_doing_instrument_config:
                            spec_controller.instrument_config(instrument_config_num)
                            wait_for_saveconfig_before_doing_instrument_config=False
                            instrument_config_num=None
                        old=len(spec_controller.hopefully_saved_files)
                        if spec_controller.save_dir=='':
                            with open(write_command_loc+'\\noconfig'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            continue
                        if spec_controller.numspectra==None:
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            continue
                        if computer=='old':
                            filename=params[0]+'\\'+params[1]+'.'+params[2]
                        elif computer=='new':
                            filename=params[0]+'\\'+params[1]+params[2]+'.asd'
                        exists=False
                        print('here I am about to check if it is a file in the spectrum '+filename)
                        os.listdir(spec_controller.save_dir)
                        if os.path.isfile(filename):
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
                            print(new)
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
                        file=check_for_unexpected(save_path, spec_controller.hopefully_saved_files, data_files_to_ignore)
                        found_unexpected=False
                        while file !=None:
                            found_unexpected=True
                            print('found unexpected in saveconfig:'+file)
                            data_files_to_ignore.append(file)
                            with open(write_command_loc+'\\unexpectedfile'+str(cmdnum)+'&'+file,'w+') as f:
                                    pass
                            cmdnum+=1
                            file=check_for_unexpected(save_path, spec_controller.hopefully_saved_files, data_files_to_ignore)
                        if found_unexpected==True:
                            time.sleep(2)
                        with open(write_command_loc+'\\donelookingforunexpected'+str(cmdnum),'w+') as f:
                                    pass
                        
                        basename=params[1]
                        startnum=params[2]
                        filename=''
                        if computer=='old':
                            filename=save_path+'\\'+basename+'.'+startnum
                        elif computer=='new':
                            filename=save_path+'\\'+basename+startnum+'.asd'
                        print('checking for '+filename+' in saveconfig')
                        if os.path.isfile(filename):
                            print('Cannot set saveconfig: '+filename+' already exists.')
                            with open(write_command_loc+'\\fileexists'+str(cmdnum),'w+') as f:
                                pass
                            files0=files
                            cmdnum+=1
                            #continue
                            skip_spectrum()
                            wait_for_saveconfig_before_doing_instrument_config=False
                            instrument_config_num=None
                            #files0=files
                            continue
                        print('ready to do spectrum_save')
                        spec_controller.spectrum_save(save_path, basename, startnum)
                            
                        if spec_controller.failed_to_open:
                            spec_controller.failed_to_open=False
                            with open(write_command_loc+'\\saveconfigerror'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            #files0=files
                            #continue
                            wait_for_saveconfig_before_doing_instrument_config=False
                            instrument_config_num=None
                            skip_spectrum()
                        else:
                            with open(write_command_loc+'\\saveconfigsuccess'+str(cmdnum),'w+') as f:
                                pass
                                cmdnum+=1
                            
                    elif 'wr' in cmd: 
                        spec_controller.white_reference()
                        while spec_controller.wr_success==False:
                            time.sleep(1)
                            print('waiting for wr success')
                        with open(write_command_loc+'\\wrsuccess'+str(cmdnum),'w+') as f:
                            pass
                        cmdnum+=1
                    elif 'opt' in cmd: spec_controller.optimize()
                    elif 'process' in cmd:
                        input_path=params[0]                            
                        output_path=params[1]
                        tsv_name=params[2]
                        filename=output_path+'\\'+tsv_name
                        print(filename)
                        if os.path.isfile(filename):
                            print('do not process')
                            with open(write_command_loc+'\\processerrorfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            continue
                        try:
                            print('trying to process')
                            process_controller.process(input_path, output_path, tsv_name)
                            print('check if it actually saved')
                            print(filename)
                            saved=False
                            t0=time.clock()
                            t=time.clock()
                            while t-t0<5 and saved==False:
                                saved=os.path.isfile(filename)
                                time.sleep(0.2)
                                t=time.clock()
                            if saved:
                                with open(write_command_loc+'\\processsuccess'+str(cmdnum),'w+') as f:
                                    pass
                            else:
                                with open(write_command_loc+'\\processerrorwropt'+str(cmdnum),'w+') as f:
                                    pass
                            cmdnum+=1
                        except:
                            process_controller.reset()
                            with open(write_command_loc+'\\processerror'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    elif 'instrumentconfig' in cmd:
                        print('check for saveconfig first')
                        wait_for_saveconfig_before_doing_instrument_config=True
                        instrument_config_num=params[0]
                        continue
                    elif 'ignorefile' in cmd:
                        print('hooray!')
                        data_files_to_ignore.append('hooray!')
                    elif 'rmfile' in cmd:
                        print('not actually removing anything!')
                    elif 'listdir' in cmd:
                        try:
                            os.remove(read_command_loc+'\\'+file)
                        except:
                            time.sleep(1)
                            os.remove(read_command_loc+'\\'+file)
                        try:
                            dir=params[0]
                            if dir[-1]!='\\':dir+='\\'
                            cmdfilename=cmd_to_filename(cmd,[params[0]])
                            files=os.listdir(dir)
                            with open(write_command_loc+'\\'+cmdfilename,'w+') as f:
                                for file in files:
                                    if os.path.isdir(dir+file) and file[0]!='.':
                                        f.write(file+'\n')
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\'+'listdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    elif 'mkdir' in cmd:
                        os.remove(read_command_loc+'\\'+file)
                        try:
                            os.mkdir(params[0])
                            print('succeeding')
                            with open(write_command_loc+'\\'+'mkdirsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            print('failing')
                            with open(write_command_loc+'\\'+'mkdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        
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

def check_for_unexpected(save_dir, hopefully_saved_files, data_files_to_ignore):
    data_files=[]
    try:
        data_files=os.listdir(save_dir)
    except:
        pass
    expected_files=[]
    for file in hopefully_saved_files:
        expected_files.append(file.split('\\')[-1])
    for file in data_files:
        #print('This file is here:'+file)
        if file not in data_files_to_ignore:
            if file not in expected_files:
                #print('And it is not expected.')
                return file
    return None

if __name__=='__main__':
    main()