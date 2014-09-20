from chili import command
import chili
import chili.keyboard
from chili.keyboard import hotkey
import chili.ui
from chili.timer import every
import chili.wm

import os
import time
import subprocess
import pytz
import datetime

last_key = 0
last_break = 0

def key_pressed(char, mask):
    global last_key
    last_key = time.time()

from Cocoa import NSApplication
NSApplication.sharedApplication().delegate().register_key_hook(key_pressed)

@command('echo')
def echo(text):
    chili.ui.prompt(text)

@command('say')
def say(text):
    os.system('say %s' % text)

@every(60)
def check_breaks(done, _):
    global last_key, last_break
    if last_key < last_break:
        print 'still in break'

    elif time.time() - last_key > 120:
        last_break = time.time()
        print 'break'

    elif last_break > 0 and time.time() - last_break > 3600:
        chili.ui.prompt('Your last break was over an hour ago. How about a break?', default='OK')

    done()

@hotkey('ctrl-cmd-m')
def maximize():
    window = chili.wm.get_focused_window()
    screen = chili.wm.get_window_screen(window)
    frame = screen.frame()
    print frame
    pos = chili.wm.get_window_pos(window)
    print pos.x, pos.y
    chili.wm.set_window_pos(window, frame.origin.x, frame.origin.y)
    chili.wm.set_window_size(window, frame.size.width, frame.size.height)

@hotkey('ctrl-cmd-1')
def left_half():
    window = chili.wm.get_focused_window()
    screen = chili.wm.get_window_screen(window)
    frame = screen.frame()
    chili.wm.set_window_pos(window, frame.origin.x, frame.origin.y)
    chili.wm.set_window_size(window, frame.size.width / 2, frame.size.height)

@hotkey('ctrl-cmd-2')
def right_half():
    window = chili.wm.get_focused_window()
    screen = chili.wm.get_window_screen(window)
    frame = screen.frame()
    chili.wm.set_window_pos(window, frame.size.width / 2, 0)
    chili.wm.set_window_size(window, frame.size.width / 2, frame.size.height)

@every(3600*5, 0.2)
def anki_prompt(done, snooze):
    def run_anki():
        chili.launch('/Applications/Anki.app')
        done()

    chili.ui.prompt('how about some anki?', default='Yes', alt='No',
        other='Snooze 10 Minutes', default_cb=run_anki, alt_cb=done,
        other_cb=lambda: snooze(600))

eastern = pytz.timezone('US/Eastern')
ny_clock_status_item = chili.ui.status_item_make(
    datetime.datetime.now(eastern).strftime('NY %H:%M'))

@every(60)
def ny_clock(done, snooze):
    eastern_now = datetime.datetime.now(eastern)
    ny_clock_status_item.text = eastern_now.strftime('NY %H:%M')
    done()

@command('zipcode')
def zipcode(_):
    type_('6382561')


@command('load')
def load(path):
    execfile(path)


@command('openmy')
def openmy(_):
    chili.open_with(os.path.expanduser('~/.chili/my.py'), '/Applications/MacVim.app')

@command('#')
def terminal(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = p.communicate()[0]
    chili.input(output)

@command('fasd')
def fasd(query):
    p = subprocess.Popen(['fasd','-al',query], stdout=subprocess.PIPE)
    output = p.communicate()[0]
    chili.input(output)

@command('~')
def home(_):
    chili.open(os.path.expanduser('~'))

@command('type')
def type_(text):
    chili.close()
    time.sleep(0.5)
    chili.keyboard.type_string(text)

@command('ma')
def mail(body):
    chili.open_url('mailto:%%20?body=%s' % body)
    chili.close(reactivate=False)

@command('with')
def openwith(text):
    split = map(unicode.strip,text.split(','))
    chili.open_with(os.path.expanduser(split[1]), split[0])

@command('restart')
def restart(_):
    os.chdir('/Users/benbonfil/Projects/chili/')
    os.execvp('/bin/sh',['/bin/sh', 'dev.sh'])

