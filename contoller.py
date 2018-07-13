import time
import os
import imp
import sys

dev=True

if dev: sys.path.append('c:/users/rs3admin/hozak/python/autospec/')

import spectrometer_controller
import processor
import controls

if dev:
    #imp.reload(spectrum_taker)
    #from spectrum_taker import SpectrometerController
    imp.reload(spectrometer_controller)
    from spectrometer_controller import SpectrometerController
    imp.reload(processor)

def main():
    spec_controller=SpectrometerController(running=True)
    
    cmds0=os.listdir('//PATATO/spec_share/commands/')
    while True:
        
        cmds=os.listdir('//PATATO/spec_share/commands/')
        if cmds==cmds0:
            print('no change')
        else:
            for cmd in cmds:
                if cmd not in cmds0:
                    print(cmd)
                    if 'spectrum' in cmd:
                        spec_controller.take_spectrum()
            cmds0=cmds
        time.sleep(1)
        cmds0
    
if __name__=='__main__':
    main()