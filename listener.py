import time
import os
import imp
import sys

dev=True
RS3_running=True
ViewSpecPro_running=True

if dev: sys.path.append('c:/users/rs3admin/hozak/python/autospec/')

import asdcontrols

if dev:
    imp.reload(asdcontrols)
    from asdcontrols import RS3Controller
    from asdcontrols import ViewSpecProController

def main():
    spec_controller=RS3Controller(running=RS3_running)
    process_controller=ViewSpecProController(running=ViewSpecPro_running)
    
    cmds0=os.listdir('//PATATO/spec_share/commands/')
    while True:
        
        cmds=os.listdir('//PATATO/spec_share/commands/')
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
                        file=open('//PATATO/spec_share/commands/'+cmd,'r')
                        input_path=file.readline()
                        output_path=file.readline()
                        tsv_name=file.readline()
                        process_controller.process(input_path, output_path, tsv_name)
            cmds0=cmds
        time.sleep(1)
        cmds0
    
if __name__=='__main__':
    main()