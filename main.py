import time
import math
import machine
import network
import ntptime
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4
  

def toggle_standby():
    global standby, off_button_counter
    if standby:
        graphics.set_backlight(1.0)
        led.set_rgb(255,0,0)
    else:
        graphics.set_backlight(0.0)
        led.set_rgb(0,0,0)
    off_button_counter = 0
    standby = not standby


def reset_off_counter():
    global off_button_counter
    off_button_counter = 0

def start_pomodoro():
    global ps_active, ps_current_state, ps_remaining_seconds, ps_cyles_done
    if not ps_active:
        led.set_rgb(0,255,0)
        ps_remaining_seconds = pomo_schedules[selected_schedule][0]*60
        ps_current_state = 1
        ps_cyles_done = 0
        timer.init(period=1000, callback=progress_pomodoro)


def pause_pomodoro():
    global ps_active, ps_current_state, ps_remaining_seconds, ps_cyles_done
    if ps_active:
        led.set_rgb(255,0,0)
        ps_current_state = 0
        timer.deinit()


def reset_pomodoro():
    global ps_active, ps_current_state, ps_remaining_seconds, ps_cyles_done
    pass


def progress_pomodoro(pin):
    global ps_active, ps_current_state, ps_remaining_seconds, ps_cyles_done
    if ps_active: 
        title = f"{state_descriptions[ps_current_state]}"       
        remaining_time = f"{'{:02d}'.format(ps_remaining_seconds//60)}:{'{:02d}'.format(ps_remaining_seconds%60)}m"
        draw_pomodoro(title=title, remaining=remaining_time)
        ps_remaining_seconds -= 1
        print(f"Remaining seconds: {ps_remaining_seconds}")
        if ps_remaining_seconds == 0:
            if ps_current_state == WORK:
                ps_cyles_done += 1
                print(f"Cycles done: {ps_cyles_done}")
                if (ps_cyles_done%2) == 0:
                    print("Switching to longbreak...")
                    ps_current_state = LONG_BREAK
                    ps_remaining_seconds = long_pauses[selected_pause]*60
                else:
                    print("Switching to normal break...")
                    ps_current_state = BREAK
                    ps_remaining_seconds = pomo_schedules[selected_schedule][1]*60
            else:
                print("Switching back to work...")
                ps_current_state = WORK
                ps_remaining_seconds = pomo_schedules[selected_schedule][1]*60


def draw_settings(title, message):
    graphics.set_pen(BLUE)
    graphics.clear()
    graphics.set_pen(WHITE)
    graphics.set_font("bitmap8")
    title_space = graphics.measure_text(title, fixed_width=True)
    graphics.text(title, (WIDTH-title_space)//2, 5)
    graphics.set_font("sans")
    message_space = graphics.measure_text(message, 2.0)
    graphics.text(message, (WIDTH-message_space)//2,HEIGHT//2)
    graphics.update()


def draw_pomodoro(title, remaining):
    if ps_current_state == WORK:
        graphics.set_pen(GREEN)
    elif ps_current_state == BREAK or ps_current_state == LONG_BREAK:
        graphics.set_pen(RED)
    else:
        graphics.set_pen(YELLOW)
    graphics.clear()
    graphics.set_pen(WHITE)
    graphics.set_font("bitmap8")
    title_space = graphics.measure_text(title, fixed_width=True)
    graphics.text(title, (WIDTH-title_space)//2, 5)
    cycle_text = f"Cycles: {ps_cyles_done%4}, Today: {ps_cyles_done}"
    graphics.text(cycle_text, 0, 107)
    graphics.set_font("sans")
    message_space = graphics.measure_text(remaining, 2.0)
    graphics.text(remaining, (WIDTH-message_space)//2,HEIGHT//2)
    
    graphics.update()

def button_a_pressed(pin):
    global selected_schedule
    if standby:
        toggle_standby()
    reset_off_counter()
    led.set_rgb(0,0,255)
    if not ps_active:    
        selected_schedule = (selected_schedule + 1) % len(pomo_schedules)
        graphics.set_pen(BLUE)
        graphics.clear()
        graphics.set_pen(WHITE)
        info_text = f"{pomo_schedules[selected_schedule][0]}/{pomo_schedules[selected_schedule][1]}"
        draw_settings("Selected timing", info_text)
    

def button_b_pressed(pin):
    global selected_pause
    if standby:
        toggle_standby()
    reset_off_counter()

    led.set_rgb(0,0,255)
    if not ps_active:    
        selected_pause = (selected_pause + 1) % len(long_pauses)
        graphics.set_pen(BLUE)
        graphics.clear()
        graphics.set_pen(WHITE)
        info_text = f"{long_pauses[selected_pause]}"
        draw_settings("Selected long pause", info_text)

# Run / Pause
def button_x_pressed(pin):
    global ps_active, ps_remaining_seconds, ps_current_state, ps_cyles_done
    if standby:
        toggle_standby()
    reset_off_counter()
    if ps_active:
        pause_pomodoro()
    else:
        start_pomodoro()        
    ps_active = not ps_active

# Reset and standby    
def button_y_pressed(pin):
    global off_button_counter
    print("Button Y pressed")
    if not ps_active:
        off_button_counter += 1
        if off_button_counter > 2:
            toggle_standby()



# We use a landscape display with low color depth (16 colors)
graphics = PicoGraphics(DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=0)

# Status LED
led = RGBLED(6, 7, 8)
led.set_rgb(255,0,0)

# The timer
timer = machine.Timer()

# So let's define those
BLACK = graphics.create_pen(0,0,0)
WHITE = graphics.create_pen(255,255,255)
RED = graphics.create_pen(255,0,0)
YELLOW = graphics.create_pen(255,255,0)
GREEN = graphics.create_pen(0, 255, 0)
BLUE = graphics.create_pen(0,0,255)

WIDTH = graphics.get_bounds()[0]
HEIGHT = graphics.get_bounds()[1]

pomo_schedules = [(1,1),(50, 10), (25,5)]
long_pauses = [1,10, 15, 20, 30, 60]

selected_schedule = 0
selected_pause = 0
ps_active = False
ps_current_state = 0 # 0=waiting, 1=work, 2=pause, 3=longpause
ps_cyles_done = 0
ps_remaining_seconds = 0

WAIT = 0
WORK = 1
BREAK = 2
LONG_BREAK = 3

state_descriptions = {
    0: "Wait...",
    1: "Work",
    2: "Break",
    3: "Long Break"
}

off_button_counter = 0
standby = False

graphics.set_font("sans")
graphics.set_thickness(2)

led.set_rgb(0,0,255)


# Define the button handling using IRQs
a_button = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
a_button.irq(trigger=machine.Pin.IRQ_FALLING, handler = button_a_pressed)

b_button = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
b_button.irq(trigger=machine.Pin.IRQ_FALLING, handler = button_b_pressed)

x_button = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
x_button.irq(trigger=machine.Pin.IRQ_FALLING, handler = button_x_pressed)

y_button = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
y_button.irq(trigger=machine.Pin.IRQ_FALLING, handler = button_y_pressed)


while True:
    pass
