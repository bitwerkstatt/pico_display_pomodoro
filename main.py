import time
import math
import machine
import network
import ntptime
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P8
  

def reset_off_counter():
    global reset_button_counter
    reset_button_counter = 0

def start_pomodoro():
    global ps_current_state, ps_remaining_seconds, ps_cyles_done
    # Actual start
    if ps_current_state==IDLE:
        ps_remaining_seconds = pomo_schedules[selected_schedule][0]*60
        ps_current_state = WORK
        ps_cyles_done = 0
    # Resume
    if ps_current_state == INTERRUPTED:
        ps_current_state = ps_save_state
    led.set_rgb(0,255,0)
    period = 50 if DEV_MODE else 1000
    timer.init(period=period, callback=progress_pomodoro)


def pause_pomodoro():
    global ps_current_state, ps_save_state, ps_remaining_seconds, ps_cyles_done, ps_interruptions
    if (ps_current_state != IDLE) and (ps_current_state != INTERRUPTED):
        led.set_rgb(255,0,0)
        ps_save_state = ps_current_state
        ps_current_state = INTERRUPTED
        timer.deinit()
        ps_interruptions += 1
        draw_pomodoro()


def reset_pomodoro():
    global ps_current_state, ps_save_state, ps_remaining_seconds, ps_cyles_done, ps_interruptions
    ps_current_state = IDLE
    ps_save_state = IDLE
    ps_cyles_done = 0
    ps_interruptions = 0
    ps_remaining_seconds = pomo_schedules[selected_schedule][0]*60
    draw_pomodoro()


def progress_pomodoro(pin):
    global ps_current_state, ps_remaining_seconds, ps_cyles_done

    if ps_remaining_seconds == 0:
        if ps_current_state == WORK:
            ps_cyles_done += 1
            if (ps_cyles_done%2) == 0:
                ps_current_state = LONG_BREAK
                ps_remaining_seconds = long_pauses[selected_pause]*60
            else:
                ps_current_state = NORMAL_BREAK
                ps_remaining_seconds = pomo_schedules[selected_schedule][1]*60
        else:
            ps_current_state = WORK
            ps_remaining_seconds = pomo_schedules[selected_schedule][1]*60
    draw_pomodoro()
    ps_remaining_seconds -= 1

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


def draw_pomodoro():
    global ps_current_state
    title = f"{state_descriptions[ps_current_state]}"           
    remaining_time = f"{'{:02d}'.format(ps_remaining_seconds//60)}:{'{:02d}'.format(ps_remaining_seconds%60)}m"
    if ps_current_state == WORK:
        graphics.set_pen(GREEN)
    elif ps_current_state == NORMAL_BREAK or ps_current_state == LONG_BREAK:
        graphics.set_pen(RED)
    else:
        graphics.set_pen(ORANGE)
    graphics.clear()
    graphics.set_pen(WHITE)
    graphics.set_font("bitmap8")
    graphics.text(title, 5, 5)
    cycle_text = f"Stats (C/TC/INT): {ps_cyles_done%4}/{ps_cyles_done}/{ps_interruptions}"
    graphics.text(cycle_text, 5, 107)
    graphics.set_font("sans")
    message_space = graphics.measure_text(remaining_time, 2.0)
    graphics.text(remaining_time, (WIDTH-message_space)//2,HEIGHT//2)
    
    graphics.update()

def button_a_pressed(pin):
    global selected_schedule
    reset_off_counter()
    if ps_current_state == IDLE:    
        led.set_rgb(0,0,255)
        selected_schedule = (selected_schedule + 1) % len(pomo_schedules)
        graphics.set_pen(BLUE)
        graphics.clear()
        graphics.set_pen(WHITE)
        info_text = f"{pomo_schedules[selected_schedule][0]}/{pomo_schedules[selected_schedule][1]}"
        draw_settings("Selected timing", info_text)
    

def button_b_pressed(pin):
    global selected_pause
    reset_off_counter()
    if ps_current_state == IDLE:
        led.set_rgb(0,0,255)    
        selected_pause = (selected_pause + 1) % len(long_pauses)
        graphics.set_pen(BLUE)
        graphics.clear()
        graphics.set_pen(WHITE)
        info_text = f"{long_pauses[selected_pause]}"
        draw_settings("Selected long pause", info_text)

# Run / Pause
def button_x_pressed(pin):
    global ps_active, ps_remaining_seconds, ps_current_state, ps_cyles_done
    reset_off_counter()
    if ps_current_state == IDLE or ps_current_state == INTERRUPTED:
        start_pomodoro()
    else:
        pause_pomodoro()

# Reset and standby    
def button_y_pressed(pin):
    global reset_button_counter
    if ps_current_state == IDLE or ps_current_state == INTERRUPTED:
        reset_button_counter += 1
        if reset_button_counter == 2:
            reset_pomodoro()



# We use a landscape display 
graphics = PicoGraphics(DISPLAY_PICO_DISPLAY, pen_type=PEN_P8, rotate=0)

# Status LED
led = RGBLED(6, 7, 8)
led.set_rgb(255,0,0)

# The timer
timer = machine.Timer()

DEV_MODE = False # Set True for faster test runs

# So let's define those
BLACK = graphics.create_pen(0,0,0)
WHITE = graphics.create_pen(255,255,255)
RED = graphics.create_pen(239, 26, 45)
YELLOW = graphics.create_pen(255,255,0)
GREEN = graphics.create_pen(23, 66, 34)
BLUE = graphics.create_pen(33,115,184)
ORANGE = graphics.create_pen(251, 170, 30)

WIDTH = graphics.get_bounds()[0]
HEIGHT = graphics.get_bounds()[1]

pomo_schedules = [(25,5), (50, 10)]
long_pauses = [20, 30, 60, 10, 15]

IDLE = 0
WORK = 1
NORMAL_BREAK = 2
LONG_BREAK = 3
INTERRUPTED = 4

selected_schedule = 0
selected_pause = 0
ps_current_state = IDLE # 0=waiting, 1=work, 2=pause, 3=longpause
ps_save_state = IDLE
ps_cyles_done = 0
ps_interruptions = 0
ps_remaining_seconds = 0


state_descriptions = {
    0: "Idle",
    1: "Do some work!",
    2: "Take a break!",
    3: "Take a long break!",
    4: "You got interrupted..."
}

reset_button_counter = 0
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
