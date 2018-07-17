import time
import os
import imp
import sys

dev=True
RS3_running=True
ViewSpecPro_running=True

if dev: 
    sys.path.append('c:/users/rs3admin/hozak/python/autospec/')
    #os.system('del C:\\Kathleen\commands\*')

import asdcontrols

share_loc='C:\Kathleen'

if dev:
    imp.reload(asdcontrols)
    from asdcontrols import RS3Controller
    from asdcontrols import ViewSpecProController

def main():
    delme=os.listdir(share_loc+'/commands/')
    for file in delme:
        cmd='del C:\\Kathleen\\commands\\'+file
        os.system(cmd)
    spec_controller=RS3Controller(running=RS3_running)
    process_controller=ViewSpecProController(running=ViewSpecPro_running)
    
    cmds0=os.listdir(share_loc+'/commands/')
    while True:
        
        cmds=os.listdir(share_loc+'/commands/')
        if cmds==cmds0:
            print('no change')
        else:
            for cmd in cmds:
                if cmd not in cmds0:
                    print(cmd)
                    if 'spectrum' in cmd: spec_controller.take_spectrum()
                    elif 'wr' in cmd: spec_controller.white_reference()
                    elif 'opt' in cmd: spec_controller.optimize()
                    elif 'process' in cmd:
                        params=cmd.split('_')
                        input_path=params[2].replace('-','\\')
                        input_path=input_path.replace('&',':')
                        output_path=params[3].replace('-','\\')
                        output_path=output_path.replace('&',':')
                        tsv_name=params[4]
                        #file=open(share_loc+'/commands/'+cmd,'r')
                        # input_path=file.readline().strip('\n')
                        # output_path=file.readline().strip('\n')
                        # tsv_name=file.readline().strip('\n')
                        process_controller.process(input_path, output_path, tsv_name)
            cmds0=cmds
        time.sleep(1)
        cmds0
    
if __name__=='__main__':
    main()