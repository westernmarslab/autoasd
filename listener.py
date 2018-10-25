import time
import os
import imp
import sys
import datetime
import pexpect
from shutil import copyfile

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
data_loc=share_loc
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
        
    with open(write_command_loc+'\\started'+str(cmdnum),'w+') as f:
            pass
    cmdnum+=1

        
    spec_controller=RS3Controller(share_loc, RS3_loc, logdir, running=RS3_running)
    process_controller=ViewSpecProController(share_loc, ViewSpecPro_loc,logdir, running=ViewSpecPro_running)
    
    cmdfiles0=os.listdir(read_command_loc)
    
    print('time to listen!')
    with open(write_command_loc+'\\ready'+str(cmdnum),'w+') as f:
            pass
    cmdnum+=1

    wait_for_saveconfig_before_doing_instrument_config=False
    instrument_config_num=None
    
    data_files_to_ignore=[]
    lost_connection_count=0
    while True:
        #check connectivity with spectrometer
        connected=spec_controller.check_connectivity()
        if not connected:
            with open(write_command_loc+'\\lostconnection'+str(cmdnum),'w+') as f:
                pass
            cmdnum+=1
            continue
                
        
        #check for unexpected files in data adirectory
        file=check_for_unexpected(spec_controller.save_dir, spec_controller.hopefully_saved_files, data_files_to_ignore)
        while file !=None:
            data_files_to_ignore.append(file)
            with open(write_command_loc+'\\unexpectedfile'+str(cmdnum)+'&'+file,'w+') as f:
                    pass
            cmdnum+=1
            file=check_for_unexpected(spec_controller.save_dir, spec_controller.hopefully_saved_files, data_files_to_ignore)
               
                 
        #check for new commands in the read_command location
        cmdfiles=os.listdir(read_command_loc)

        if cmdfiles!=cmdfiles0:
            print('***************')
            for file in cmdfiles:
                if file not in cmdfiles0:
                    print(file)
                    cmd,params=filename_to_cmd(file)
                    print(cmd)
                    # if not connected:
                    #     print('not connected')
                    #     if 'retryconnection' in cmd:
                    #         connected=spec_controller.check_connectivity()
                    #         if connected:
                    #             print('reconnected')
                    #         else:
                    #             continue
                    #     else:
                    #         time.sleep(0.25)
                    #         continue
                    if 'checkwriteable' in cmd:
                        try:
                            os.mkdir(params[0]+'\\autospec_temp')
                            os.removedirs(params[0]+'\\autospec_temp')
                            print('writeable')
                            with open(write_command_loc+'\\yeswriteable'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            #writeable=False
                            print('not writeable')
                            with open(write_command_loc+'\\notwriteable'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    #os.remove(read_command_loc+'\\'+file)
                    elif 'spectrum' in cmd: 
                        # if wait_for_saveconfig_before_doing_instrument_config:
                        #     spec_controller.instrument_config(instrument_config_num)
                        #     wait_for_saveconfig_before_doing_instrument_config=False
                        #     instrument_config_num=None
                        if spec_controller.save_dir=='':
                            with open(write_command_loc+'\\noconfig'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        if spec_controller.numspectra==None:
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                            
                        #We'll wait for this number to change after requesting a spectrum save.
                        old=len(spec_controller.hopefully_saved_files)
                        if computer=='old':
                            filename=params[0]+'\\'+params[1]+'.'+params[2]
                        elif computer=='new':
                            filename=params[0]+'\\'+params[1]+params[2]+'.asd'
                        exists=False
                        os.listdir(spec_controller.save_dir)
                        if os.path.isfile(filename):
                            exists=True
                            with open(write_command_loc+'\\savespecfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        spec_controller.take_spectrum(filename)

                        while True:
                            time.sleep(0.2)
                            new=len(spec_controller.hopefully_saved_files)
                            if new>old:
                                break
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
                        print('saveconfig')
                        save_path=params[0]
                        file=check_for_unexpected(save_path, spec_controller.hopefully_saved_files, data_files_to_ignore)
                        found_unexpected=False
                        while file !=None:
                            found_unexpected=True
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
                            with open(write_command_loc+'\\saveconfigfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            #files0=files
                            cmdnum+=1
                            #continue
                            skip_spectrum()
                            wait_for_saveconfig_before_doing_instrument_config=False
                            instrument_config_num=None
                            #files0=files
                            cmdfiles0=cmdfiles
                            continue
                        try:
                            spec_controller.spectrum_save(save_path, basename, startnum)
                            if spec_controller.failed_to_open:
                                spec_controller.failed_to_open=False
                                with open(write_command_loc+'\\saveconfigerror'+str(cmdnum),'w+') as f:
                                    pass
                                cmdnum+=1

                                #This can be deleted, we don't wait for saveconfig anymore.
                                wait_for_saveconfig_before_doing_instrument_config=False
                                instrument_config_num=None
                                skip_spectrum()
                            else:
                                with open(write_command_loc+'\\saveconfigsuccess'+str(cmdnum),'w+') as f:
                                    pass
                                    cmdnum+=1
                        except:
                            spec_controller.failed_to_open=False
                            with open(write_command_loc+'\\saveconfigerror'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            skip_spectrum()
                            instrument_config_num=None



                            
                    elif 'wr' in cmd and 'writeable' not in cmd: 
                        if spec_controller.save_dir=='':
                            with open(write_command_loc+'\\noconfig'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        if spec_controller.numspectra==None:
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                            
                        if computer=='old':
                            filename=spec_controller.save_dir+'\\'+spec_controller.basename+'.'+spec_controller.nextnum
                        elif computer=='new':
                            filename=spec_controller.save_dir+'\\'+spec_controller.basename+spec_controller.nextnum+'.asd'
                        exists=False
                        
                        #os.listdir(spec_controller.save_dir)
                        if os.path.isfile(filename):
                            
                            exists=True
                            with open(write_command_loc+'\\wrfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        spec_controller.white_reference()
                        while spec_controller.wr_success==False:
                            time.sleep(1)
                        with open(write_command_loc+'\\wrsuccess'+str(cmdnum),'w+') as f:
                            pass
                        cmdnum+=1
                        
                    elif 'opt' in cmd: 
                        if spec_controller.numspectra==None:
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        try:
                            spec_controller.optimize()
                            with open(write_command_loc+'\\optsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\optfailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                   
                    elif 'process' in cmd:
                        input_path=params[0]                            
                        output_path=params[1]
                        tsv_name=params[2]
                        if os.path.isfile(output_path+'\\'+tsv_name):
                            with open(write_command_loc+'\\processerrorfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        writeable=os.access(output_path,os.W_OK)
                        try:
                            os.mkdir(output_path+'\\delme')
                            os.removedirs(output_path+'\\delme')
                        except:
                            writeable=False
                       
                        if not writeable:
                            with open(write_command_loc+'\\processerrorcannotwrite'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        else:
                            if output_path[0:3]!='C:\\':
                                temp_output_path='C:\\SpecShare\\temp'
                            else:
                                temp_output_path=output_path
                            
                            filename=temp_output_path+'\\'+tsv_name
                            print(temp_output_path)

                            try:
                                process_controller.process(input_path, temp_output_path, tsv_name)
    
                                saved=False
                                t0=time.clock()
                                t=time.clock()
                                while t-t0<5 and saved==False:
                                    saved=os.path.isfile(filename)
                                    time.sleep(0.2)
                                    t=time.clock()
                                if saved:
                                    if temp_output_path!=output_path:
                                        tempfilename=filename
                                        filename=output_path+'\\'+tsv_name
                                        os.system('move '+tempfilename+' '+filename)
                                        print('yay moved fine')
                                    print(spec_controller.save_dir)
                                    if spec_controller.save_dir!=None and spec_controller.save_dir!='':
                                        if spec_controller.save_dir in filename:
                                            print(spec_controller.save_dir)
                                            print('going to check expected')
                                            expected=filename.split(spec_controller.save_dir)[1].split('\\')[1]
                                            print(expected)
                                            spec_controller.hopefully_saved_files.append(expected)
                                    print('going to say success')
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
                        instrument_config_num=params[0]
                        try:
                            spec_controller.instrument_config(instrument_config_num)
                            with open(write_command_loc+'\\iconfigsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\iconfigfailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                    #I am really not sure what this was all about...
                    elif 'ignorefile' in cmd:
                        print('hooray!')
                        data_files_to_ignore.append('hooray!')
                    elif 'rmfile' in cmd:
                        try:
                            delme=params[0]+'\\'+params[1]+params[2]+'.asd'
                            os.remove(delme)
                            with open(write_command_loc+'\\rmsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\rmfailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    elif 'getdata' in cmd:
                        print('getting data')
                        print(params[0])
                        try:
                            copyfile(params[0],data_loc+'\\temp.tsv')
                            with open(write_command_loc+'\\datacopied'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except Exception as e:
                            print(str(e))
                            with open(write_command_loc+'\\datafailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    elif 'listdir' in cmd:

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
                        except(PermissionError):
                            print('permission')
                            with open(write_command_loc+'\\'+'listdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\'+'listdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                    elif 'listcontents' in cmd:

                        try:
                            dir=params[0]
                            if dir[-1]!='\\':dir+='\\'
                            cmdfilename=cmd_to_filename(cmd,[params[0]])
                            files=os.listdir(dir)
                            sorted_files=[]
                            for i, file in enumerate(files):
                                if os.path.isdir(dir+file) and file[0]!='.':
                                    sorted_files.append(file)
                                elif file[0]!='.':
                                    #This is a way for the control compy to differentiate files from directories
                                    sorted_files.append('~:'+file)
                            sorted_files.sort()
                            with open(write_command_loc+'\\'+cmdfilename,'w+') as f:
                                for file in sorted_files:
                                    f.write(file+'\n')
                            cmdnum+=1
                        except(PermissionError):
                            print('permission')
                            with open(write_command_loc+'\\'+'listdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\'+'listdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                    elif 'mkdir' in cmd:
                        try:
                            os.makedirs(params[0])
                            if spec_controller.save_dir!=None and spec_controller.save_dir!='':
                                print(params[0])
                                if '\\'.join(params[0].split('\\')[:-1])==spec_controller.save_dir:
                                    expected=params[0].split(spec_controller.save_dir)[1].split('\\')[1]
                                    spec_controller.hopefully_saved_files.append(expected)
                            
                            with open(write_command_loc+'\\'+'mkdirsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except(FileExistsError):
                            print(params[0])
                            with open(write_command_loc+'\\'+'mkdirfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except(PermissionError):
                            with open(write_command_loc+'\\'+'mkdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\'+'mkdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        
        time.sleep(0.25)
        cmdfiles0=cmdfiles
        
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