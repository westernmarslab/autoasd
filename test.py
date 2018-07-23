app=Application().connect(path=r"C:\Program Files\ASD\RS3\RS3.exe")
spec=app['RS³   18483 1']
x_left=spec.rectangle().left
y_top=spec.rectangle().top
width=300
height=50
time.sleep(2)
screenshot=pyautogui.screenshot(region=(x_left, y_top, width, height))
location=pyautogui.locate('img/rs3display.png', screenshot)
if location==None:
    print('Display button not found. Failed to open save menu')
    print('Here is where I am looking:')
    print(str(x_left)+' '+str(y_top))