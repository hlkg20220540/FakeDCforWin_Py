import screen_brightness_control as bri
import win32gui,win32con,win32api
import settings as sets
import setupused as need
import lastvar as mem
from PyQt5 import QtCore,QtWidgets,QtGui
import time,os
import threading
import importlib

try:
    test = sets.FirstUse
    test = sets.AutoStart
    test = sets.min_dc
except:
    fix = open('settings.py','w')
    fix.write('FirstUse = True')
    fix.write('\n')
    fix.write('AutoStart = False')
    fix.write('\n')
    fix.write('min_dc = 50')
    fix.close()
    del fix
    importlib.reload(sets)
try:
    test = need.SetupUsed
except:
    fix = open('setupused.py','w')
    fix.write('SetupUsed = False')
    fix.close()
    del fix
    importlib.reload(need)


if need.SetupUsed != True:
    if sets.FirstUse == True:
        print('欢迎！检测到首次使用，正在加载设置引导。。。')
    if sets.FirstUse == False:
        print('正在加载设置向导。。。')
    settings = open('settings.py','w')
    settings.write('FirstUse = False')
    settings.write('\n')
    chk = False;
    while chk != True:
        print('是否开机自启动？(y/n)')
        self_boot = input()
        if self_boot == 'y':
            os.system('mklink main.py "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\FakeDC.ink"')
            settings.write('AutoStart = True')
            settings.write('\n')
            chk = True
        if self_boot == 'n':
            os.system('del "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\FakeDC.ink"')
            settings.write('AutoStart = False')
            settings.write('\n')
            chk = True
    print('现在，请打开手机相机的专业模式，快门时间拉到最小。对照着调整屏幕亮度，直到保持在最小的DC维持亮度。')
    input('调整完成后，按下回车以继续。')
    min_dc = bri.get_brightness()
    min_dc = min_dc[0]
    settings.write('min_dc = '+str(min_dc))
    settings.close()
    setSetupNeed = open('setupused.py','w')
    setSetupNeed.write('SetupUsed = True')
    setSetupNeed.close()
importlib.reload(sets)
hwnd = win32gui.GetForegroundWindow()
win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
tips = ''
if sets.AutoStart == True:
    tips = tips + '，开机自启'
mask_bri = mem.MaskBri
DarkRate = mem.DarkRate
exit_dog = False
def dc_loop():
    while exit_dog != True:
        try:
            cur_bri = bri.get_brightness()
        except:
            time.sleep(0.5)
            continue
        cur_bri = cur_bri[0]
        if cur_bri < sets.min_dc:
            bri.set_brightness(sets.min_dc)
        time.sleep(0.5)
    return 0
dc_watchdog = threading.Thread(target=dc_loop)
def mask_up():
    global mask_bri,DarkRate
    mask_bri = mask_bri + 10
    if mask_bri >= sets.min_dc:
        mask_bri = sets.min_dc
        DarkRate = 0
    elif mask_bri <= 10:
        mask_bri = 10
        DarkRate = 1-mask_bri/sets.min_dc
        DarkRate = round(DarkRate,2)
    else:
        DarkRate = 1-mask_bri/sets.min_dc
        DarkRate = round(DarkRate,2)
    mask.setWindowOpacity(DarkRate)
def mask_down():
    global mask_bri,DarkRate
    mask_bri = mask_bri - 10
    if mask_bri >= sets.min_dc:
        mask_bri = sets.min_dc
        DarkRate = 0
    elif mask_bri <= 10:
        mask_bri = 10
        DarkRate = 1-mask_bri/sets.min_dc
        DarkRate = round(DarkRate,2)
    else:
        DarkRate = 1-mask_bri/sets.min_dc
        DarkRate = round(DarkRate,2)
    mask.setWindowOpacity(DarkRate)
def load_setup():
    global exit_dog,DarkRate
    setSetupNeed = open('setupused.py','w')
    setSetupNeed.write('SetupUsed = False')
    setSetupNeed.close()
    savevar = open('lastvar.py','w')
    savevar.write('DarkRate = '+str(DarkRate))
    savevar.write('\n')
    savevar.write('MaskBri = '+str(mask_bri))
    savevar.close()
    exit_dog = True
    dc_watchdog.join()
    tray_icon.hide()
    mask_div.quit()
    exit
def exit_all():
    global exit_dog,DarkRate
    savevar = open('lastvar.py','w')
    savevar.write('DarkRate = '+str(DarkRate))
    savevar.write('\n')
    savevar.write('MaskBri = '+str(mask_bri))
    savevar.close()
    exit_dog = True
    dc_watchdog.join()
    tray_icon.hide()
    mask_div.quit()
    exit
mask_div = QtWidgets.QApplication([])
mask = QtWidgets.QMainWindow()
mask.setStyleSheet('background-color:rgb(0,0,0);')
mask.setWindowOpacity(DarkRate)
screen = QtWidgets.QDesktopWidget().screenGeometry()
screen_width = screen.width()
screen_height = screen.height()
mask.setGeometry(0,0,screen_width,screen_height)
mask.setWindowFlag(QtCore.Qt.WindowTransparentForInput)
mask.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
mask.setWindowFlag(QtCore.Qt.FramelessWindowHint)
mask.setWindowFlag(QtCore.Qt.Tool)
tray_icon = QtWidgets.QSystemTrayIcon()
tray_icon.setIcon(QtGui.QIcon('FakeDC.png'))
tray_icon.setObjectName('FakeDC')
tray_icon.setToolTip('FakeDC正在运行'+tips)
menu = QtWidgets.QMenu()
mask_bri_up = QtWidgets.QAction('增加遮罩亮度')
mask_bri_up.triggered.connect(mask_up)
mask_bri_down = QtWidgets.QAction('减少遮罩亮度')
mask_bri_down.triggered.connect(mask_down)
exit_to_setup = QtWidgets.QAction('退出并在下次启动时加载设置引导')
exit_to_setup.triggered.connect(load_setup)
exit_app = QtWidgets.QAction('退出')
exit_app.triggered.connect(exit_all)
menu.addAction(mask_bri_up)
menu.addAction(mask_bri_down)
menu.addAction(exit_to_setup)
menu.addAction(exit_app)
tray_icon.setContextMenu(menu)
tray_icon.show()
mask.show()
dc_watchdog.start()
mask_div.exec()
