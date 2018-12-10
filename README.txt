This version is ready for installation on MARSINSIGHT, the desktop computer we just got for the spectroscopy lab.

Here are instructions for installing AutoASD on a new computer.

1. On the new spec computer, create a new folder called SpecShare. Right click, properties ? Sharing ? Share. Type ‘Everyone’, Add, then change permission levels to Read/Write. Share! Make a note of name e.g. \\MARSINSIGHT\SpecShare. Inside, create directories
	log
	temp
	commands 
		from_spec
		From_control
2. On spec compy, open settings, network and internet, sharing options. Under current domain, select ‘turn on network discovery’ and save changes.
3. On spec compy, open a command terminal as an administrator, then run pip install autoasd. Open source code, and in __main__.py and auto_asd.py, look at all lines that are dependent on the value of the variable computer. Check if any need to be updated. If the RS3 version is the same and default install locations were used, everything should be fine.
4. On control compy, in a file explorer, navigate to Network, then click on e.g. MARSINSIGHT ? SpecShare. If you have trouble with this, open a command terminal and type e.g. net use * \\MARSINSIGHT\SpecShare. If asked for credentials and the new compy is on the WWU network, use your western ID while being sure to include the WWU domain. So you might have to click ‘Use other credentials’ and then type in e.g. WWU\hozak as your username before entering your WWU password.
3. From the control computer, in controller.py, change the computer variable to be something new and use it to set the server name to the right thing e.g. MARSINSIGHT
