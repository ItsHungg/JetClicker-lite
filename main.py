from tkinter import ttk, messagebox
import tkinter as tk

from itertools import permutations, chain
from os import _exit
import pyautogui
import threading
import keyboard
import random
import mouse
import time
import json

__project__ = 'JetClicker Lite'
__version__ = '1.0'
__author__ = 'Hung'


class Utilities:
    @staticmethod
    def add_default_hotkeys(return_: bool = False):
        keyboard.add_hotkey('ctrl+shift+alt+r', Utilities.reset_all)

        if return_:
            return ['+'.join(x for x in i) for i in list(chain.from_iterable(
                permutations(hk.split('+'), r=len(hk.split('+'))) for hk in
                ['ctrl+alt+s', 'ctrl+shift+alt+r', 'ctrl+alt+b']))]

        if not STORAGE.Extension.ON:
            keyboard.add_hotkey('ctrl+alt+s', root.settings)

    @staticmethod
    def add_trigger_hotkey():
        keyboard.add_hotkey(STORAGE.Setting.trigger_hotkey,
                            lambda: root.stopClicking() if STORAGE.CLICKING else root.startClicking())

    @staticmethod
    def child_geometry(window, master, do=True):
        result = '+' + master.geometry().split('+', maxsplit=1)[1]
        if do:
            window.geometry(result)
        return result

    @staticmethod
    def reset_all(message: bool = True):
        if message and not messagebox.askyesno(f'Reset {__project__} {__version__}',
                                               f'Are you sure that you want to reset all data of {__project__}?',
                                               icon='warning'):
            return

        STORAGE.FIXED_POSITIONS = (0, 0)
        STORAGE.Setting.trigger_hotkey = 'ctrl+q'
        STORAGE.Setting.isFailsafe = True

        STORAGE.Extension.MouseRecorder.playbackSpeed = 1
        STORAGE.Extension.MouseRecorder.isClicksRecorded = True
        STORAGE.Extension.MouseRecorder.isMovementsRecorded = True
        STORAGE.Extension.MouseRecorder.isWheelrollsRecorded = True
        STORAGE.Extension.MouseRecorder.isInsertedEvents = False

        root.title(f'{__project__} {__version__}')
        keyboard.unregister_all_hotkeys()
        Utilities.add_default_hotkeys()
        Utilities.add_trigger_hotkey()

    @staticmethod
    def start(restart: bool = False):
        global root, backgroundThread
        if restart:
            for _widget in root.winfo_children():
                if isinstance(_widget, tk.Toplevel):
                    _widget.destroy()
                    STORAGE.Setting.ON = False
                    STORAGE.Extension.ON = False
                    STORAGE.Extension.MouseRecorder.ON = False
                else:
                    _widget.grid_forget()
            root.draw()
            keyboard.unregister_all_hotkeys()
            Utilities.add_trigger_hotkey()
            Utilities.add_default_hotkeys()
            root.geometry(STORAGE.Garbage.root_geometry.split('+')[0])
            return
        root = Application()
        Utilities.add_trigger_hotkey()
        Utilities.add_default_hotkeys()
        backgroundThread = threading.Thread(target=background_tasks)
        backgroundThread.start()
        STORAGE.RUNNING = True
        root.protocol('WM_DELETE_WINDOW', on_window_exit)
        root.mainloop()

    @staticmethod
    def set_window_icon(window: tk.Tk | tk.Toplevel, path: str = 'assets\\icons\\logo.ico'):
        window.iconbitmap(path)


with open(r'data\data.json', 'r') as read_data:
    try:
        DATA = json.load(read_data)
    except json.decoder.JSONDecodeError as error:
        messagebox.showerror('Decode Error',
                             'Couldn\'t read data.json file.\nPlease check the data file and try again.')
        quit()


class Storage:
    RUNNING = False
    BACKGROUND = False
    CLICKING = False
    FIXED_POSITIONS = tuple(map(int, DATA[0]['fixed-position']))

    class Garbage:
        isMasterFocus = False
        root_geometry: str = None

    class Setting:
        ON: bool | tk.Toplevel = False
        trigger_hotkey = DATA[1]['trigger-hotkey']

        isFailsafe = DATA[1]['is.failsafe']

    class Extension:
        ON: bool | tk.Toplevel = False
        version = '1.0.0'

        class MouseRecorder:
            ON: bool | tk.Toplevel = False
            version = '1.0'

            playbackSpeed = DATA[2]['extensions']['mouse-recorder']['playback-speed']
            isClicksRecorded = DATA[2]['extensions']['mouse-recorder']['is.record-clicks']
            isMovementsRecorded = DATA[2]['extensions']['mouse-recorder']['is.record-movements']
            isWheelrollsRecorded = DATA[2]['extensions']['mouse-recorder']['is.record-wheelrolls']
            isInsertedEvents = DATA[2]['extensions']['mouse-recorder']['is.insert-events']


STORAGE = Storage
pyautogui.FAILSAFE = STORAGE.Setting.isFailsafe
pyautogui.PAUSE = 0


def save_data(data: list | dict = None):
    if data is None:
        data = [
            {
                'category': 'storage',
                'fixed-position': STORAGE.FIXED_POSITIONS,
                'position-type': root.positionType.get()
            },
            {
                'category': 'settings',
                'trigger-hotkey': STORAGE.Setting.trigger_hotkey,
                'is.failsafe': STORAGE.Setting.isFailsafe
            },
            {
                'category': 'extensions',
                'version': STORAGE.Extension.version,
                'extensions': {
                    'mouse-recorder': {
                        'version': STORAGE.Extension.MouseRecorder.version,
                        'playback-speed': STORAGE.Extension.MouseRecorder.playbackSpeed,
                        'is.record-clicks': STORAGE.Extension.MouseRecorder.isClicksRecorded,
                        'is.record-movements': STORAGE.Extension.MouseRecorder.isMovementsRecorded,
                        'is.record-wheelrolls': STORAGE.Extension.MouseRecorder.isWheelrollsRecorded,
                        'is.insert-events': STORAGE.Extension.MouseRecorder.isInsertedEvents
                    },
                }
            }
        ]

    with open(r'data\data.json', 'w') as write_data:
        json.dump(data, write_data, indent=4)


# noinspection PyTypeChecker,PyMethodMayBeStatic
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.spinTimeLabel = None
        self._click_optionFrame = None
        self._click_repeatFrame = None
        self._cursor_positionFrame = None
        self._intervalFrame = None
        self.allMenuFrame = None
        self.click_optionFrame = None
        self.click_repeatFrame = None
        self.clickTypeOptionCombobox = None
        self.cursor_positionFrame = None
        self.customPositionRadiobutton = None
        self.extensionsButton = None
        self.intervalFrame = None
        self.intervalHourEntry = None
        self.intervalMillisecondEntry = None
        self.intervalMinuteEntry = None
        self.intervalSecondEntry = None
        self.intervalWidgets = None
        self.limitedRepeatRadiobutton = None
        self.limitedRepeatSpinbox = None
        self.mainFrame = None
        self.menuButton = None
        self.menuColor = None
        self.menuFrame = None
        self.menuImage = None
        self.mouseButtonOptionCombobox = None
        self.mouseImage = None
        self.mousePositionRadiobutton = None
        self.positionType = tk.StringVar(value=DATA[0]['position-type'])
        self.positionVar = tk.StringVar(value='mouse')
        self.randomPositionVar = tk.IntVar(value=0)
        self.repeatVar = tk.StringVar(value='unlimited')
        self.runFrame = None
        self.settingButton = None
        self.settingImage = None
        self.spinTime = 1
        self.startClickButton = None
        self.stopClickButton = None
        self.unlimitedRepeatRadiobutton = None
        self.draw()

    def draw(self):
        self.title(f'{__project__} {__version__}')
        self.resizable(False, False)
        self.attributes('-topmost', True)
        Utilities.set_window_icon(self)

        self.mainFrame = tk.Frame(self)
        self.mainFrame.grid(row=5, column=3, padx=15, pady=15)

        self.menuImage = tk.PhotoImage(file=r'assets\textures\menu.png').subsample(20, 20)
        self.menuButton = tk.Button(self, image=self.menuImage, border=0, background=self.mainFrame.cget('background'),
                                    cursor='hand2',
                                    command=self.menuActions)
        self.menuButton.grid(row=0, column=0, columnspan=100, rowspan=100, sticky='nw', padx=7, pady=3)

        self.menuFrame = tk.Frame(background='gray80', width=100)
        self.menuColor = self.menuFrame.cget('background')

        self.allMenuFrame = tk.Frame(self.menuFrame)
        self.allMenuFrame.grid(row=3, column=3, padx=5, pady=5)

        tk.Button(self.allMenuFrame, image=self.menuImage, border=0, background=self.menuColor,
                  activebackground=self.menuColor,
                  cursor='hand2',
                  command=self.menuActions).grid(row=1, column=3, sticky='ew')

        tk.Label(self.allMenuFrame, text='', background=self.menuColor, font=('Calibri', 1)).grid(row=3, column=3,
                                                                                                  sticky='ew')
        tk.Frame(self.allMenuFrame, background='black', height=2).grid(row=4, column=3, sticky='ew')
        tk.Frame(self.allMenuFrame, background='black', height=2).grid(row=6, column=3, sticky='ew')

        self.mouseImage = tk.PhotoImage(file=r'assets\textures\mouse.png').subsample(22, 22)
        self.extensionsButton = tk.Button(self.allMenuFrame, background=self.menuColor, activebackground=self.menuColor,
                                          border=0,
                                          image=self.mouseImage, cursor='hand2', command=self.extensions)
        self.extensionsButton.grid(row=5, column=3, ipady=7, sticky='nsew')

        self.settingImage = tk.PhotoImage(file=r'assets\textures\setting.png').subsample(22, 22)
        self.settingButton = tk.Button(self.allMenuFrame, background=self.menuColor, activebackground=self.menuColor,
                                       border=0,
                                       image=self.settingImage, cursor='hand2', command=self.settings)
        self.settingButton.grid(row=7, column=3, ipady=7, sticky='nsew')

        self.intervalFrame = ttk.LabelFrame(self.mainFrame, text='Click interval', labelanchor='n')
        self.intervalFrame.grid(row=3, column=3, ipadx=15, ipady=5, sticky='new', columnspan=3)
        self.intervalFrame.grid_columnconfigure(3, weight=1)

        self._intervalFrame = tk.Frame(self.intervalFrame)
        self._intervalFrame.grid(row=3, column=3, pady=(5, 0))
        self._intervalFrame.grid_columnconfigure(tuple(range(3, 11)), weight=1)

        self.intervalHourEntry = ttk.Entry(self._intervalFrame, width=3)
        self.intervalHourEntry.grid(row=3, column=3)
        self.intervalHourEntry.insert('end', '00')
        ttk.Label(self._intervalFrame, text='hours, ').grid(row=3, column=4, sticky='w', padx=(0, 6))

        self.intervalMinuteEntry = ttk.Entry(self._intervalFrame, width=3)
        self.intervalMinuteEntry.grid(row=3, column=5)
        self.intervalMinuteEntry.insert('end', '00')
        ttk.Label(self._intervalFrame, text='minutes, ').grid(row=3, column=6, sticky='w', padx=(0, 6))

        self.intervalSecondEntry = ttk.Entry(self._intervalFrame, width=3)
        self.intervalSecondEntry.grid(row=3, column=7)
        self.intervalSecondEntry.insert('end', '00')
        ttk.Label(self._intervalFrame, text='seconds, ').grid(row=3, column=8, sticky='w', padx=(0, 6))

        self.intervalMillisecondEntry = ttk.Entry(self._intervalFrame, width=3)
        self.intervalMillisecondEntry.grid(row=3, column=9)
        self.intervalMillisecondEntry.insert('end', '100')
        ttk.Label(self._intervalFrame, text='milliseconds').grid(row=3, column=10, sticky='w', padx=(0, 6))

        for i in [self.intervalHourEntry, self.intervalMinuteEntry, self.intervalSecondEntry,
                  self.intervalMillisecondEntry]:
            i.bind('<FocusOut>', lambda event=i: self.bindChosenAll(event))

        self.click_optionFrame = ttk.LabelFrame(self.mainFrame, text='Click options', labelanchor='nw')
        self.click_optionFrame.grid(row=5, column=3, ipadx=15, ipady=5, pady=(5, 0), sticky='nw', padx=(0, 5))
        self.click_optionFrame.grid_columnconfigure(3, weight=1)

        self._click_optionFrame = tk.Frame(self.click_optionFrame)
        self._click_optionFrame.grid(row=3, column=3, pady=(5, 0))
        self._click_optionFrame.grid_columnconfigure((3, 5), weight=1)

        mousebuttonLabel = ttk.Label(self._click_optionFrame,
                                     text='Mouse button:',
                                     width=12)
        mousebuttonLabel.grid(row=3, column=3, padx=(0, 5), pady=(0, 5),
                              sticky='w')
        self.mouseButtonOptionCombobox = ttk.Combobox(self._click_optionFrame, width=7,
                                                      values=['Left', 'Right', 'Middle'], state='readonly')
        self.mouseButtonOptionCombobox.grid(row=3, column=4, pady=(0, 5))
        self.mouseButtonOptionCombobox.set('Left')

        ttk.Label(self._click_optionFrame, text='Click type:').grid(row=5, column=3, padx=(0, 5), sticky='w')
        self.clickTypeOptionCombobox = ttk.Combobox(self._click_optionFrame, width=7,
                                                    values=['Single', 'Double', 'Triple'], state='readonly')
        self.clickTypeOptionCombobox.grid(row=5, column=4)
        self.clickTypeOptionCombobox.set('Single')

        self.click_repeatFrame = ttk.LabelFrame(self.mainFrame, text='Click repeat', labelanchor='nw')
        self.click_repeatFrame.grid(row=5, column=5, ipadx=15, ipady=5, pady=5, sticky='ne', padx=(5, 0))
        self.click_repeatFrame.grid_columnconfigure(3, weight=1)

        self._click_repeatFrame = tk.Frame(self.click_repeatFrame)
        self._click_repeatFrame.grid(row=3, column=3, pady=(5, 0))
        self._click_repeatFrame.grid_columnconfigure((3, 5), weight=1)

        self.limitedRepeatRadiobutton = ttk.Radiobutton(self._click_repeatFrame, text='Repeat', value='limited',
                                                        variable=self.repeatVar,
                                                        command=lambda: self.limitedRepeatSpinbox.focus())
        self.limitedRepeatRadiobutton.grid(row=3, column=3, padx=(0, 5), pady=(0, 5), sticky='w')

        self.limitedRepeatSpinbox = ttk.Spinbox(self._click_repeatFrame, from_=1, to=99999, width=5, wrap=True,
                                                validate='key', validatecommand=(
                self.register(lambda item: True if not len(item) or (item.isdigit() and int(item)) else False), '%P'))
        self.limitedRepeatSpinbox.grid(row=3, column=4, padx=5, pady=(0, 5), sticky='w')
        self.limitedRepeatSpinbox.set(self.spinTime)
        self.spinTimeLabel = ttk.Label(self._click_repeatFrame, text=f'times', width=5)
        self.spinTimeLabel.grid(row=3, column=5, pady=(0, 5), sticky='w')

        self.unlimitedRepeatRadiobutton = ttk.Radiobutton(self._click_repeatFrame, text='Until stopped',
                                                          value='unlimited', variable=self.repeatVar)
        self.unlimitedRepeatRadiobutton.grid(row=5, column=3, padx=(0, 5), sticky='w', columnspan=3)

        self.cursor_positionFrame = ttk.LabelFrame(self.mainFrame, text='Cursor position', labelanchor='n')
        self.cursor_positionFrame.grid(row=7, column=3, ipadx=15, ipady=5, sticky='new', columnspan=3)
        self.cursor_positionFrame.grid_columnconfigure(3, weight=1)

        self._cursor_positionFrame = tk.Frame(self.cursor_positionFrame)
        self._cursor_positionFrame.grid(row=3, column=3, pady=(5, 0))
        self._cursor_positionFrame.grid_columnconfigure(tuple(range(3, 11)), weight=1)

        self.mousePositionRadiobutton = ttk.Radiobutton(self._cursor_positionFrame, text='Current (0, 0)',
                                                        value='mouse', variable=self.positionVar)
        self.mousePositionRadiobutton.grid(row=3, column=3, padx=(0, 7), pady=(0, 5), sticky='w')

        self.customPositionRadiobutton = ttk.Radiobutton(self._cursor_positionFrame,
                                                         text='Custom ({0}, {1})'.format(*STORAGE.FIXED_POSITIONS),
                                                         value='custom',
                                                         variable=self.positionVar, command=self.customPositionDialog)
        self.customPositionRadiobutton.grid(row=3, column=5, padx=(7, 0), sticky='e')

        self.runFrame = tk.Frame(self.mainFrame)
        self.runFrame.grid(row=9, column=3, columnspan=3, sticky='nsew', ipadx=15, ipady=5, pady=(15, 0))
        self.runFrame.grid_columnconfigure((3, 5), weight=1)
        self.runFrame.grid_rowconfigure((3, 5), weight=1)

        self.startClickButton = ttk.Button(self.runFrame, text='Start', command=self.startClicking)
        self.startClickButton.grid(row=3, column=3, sticky='nsew')

        self.stopClickButton = ttk.Button(self.runFrame, text='Stop', state='disabled', command=self.stopClicking)
        self.stopClickButton.grid(row=3, column=5, sticky='nsew')

    def startClicking(self):
        try:
            hour, minute, second, millisecond = map(int, [self.intervalHourEntry.get(), self.intervalMinuteEntry.get(),
                                                          self.intervalSecondEntry.get(),
                                                          self.intervalMillisecondEntry.get()])
        except ValueError:
            messagebox.showwarning('Invalid intervals', 'The interval you put in is invalid. Please check again.')
            return

        sleepTime = hour * 60 * 60 + minute * 60 + second + millisecond / 1000

        clickType = self.clickTypeOptionCombobox.get().lower().strip()
        mouseButton = self.mouseButtonOptionCombobox.get().lower().strip()

        self.startClickButton.config(state='disabled')
        self.stopClickButton.config(state='normal')
        self.extensionsButton.config(state='disabled', cursor='')
        self.settingButton.config(state='disabled', cursor='')
        self.title(f'Clicking - {__project__} {__version__}')

        for widget in [self.intervalHourEntry, self.intervalMinuteEntry, self.intervalSecondEntry,
                       self.intervalMillisecondEntry, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton]:
            widget.config(state='disabled')
        STORAGE.CLICKING = True

        def click():
            if self.positionVar.get() == 'custom' and not self.randomPositionVar.get():
                pyautogui.moveTo(*map(int, STORAGE.FIXED_POSITIONS))
            if self.positionVar.get() == 'custom' and self.positionType.get().strip() == 'manual' and self.randomPositionVar.get():
                pos = [random.randint(0, c) for c in pyautogui.size()]
                pyautogui.moveTo(*pos)

            pyautogui.click(button=mouseButton,
                            clicks=3 if clickType == 'triple' else 2 if clickType == 'double' else 1)

        def runClicks():
            nonlocal sleepTime

            if not self.limitedRepeatSpinbox.get().strip().isdigit() and self.repeatVar.get() == 'limited':
                self.stopClicking()
                return
            else:
                repeatTime = -1 if self.repeatVar.get() == 'unlimited' else int(self.limitedRepeatSpinbox.get())
            while 1:
                if not repeatTime:
                    self.stopClicking()
                    break
                if not STORAGE.CLICKING:
                    self.stopClicking()
                    break
                try:
                    if pyautogui.position() in pyautogui.FAILSAFE_POINTS:
                        raise pyautogui.FailSafeException
                    click()

                    time.sleep(sleepTime)
                except pyautogui.FailSafeException:
                    keyboard.unregister_all_hotkeys()
                    Utilities.add_default_hotkeys()
                    self.stopClickButton.config(state='disabled')
                    messagebox.showwarning('Fail-safe Triggered',
                                           f'You have triggered {__project__} fail-safe by moving the mouse to the corner of the screen.\n\n(You can disable it in the settings, but it\'s NOT RECOMMENDED)')
                    self.stopClicking()
                    Utilities.add_trigger_hotkey()
                    break
                repeatTime -= 1

        threading.Thread(target=runClicks).start()

    def stopClicking(self):
        self.startClickButton.config(state='normal')
        self.stopClickButton.config(state='disabled')
        self.extensionsButton.config(state='normal', cursor='hand2')
        self.settingButton.config(state='normal', cursor='hand2')
        self.title(f'Stopped - {__project__} {__version__}')
        STORAGE.CLICKING = False

        for widget in [self.intervalHourEntry, self.intervalMinuteEntry, self.intervalSecondEntry,
                       self.intervalMillisecondEntry, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton]:
            widget.config(state='readonly' if widget in [self.clickTypeOptionCombobox,
                                                         self.mouseButtonOptionCombobox] else 'normal')

    def menuActions(self):
        self.menuFrame.grid(row=0, column=0, sticky='nsw', columnspan=100, rowspan=100)
        if self.menuFrame.winfo_viewable():
            self.menuFrame.grid_forget()

    def settings(self):
        if isinstance(STORAGE.Setting.ON, tk.Toplevel):
            STORAGE.Setting.ON.lift()
            return

        for widget in [self.intervalHourEntry, self.intervalMinuteEntry, self.intervalSecondEntry,
                       self.intervalMillisecondEntry, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton, self.startClickButton,
                       self.extensionsButton]:
            widget.config(state='disabled', cursor='')
        keyboard.unregister_all_hotkeys()
        Utilities.add_default_hotkeys()

        settingWindow = STORAGE.Setting.ON = tk.Toplevel(self)
        settingWindow.title('Settings')
        settingWindow.resizable(False, False)
        settingWindow.attributes('-topmost', True)
        Utilities.set_window_icon(settingWindow)

        settingWindow.geometry(f'+{self.winfo_x() + self.winfo_width() + 10}+{self.winfo_y()}')
        self.bind('<Configure>', lambda _: settingWindow.geometry(
            f'+{self.winfo_x() + self.winfo_width() + 10}+{self.winfo_y()}') if settingWindow.winfo_exists() else None)

        allSettingsFrame = tk.Frame(settingWindow)
        allSettingsFrame.grid(row=3, column=3, padx=10, pady=10)

        setting2_hotkey_frame = ttk.LabelFrame(allSettingsFrame, text='Hotkeys')
        setting2_hotkey_frame.grid(row=3, column=3, sticky='ew', pady=(0, 5))

        _setting1_hotkey_frame = tk.Frame(setting2_hotkey_frame)
        _setting1_hotkey_frame.grid(row=3, column=3, padx=15, pady=5)

        hotkeyDisplayEntry = tk.Entry(_setting1_hotkey_frame, width=11)
        hotkeyDisplayEntry.insert(0, '+'.join(
            [key.capitalize() for key in STORAGE.Setting.trigger_hotkey.lower().split('+')]))
        hotkeyDisplayEntry.grid(row=3, column=3, sticky='ns', padx=(0, 5))

        def check_key_validation(_):
            invalidKeysLabel.config(text='')
            saveButton.config(state='normal')
            for key in hotkeyDisplayEntry.get().lower().split('+'):
                if not pyautogui.isValidKey(key):
                    saveButton.config(state='disabled')
                    invalidKeysLabel.config(text='Invalid!')
            if hotkeyDisplayEntry.get().replace(' ', '').strip().lower() in Utilities.add_default_hotkeys(True):
                invalidKeysLabel.config(text='Corrupted!')
                saveButton.config(state='disabled')

        hotkeyDisplayEntry.bind('<KeyRelease>', check_key_validation)

        invalidKeysLabel = tk.Label(_setting1_hotkey_frame, text='', foreground='red', width=10, anchor='w')
        invalidKeysLabel.grid(row=3, column=7, padx=5)

        setting3_pickposition_frame = ttk.LabelFrame(allSettingsFrame, text='Pick-position dialog')
        setting3_pickposition_frame.grid(row=5, column=3, sticky='ew', pady=(0, 5))
        setting3_pickposition_frame.grid_columnconfigure(3, weight=1)

        _setting2_pickposition_frame = tk.Frame(setting3_pickposition_frame)
        _setting2_pickposition_frame.grid(row=3, column=3, padx=15, pady=5, sticky='ew')
        _setting2_pickposition_frame.grid_columnconfigure(3, weight=1)

        transparencyFrame = tk.Frame(_setting2_pickposition_frame)
        transparencyFrame.grid(row=3, column=3)
        transparencyFrame.grid_columnconfigure((3, 5, 7), weight=1)

        askCustomDialogOpenButton = ttk.Button(_setting2_pickposition_frame, text='Open',
                                               command=lambda: self.customPositionDialog(True))
        askCustomDialogOpenButton.grid(
            row=5, column=3, sticky='ew', pady=5)

        setting10_miscellaneous_frame = ttk.LabelFrame(allSettingsFrame, text='Miscellaneous')
        setting10_miscellaneous_frame.grid(row=21, column=3, sticky='ew')

        _setting10_miscellaneous_frame = tk.Frame(setting10_miscellaneous_frame)
        _setting10_miscellaneous_frame.grid(row=3, column=3)

        failsafeVar = tk.IntVar()
        checkbox3_failsafe = tk.Checkbutton(_setting10_miscellaneous_frame, text='Fail-safe system',
                                            variable=failsafeVar)
        checkbox3_failsafe.select() if STORAGE.Setting.isFailsafe else None
        checkbox3_failsafe.grid(row=7, column=3, sticky='w')

        def save():
            STORAGE.Setting.trigger_hotkey = hotkeyDisplayEntry.get().lower().strip()
            STORAGE.Setting.isFailsafe = bool(failsafeVar.get())

            self.attributes('-topmost', True)
            pyautogui.FAILSAFE = STORAGE.Setting.isFailsafe

        def closing():
            STORAGE.Setting.ON = False
            settingWindow.destroy()

            for _widget in [self.intervalHourEntry, self.intervalMinuteEntry, self.intervalSecondEntry,
                            self.intervalMillisecondEntry, self.mouseButtonOptionCombobox,
                            self.clickTypeOptionCombobox,
                            self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                            self.mousePositionRadiobutton, self.customPositionRadiobutton, self.startClickButton,
                            self.extensionsButton]:
                if _widget is self.extensionsButton:
                    _widget.config(state='normal', cursor='hand2')
                else:
                    _widget.config(state='readonly' if _widget in [self.clickTypeOptionCombobox,
                                                                   self.mouseButtonOptionCombobox] else 'normal')
            keyboard.unregister_all_hotkeys()
            Utilities.add_default_hotkeys()
            Utilities.add_trigger_hotkey()

        def on_exit(saving: bool = True, on_quit: bool = False):
            if not keyboard.is_pressed('ctrl') and on_quit:
                if not messagebox.askyesno('Closing Settings',
                                           'Are you sure that you want to close settings? Everything won\'t be saved.',
                                           default='no', parent=settingWindow, icon='warning'):
                    return

            if not on_quit:
                for _widget in [hotkeyDisplayEntry, askCustomDialogOpenButton, checkbox3_failsafe, saveButton]:
                    _widget.config(state='disabled')

            if saving:
                save()

            closing()

        saveSettingsFrame = tk.Frame(settingWindow)
        saveSettingsFrame.grid(row=100, column=3, sticky='ew', pady=(0, 10))
        saveSettingsFrame.grid_columnconfigure((3, 5), weight=1)

        saveButtonStyle = ttk.Style()
        saveButtonStyle.configure('save.TButton', foreground='darkgreen', font=('', 9, 'bold'))

        saveButton = ttk.Button(saveSettingsFrame, text='Save & Quit', style='save.TButton', command=on_exit)
        saveButton.grid(row=3, column=3, ipadx=15, sticky='nse', padx=3)

        settingWindow.protocol('WM_DELETE_WINDOW', lambda: on_exit(False, True))

    def extensions(self):
        STORAGE.Extension.ON = extensionsWindow = tk.Toplevel(self)
        extensionsWindow.title(f'Extensions List ({STORAGE.Extension.version})')
        Utilities.child_geometry(extensionsWindow, self)
        extensionsWindow.resizable(False, False)
        extensionsWindow.attributes('-topmost', True)
        Utilities.set_window_icon(extensionsWindow)
        self.withdraw()

        keyboard.unregister_all_hotkeys()
        Utilities.add_default_hotkeys()

        allExtensionsFrame = tk.Frame(extensionsWindow)
        allExtensionsFrame.grid(row=3, column=3, sticky='nsew')

        tk.Label(allExtensionsFrame, text='Extensions', font=('Calibri', 25, 'bold')).grid(row=0, column=3)

        extensionsFrame = tk.Frame(allExtensionsFrame)
        extensionsFrame.grid(row=5, column=3, padx=15, pady=15)
        extensionsFrame.grid_columnconfigure((3, 5, 7), weight=1)
        tk.Frame(extensionsFrame, background='black', height=3).grid(row=0, column=0, columnspan=100, sticky='ew')
        tk.Frame(extensionsFrame, background='black', width=3).grid(row=0, column=0, rowspan=100, sticky='ns')
        tk.Frame(extensionsFrame, background='black', height=3).grid(row=99, column=0, columnspan=100, sticky='ew')
        tk.Frame(extensionsFrame, background='black', width=3).grid(row=0, column=99, rowspan=100, sticky='ns')

        insideExtensionFrame = tk.Frame(extensionsFrame)
        insideExtensionFrame.grid(row=3, column=3, padx=5, pady=5)

        extension1_mouseRecorderButton = ttk.Button(insideExtensionFrame,
                                                    text=f'MouseRecorder',
                                                    cursor='hand2', command=self.mouseRecorder)
        extension1_mouseRecorderButton.grid(row=3, column=3)
        tk.Label(insideExtensionFrame,
                 text=f'Version: {STORAGE.Extension.MouseRecorder.version}\nAuthor: {__author__}\nStatus: Available',
                 anchor='center').grid(row=5, column=3)

        tk.Frame(insideExtensionFrame, background='black', width=3).grid(row=3, column=4, sticky='ns', rowspan=100,
                                                                         padx=5)

        extension2_cpsCounterButton = ttk.Button(insideExtensionFrame,
                                                 text=f'CPS Calculator',
                                                 state='disabled')
        extension2_cpsCounterButton.grid(row=3, column=5)
        tk.Label(insideExtensionFrame, text=f'Version: N/A\nAuthor: {__author__}\nStatus: Unavailable',
                 anchor='center').grid(row=5, column=5)

        def closeExtensions():
            self.deiconify()
            extensionsWindow.destroy()
            STORAGE.Extension.ON = False

            Utilities.add_default_hotkeys()
            Utilities.add_trigger_hotkey()

        extensionsWindow.protocol('WM_DELETE_WINDOW', closeExtensions)

    def mouseRecorder(self):
        STORAGE.Extension.MouseRecorder.ON = recorderWindow = tk.Toplevel(STORAGE.Extension.ON)
        recorderWindow.title(f'MouseRecorder {STORAGE.Extension.MouseRecorder.version}')
        Utilities.child_geometry(recorderWindow, STORAGE.Extension.ON)
        recorderWindow.resizable(False, False)
        recorderWindow.attributes('-topmost', True)
        Utilities.set_window_icon(recorderWindow)
        STORAGE.Extension.ON.withdraw()

        keyboard.unregister_all_hotkeys()
        Utilities.add_default_hotkeys()

        allRecorderFrame = tk.Frame(recorderWindow)
        allRecorderFrame.grid(row=3, column=3, sticky='nsew')

        playbackRecordButton = ttk.Button(allRecorderFrame, text='Play', width=9, state='disabled',
                                          command=lambda: threading.Thread(target=playRecord).start())
        playbackRecordButton.grid(row=3, column=3)

        startRecordButton = ttk.Button(allRecorderFrame, text='Record', width=9,
                                       command=lambda: stopRecord() if hook else startRecord())
        startRecordButton.grid(row=3, column=5)

        def recorderSetting():
            recorderWindow.withdraw()

            def saveRecordSettings(widget=None):
                STORAGE.Extension.MouseRecorder.playbackSpeed = playbackSpeedVar.get() / 2
                if isinstance(widget, tk.Checkbutton) and all(
                        not i for i in [recordClicksVar.get(), recordMovementsVar.get(), recordWheelrollsVar.get()]):
                    widget.select()
                STORAGE.Extension.MouseRecorder.isClicksRecorded = bool(recordClicksVar.get())
                STORAGE.Extension.MouseRecorder.isMovementsRecorded = bool(recordMovementsVar.get())
                STORAGE.Extension.MouseRecorder.isWheelrollsRecorded = bool(recordWheelrollsVar.get())
                STORAGE.Extension.MouseRecorder.isInsertedEvents = bool(insertedEventsVar.get())

            recorderSettingWindow = tk.Toplevel(recorderWindow)
            recorderSettingWindow.title('Recorder Settings')
            Utilities.child_geometry(recorderSettingWindow, recorderWindow)
            recorderSettingWindow.resizable(False, False)
            Utilities.set_window_icon(recorderSettingWindow)

            allRecorderSettingFrame = tk.Frame(recorderSettingWindow)
            allRecorderSettingFrame.grid(row=3, column=3, padx=10)

            playbackSettingFrame = ttk.LabelFrame(allRecorderSettingFrame, text='Playback speed')
            playbackSettingFrame.grid(row=3, column=3, sticky='ew')
            playbackSpeedVar = tk.IntVar(value=STORAGE.Extension.MouseRecorder.playbackSpeed * 2)
            playbackSpeedSlider = ttk.Scale(playbackSettingFrame, from_=1, to=6, orient='horizontal',
                                            variable=playbackSpeedVar,
                                            command=lambda _: playbackSpeedDisplayLabel.config(
                                                text=f'x{playbackSpeedVar.get() / 2}'))
            playbackSpeedSlider.grid(row=3, column=3)
            playbackSpeedDisplayLabel = tk.Label(playbackSettingFrame, text=f'x{playbackSpeedVar.get() / 2}')
            playbackSpeedDisplayLabel.grid(row=3, column=5, padx=3)

            recordTargetFrame = ttk.LabelFrame(allRecorderSettingFrame, text='Record targets')
            recordTargetFrame.grid(row=5, column=3, sticky='ew', pady=(5, 0))

            recordClicksVar = tk.IntVar()
            recordClicksCheckbutton = tk.Checkbutton(recordTargetFrame, text='Mouse clicks',
                                                     variable=recordClicksVar,
                                                     command=lambda: saveRecordSettings(recordClicksCheckbutton))
            self.after(10,
                       lambda: recordClicksCheckbutton.select() if STORAGE.Extension.MouseRecorder.isClicksRecorded else None)
            recordClicksCheckbutton.grid(row=3, column=3, sticky='w')

            recordMovementsVar = tk.IntVar()
            recordMovementsCheckbutton = tk.Checkbutton(recordTargetFrame, text='Movements',
                                                        variable=recordMovementsVar,
                                                        command=lambda: saveRecordSettings(recordMovementsCheckbutton))
            self.after(10,
                       lambda: recordMovementsCheckbutton.select() if STORAGE.Extension.MouseRecorder.isMovementsRecorded else None)
            recordMovementsCheckbutton.grid(row=5, column=3, sticky='w')

            recordWheelrollsVar = tk.IntVar()
            recordWheelrollsCheckbutton = tk.Checkbutton(recordTargetFrame, text='Scroll wheel',
                                                         variable=recordWheelrollsVar,
                                                         command=lambda: saveRecordSettings(
                                                             recordWheelrollsCheckbutton))
            self.after(10,
                       lambda: recordWheelrollsCheckbutton.select() if STORAGE.Extension.MouseRecorder.isWheelrollsRecorded else None)
            recordWheelrollsCheckbutton.grid(row=7, column=3, sticky='w')

            miscellaneousRecordSettingFrame = ttk.LabelFrame(allRecorderSettingFrame, text='Miscellaneous')
            miscellaneousRecordSettingFrame.grid(row=7, column=3, sticky='ew', pady=(5, 0))

            insertedEventsVar = tk.IntVar()
            insertedEventsCheckbutton = tk.Checkbutton(miscellaneousRecordSettingFrame, text='Inserted events',
                                                       variable=insertedEventsVar,
                                                       command=lambda: saveRecordSettings(insertedEventsCheckbutton))

            self.after(10,
                       lambda: insertedEventsCheckbutton.select() if STORAGE.Extension.MouseRecorder.isInsertedEvents else None)
            insertedEventsCheckbutton.grid(row=5, column=3, sticky='w')

            clearEventsButton = ttk.Button(miscellaneousRecordSettingFrame,
                                           text=f'Clear{"" if events else "ed"} events', width=13,
                                           state='normal' if events else 'disabled', command=lambda: [events.clear(),
                                                                                                      clearEventsButton.config(
                                                                                                          text='Cleared events',
                                                                                                          state='disabled')])
            clearEventsButton.grid(row=9, column=3, sticky='w', padx=5, pady=(0, 5))
            ttk.Button(recorderSettingWindow, text='Auto-saved', state='disabled').grid(row=5, column=3, pady=7)

            def closeRecorderSetting():
                recorderSettingWindow.destroy()
                recorderWindow.deiconify()
                saveRecordSettings()
                if not events:
                    playbackRecordButton.config(state='disabled')

            recorderSettingWindow.protocol('WM_DELETE_WINDOW', closeRecorderSetting)

        recorderSettingButton = tk.Button(allRecorderFrame, background=allRecorderFrame.cget('background'),
                                          activebackground=allRecorderFrame.cget('background'),
                                          border=0,
                                          image=self.settingImage, cursor='hand2', command=recorderSetting)
        recorderSettingButton.grid(row=3, column=0, padx=3)

        hook: mouse.hook | bool = False
        hookThread: threading.Thread | bool = False
        events = []

        def startRecord():
            nonlocal hook, hookThread
            startRecordButton.config(text='Stop')
            playbackRecordButton.config(state='disabled')
            recorderSettingButton.config(state='disabled')
            if not STORAGE.Extension.MouseRecorder.isInsertedEvents:
                events.clear()

            def backgroundRecord():
                nonlocal hook
                hook = mouse.hook(events.append)

            hookThread = threading.Thread(backgroundRecord())
            hookThread.start()

        def stopRecord():
            nonlocal hook
            mouse.unhook(hook)
            hook = False

            hookThread.join(0)

            startRecordButton.config(text='Start')
            playbackRecordButton.config(state='normal')
            recorderSettingButton.config(state='normal')

        def playRecord():
            startRecordButton.config(state='disabled')
            playbackRecordButton.config(text='Playing', state='disabled')
            recorderSettingButton.config(state='disabled')
            mouse.play(events, STORAGE.Extension.MouseRecorder.playbackSpeed,
                       STORAGE.Extension.MouseRecorder.isClicksRecorded,
                       STORAGE.Extension.MouseRecorder.isMovementsRecorded,
                       STORAGE.Extension.MouseRecorder.isWheelrollsRecorded)
            startRecordButton.config(state='normal')
            playbackRecordButton.config(text='Play', state='normal')
            recorderSettingButton.config(state='normal')

        def closeRecorder():
            if hook and hookThread:
                mouse.unhook(hook)
                hookThread.join(0)
            if keyboard.is_pressed('shift'):
                self.deiconify()
                STORAGE.Extension.ON.destroy()
                keyboard.unregister_all_hotkeys()
                Utilities.add_default_hotkeys()
                Utilities.add_trigger_hotkey()
            else:
                STORAGE.Extension.ON.deiconify()

            STORAGE.Extension.MouseRecorder.ON = False
            recorderWindow.destroy()

        recorderWindow.protocol('WM_DELETE_WINDOW', closeRecorder)

    def customPositionDialog(self, fromSetting=False):
        if keyboard.is_pressed('ctrl') and not fromSetting:
            return

        self.focus()
        for widget in [self.intervalHourEntry, self.intervalMinuteEntry, self.intervalSecondEntry,
                       self.intervalMillisecondEntry, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton]:
            widget.config(state='disabled')

        keyboard.unregister_all_hotkeys()

        askPositionDialog = tk.Toplevel(self)
        askPositionDialog.title('')
        Utilities.child_geometry(askPositionDialog, self)
        askPositionDialog.resizable(False, False)
        askPositionDialog.attributes('-topmost', True)
        Utilities.set_window_icon(askPositionDialog)

        askPositionDialog.grab_set()
        askPositionDialog.focus()

        positions = STORAGE.FIXED_POSITIONS

        alldialogFrame = tk.Frame(askPositionDialog)
        alldialogFrame.grid(row=3, column=3, padx=15, pady=(15, 0), ipadx=5, ipady=5)
        alldialogFrame.grid_columnconfigure(3, weight=1)

        mainCustomPositionFrame = ttk.LabelFrame(alldialogFrame, text='Manual position', labelanchor='n')
        mainCustomPositionFrame.grid(row=3, column=3, ipadx=15, ipady=5, sticky='ew')
        mainCustomPositionFrame.grid_columnconfigure(3, weight=1)

        choosePositionFrame = tk.Frame(mainCustomPositionFrame)
        choosePositionFrame.grid(row=3, column=3, pady=(5, 0))

        choosePositionFrame_radiobutton = ttk.Radiobutton(choosePositionFrame, value='manual',
                                                          variable=self.positionType,
                                                          command=lambda: bindradio_all())
        choosePositionFrame_radiobutton.grid(row=3, column=1)

        ttk.Label(choosePositionFrame, text='x=').grid(row=3, column=2, sticky='e')
        xCustomPositionEntry = ttk.Entry(choosePositionFrame, width=4)
        xCustomPositionEntry.grid(row=3, column=3, sticky='w')

        ttk.Label(choosePositionFrame, text=',  y=', anchor='e').grid(row=3, column=4, sticky='e')
        yCustomPositionEntry = ttk.Entry(choosePositionFrame, width=4)
        yCustomPositionEntry.grid(row=3, column=5, sticky='w')
        ttk.Label(choosePositionFrame, text=',  y=', anchor='e').grid(row=3, column=4, sticky='e')

        randomPositionCheckbutton = tk.Checkbutton(choosePositionFrame, text='Random position',
                                                   variable=self.randomPositionVar, command=lambda: [[
                _widget.config(state='disabled' if self.randomPositionVar.get() else 'normal') for _widget in
                (xCustomPositionEntry, yCustomPositionEntry)],
                submitPositionButton.config(state='normal' if self.randomPositionVar.get() else 'disabled')])
        randomPositionCheckbutton.grid(row=5, column=1, columnspan=5)

        for _i, _e in zip(positions, (xCustomPositionEntry, yCustomPositionEntry)):
            _e.insert(0, _i)
        xCustomPositionEntry.selection_range(0, 'end')

        ttk.Label(alldialogFrame, text='or').grid(row=5, column=3, pady=5)

        choosePositionFrame_withMouse = ttk.LabelFrame(alldialogFrame, text='Pick position', labelanchor='n')
        choosePositionFrame_withMouse.grid(row=7, column=3, ipadx=15, ipady=5, sticky='ew')
        choosePositionFrame_withMouse.grid_columnconfigure(3, weight=1)

        _choosePositionFrame_withMouse = tk.Frame(choosePositionFrame_withMouse)
        _choosePositionFrame_withMouse.grid(row=3, column=3, pady=(5, 0))

        choosePositionFrame_withMouse_radiobutton = ttk.Radiobutton(_choosePositionFrame_withMouse, value='picker',
                                                                    variable=self.positionType,
                                                                    command=lambda: bindradio_all())
        choosePositionFrame_withMouse_radiobutton.grid(row=3, column=2, sticky='e')

        choosePositionWithMouseButton = ttk.Button(_choosePositionFrame_withMouse, text='Choose position',
                                                   command=lambda: choose_position_by_mouse(), state='disabled')
        choosePositionWithMouseButton.grid(row=3, column=3, ipadx=5)
        ##

        submitPositionFrame = tk.Frame(alldialogFrame)
        submitPositionFrame.grid(row=13, column=3, sticky='sew', pady=(20, 5))
        submitPositionFrame.grid_columnconfigure(3, weight=1)

        showPositionsLabel = ttk.Label(submitPositionFrame, text='Position: x=None; y=None')
        showPositionsLabel.grid(row=3, column=3, padx=5, columnspan=2)

        submitPositionButton = ttk.Button(submitPositionFrame, text='Submit', state='disabled',
                                          command=lambda: submit_position())
        submitPositionButton.grid(row=5, column=3, padx=5, sticky='sew')

        redcancelStyle = ttk.Style()
        redcancelStyle.configure('cancel.TButton', foreground='red')

        cancelbutton = ttk.Button(submitPositionFrame, text='Cancel', command=lambda: on_exit(), width=7,
                                  style='cancel.TButton')
        cancelbutton.grid(row=5, column=4)

        def update_text_on_return():
            nonlocal positions
            pos = [i if i.strip() else 'None' for i in (xCustomPositionEntry.get(), yCustomPositionEntry.get())]
            positions = tuple([int(c) for c in pos if c.isdigit()])
            showPositionsLabel.config(
                text=f'Position: x={pos[0][:4]}{"..." if len(pos[0]) > 4 else ""}; y={pos[1][:4]}{"..." if len(pos[1]) > 4 else ""}')

        def checkSubmitable(event=False):
            if not event:
                askPositionDialog.focus()
            submitPositionButton.config(state='disabled')
            if self.positionType.get().strip() != '':
                if xCustomPositionEntry.get().isdigit() and yCustomPositionEntry.get().isdigit():
                    submitPositionButton.config(state='normal')

            if event and self.positionType.get() == 'manual':
                update_text_on_return()

        def choose_position_by_mouse():
            transparent_layer = tk.Toplevel(askPositionDialog)
            transparent_layer.overrideredirect(True)
            transparent_layer.attributes('-alpha', 0.5)
            transparent_layer.state('zoomed')

            transparent_layer.attributes('-topmost', True)
            transparent_layer.config(cursor='crosshair')
            transparent_layer.focus()

            def quitChoose(_):
                nonlocal positions
                positions = mousex, mousey

                showPositionsLabel.config(text=f'Position: x={mousex}; y={mousey}')
                submitPositionButton.config(state='normal')
                transparent_layer.destroy()

            mousex, mousey = 0, 0

            displaying = tk.Frame(transparent_layer, background='yellow')
            displayPosition = tk.Label(displaying, text=f'x={mousex}; y={mousey}', background='yellow',
                                       font=('Calibri', 11, 'bold'))
            displayPosition.grid(row=3, column=3, padx=15)
            displaying.grid_columnconfigure(3, weight=1)

            transparent_layer.bind('<Button-1>', quitChoose)

            while transparent_layer.winfo_exists():
                mousex, mousey = pyautogui.position()
                displayPosition.config(text=f'x={mousex}; y={mousey}')
                displaying.place(x=10, y=10)

                if keyboard.is_pressed('esc'):
                    transparent_layer.destroy()
                    break

                transparent_layer.update()

        def bindradio_all():
            nonlocal positions
            pos = tuple(map(str, positions))
            for _widget in [choosePositionFrame_radiobutton, choosePositionFrame_withMouse_radiobutton]:
                if _widget.cget('value') == self.positionType.get():
                    _widgetdict = {
                        'manual': [randomPositionCheckbutton, xCustomPositionEntry, yCustomPositionEntry],
                        'picker': [choosePositionWithMouseButton]
                    }
                    for _key in _widgetdict.keys():
                        askPositionDialog.focus()
                        if _key == 'manual':
                            askPositionDialog.after(10, xCustomPositionEntry.focus)
                            pos = tuple([c.get() if c.get().isdigit() else str(positions[i]) for i, c in
                                         enumerate((xCustomPositionEntry, yCustomPositionEntry))])
                        elif _key == 'picker':
                            submitPositionButton.config(state='normal' if all(
                                0 <= c < s for c, s in zip(positions, pyautogui.size())) else 'disabled')

                        for __widget in _widgetdict[_key]:
                            if self.positionType.get().strip() == 'manual' and self.randomPositionVar.get() and __widget in [
                                xCustomPositionEntry, yCustomPositionEntry]:
                                __widget.config(state='disabled')
                                continue
                            __widget.config(
                                state='normal' if _key == self.positionType.get().strip() else 'disabled')
                    break

            positions = tuple(map(int, pos))
            showPositionsLabel.config(
                text=f'Position: x={pos[0][:4]}{"..." if len(pos[0]) > 4 else ""}; y={pos[1][:4]}{"..." if len(pos[1]) > 4 else ""}')

        def submit_position():
            if not pyautogui.onScreen(*map(int, positions)):
                messagebox.showwarning('Warning', 'Your chosen position is outside of the screen.',
                                       parent=askPositionDialog)
                return
            STORAGE.FIXED_POSITIONS = tuple(map(int, positions))
            self.customPositionRadiobutton.config(text=f'Custom ({", ".join(map(str, positions))})')
            askPositionDialog.destroy()
            Utilities.add_trigger_hotkey()
            Utilities.add_default_hotkeys()

            if not fromSetting:
                for _widget in [self.intervalHourEntry, self.intervalMinuteEntry, self.intervalSecondEntry,
                                self.intervalMillisecondEntry, self.mouseButtonOptionCombobox,
                                self.clickTypeOptionCombobox, self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton,
                                self.unlimitedRepeatRadiobutton, self.mousePositionRadiobutton,
                                self.customPositionRadiobutton]:
                    _widget.config(state='readonly' if _widget in [self.clickTypeOptionCombobox,
                                                                   self.mouseButtonOptionCombobox] else 'normal')

        xCustomPositionEntry.bind('<KeyRelease>', checkSubmitable)
        yCustomPositionEntry.bind('<KeyRelease>', checkSubmitable)
        xCustomPositionEntry.focus()
        bindradio_all()

        def on_exit():
            askPositionDialog.destroy()
            if not fromSetting:
                for _widget in [self.intervalHourEntry, self.intervalMinuteEntry, self.intervalSecondEntry,
                                self.intervalMillisecondEntry, self.mouseButtonOptionCombobox,
                                self.clickTypeOptionCombobox, self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton,
                                self.unlimitedRepeatRadiobutton, self.mousePositionRadiobutton,
                                self.customPositionRadiobutton]:
                    _widget.config(state='readonly' if _widget in [self.clickTypeOptionCombobox,
                                                                   self.mouseButtonOptionCombobox] else 'normal')

        askPositionDialog.protocol('WM_DELETE_WINDOW', on_exit)

    def bindHourChosen(self, value: str):
        if value == '':
            pass
        if value != '' and not value.isdigit() or value.isdigit() and len(value) > 2:
            return False
        return True

    def bindMinuteChosen(self, value: str):
        if value == '':
            pass
        if value != '':
            if len(value) > 2:
                return False
            if not value.isdigit():
                return False
            if int(value) > 59:
                return False
        return True

    def bindSecondChosen(self, value: str):
        if value == '':
            pass
        if value != '':
            if len(value) > 2:
                return False
            if not value.isdigit():
                return False
            if int(value) > 59:
                return False
        return True

    def bindMillisecondChosen(self, value: str):
        if value == '':
            pass
        else:
            if len(value) > 3:
                return False
            if not value.isdigit():
                return False
        return True

    def bindChosenAll(self, event: tk.Event | bool = False):
        if event and str(event.type) != '3':
            event.widget.master.focus()

            item = event.widget.get()[-3 if event.widget in [self.intervalMillisecondEntry] else -2:]
            event.widget.delete(0, 'end')
            event.widget.insert(0, item.zfill(3 if event.widget in [self.intervalMillisecondEntry] else 2))


def background_tasks():
    while True:
        if not STORAGE.RUNNING:
            continue

        if STORAGE.Garbage.root_geometry is None:
            STORAGE.Garbage.root_geometry = root.geometry()
        if root.positionVar.get() == 'mouse':
            root.mousePositionRadiobutton.config(text='Current ({0}, {1})'.format(*pyautogui.position()))
        else:
            root.mousePositionRadiobutton.config(text='Current (0, 0)')

        if keyboard.is_pressed('esc') or keyboard.is_pressed('enter'):
            if not STORAGE.Garbage.isMasterFocus:
                try:
                    root.focus_get().master.focus()
                    STORAGE.Garbage.isMasterFocus = True
                except (AttributeError, KeyError):
                    STORAGE.Garbage.isMasterFocus = False
            if root.limitedRepeatSpinbox.get().strip() == '':
                root.limitedRepeatSpinbox.set(1)
        else:
            STORAGE.Garbage.isMasterFocus = False
        root.update()
        time.sleep(0.1)


# noinspection PyUnresolvedReferences
def on_window_exit():
    if keyboard.is_pressed('ctrl+shift+alt'):
        Utilities.start(restart=True)
        return
    save_data()

    root.destroy()
    STORAGE.RUNNING = False

    backgroundThread.join(0)
    print(f'{__project__} {__version__} was closed.')
    _exit(0)


root: tk.Tk | Application | None = None
backgroundThread: threading.Thread | None = None
Utilities.start()
