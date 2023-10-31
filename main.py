import badger2040
import jpegdec
import qrcode
import json
import time

display = badger2040.Badger2040()
display.set_update_speed(badger2040.UPDATE_NORMAL)
display.led(128)
jpeg = jpegdec.JPEG(display.display)

WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

current_badge = 0
badges = []

def initialize_badges():
    try:
        with open("badges.json","r") as f:
            result = json.load(f)
    except:
        result = []
    return result

def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    display.set_pen(15)
    display.rectangle(ox, oy, size, size)
    display.set_pen(0)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)


def render_badge(badge):
    display.set_font("bitmap8")
    display.set_pen(15)
    display.rectangle(0,0,WIDTH,HEIGHT)
    display.set_pen(0)
    display.rectangle(0,0,WIDTH,28)
    display.set_pen(15)
    display.text(badges[badge]["organization"], 2, 4, scale=2)
    
    display.set_pen(0)
    display.text(badges[badge]["name"], 2, 42, scale=2)
    display.text(badges[badge]["function1"], 2, 72, scale=2)
    display.text(badges[badge]["function2"], 2, 102, scale=2)
    
    # Open the JPEG file
    if badges[badge]["logo"] != "":
        jpeg.open_file(badges[badge]["logo"])
    
    # Decode the JPEG
    jpeg.decode(WIDTH-104,32, jpegdec.JPEG_SCALE_FULL, dither=True)
    
    display.update()

def render_contact(badge):
    
    code = qrcode.QRCode()
    display.set_font("bitmap8")
    display.set_pen(15)
    display.rectangle(0,0,WIDTH,HEIGHT)
    display.set_pen(0)
    
    code.set_text(badges[badge]["profile_qr"])
    size, _ = measure_qr_code(128, code)
    top = int((HEIGHT / 2) - (size / 2))
    left = int(WIDTH - size - top)
    draw_qr_code(left, top, 128, code)
    
    lines = slice_text(badges[badge]["profile_text"],2,WIDTH - size - 10)
    for i in range(len(lines)):
        display.text(lines[i], 2, 24 + i*20, scale = 2)
    
    display.update()

def render_call_to_action(badge):

    code = qrcode.QRCode()
    display.set_font("bitmap8")
    display.set_pen(15)
    display.rectangle(0,0,WIDTH,HEIGHT)
    display.set_pen(0)
    
    code.set_text(badges[badge]["call_to_action_qr"])
    size, _ = measure_qr_code(128, code)
    top = int((HEIGHT / 2) - (size / 2))
    left = int(WIDTH - size - top)
    draw_qr_code(left, top, 128, code)
    
    lines = slice_text(badges[badge]["call_to_action_text"],2,WIDTH - size - 10)
    for i in range(len(lines)):
        display.text(lines[i], 2, 24 + i*20, scale = 2)
    
    display.update()

def slice_text(text, text_size=1, max_width = WIDTH):
    words = text.split(" ")
    res = []
    line = ""
    
    for word in words:
        if (display.measure_text(line+word+" ", text_size)) < max_width:
            line = line + word + " "
        else:
            res.append(line.strip())
            line = word + " "
    res.append(line.strip())
    return res

def truncate_text(text, text_size, width=WIDTH):
    while True:
        length = display.measure_text(text, text_size)
        if length > 0 and length > width:
            text = text[:-1]
        else:
            text += ""
            return text

def warning(title, message):
    display.set_font("bitmap8")
    display.set_pen(15)
    display.rectangle(0,0,WIDTH,HEIGHT)
    display.set_pen(0)
    display.rectangle(0,0,WIDTH,20)
    display.set_pen(15)
    display.text(title, 2, 2, scale=2)
    
    lines = slice_text(message,2)
    
    display.set_pen(0)
    for i in range(len(lines)):
        display.text(lines[i], 2, 24 + i*20, scale = 2)
        
    display.update()

def handle_button(pin):
    global current_badge
    if pin == badger2040.BUTTON_A:
        render_badge(current_badge)
    if pin == badger2040.BUTTON_B:
        render_contact(current_badge)
    if pin == badger2040.BUTTON_C:
        render_call_to_action(current_badge)
    if pin == badger2040.BUTTON_UP:

        current_badge+=1
        if current_badge >= len(badges):
            current_badge = 0

        render_badge(current_badge)
    if pin == badger2040.BUTTON_DOWN:

        current_badge-=1
        if current_badge<0:
            current_badge=len(badges)-1

        render_badge(current_badge)
    time.sleep(0.5)


badges = initialize_badges()

while True:
    display.keepalive()

    if display.pressed(badger2040.BUTTON_A):
        handle_button(badger2040.BUTTON_A)
    if display.pressed(badger2040.BUTTON_B):
        handle_button(badger2040.BUTTON_B)
    if display.pressed(badger2040.BUTTON_C):
        handle_button(badger2040.BUTTON_C)

    if display.pressed(badger2040.BUTTON_UP):
        handle_button(badger2040.BUTTON_UP)
    if display.pressed(badger2040.BUTTON_DOWN):
        handle_button(badger2040.BUTTON_DOWN)

    display.halt()