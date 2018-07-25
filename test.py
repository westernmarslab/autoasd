app=Application().connect(path=r"C:\Program Files\ASD\RS3\RS3.exe")
spec=app['RS³   18483 1']
x_left=spec.rectangle().left
y_top=spec.rectangle().top
width=300
height=50
print('swap!')
time.sleep(5)
screenshot=pyautogui.screenshot(region=(x_left, y_top, 700, 700))
location=pyautogui.locate('img/rs3specsave2.png', screenshot)
if location==None:
    print('Display button not found. Failed to open save menu')
    print('Here is where I am looking:')
    print(str(x_left)+' '+str(y_top))
else:
    print(location)