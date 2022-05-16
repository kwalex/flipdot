#! /usr/bin/env python

import random
import os.path
import time
import ephem
import datetime

from PIL import Image, ImageDraw, ImageFont, ImageOps


def rsrc(n):
    return os.path.join(os.path.dirname(__file__), n)


a1 = Image.open(rsrc("images/a1.png"))
a2 = Image.open(rsrc("images/a2.png"))
frames1 = {0: a1, 1: a1, 2: a2, 3: a2}

b1 = Image.open(rsrc("images/b1.png"))
b2 = Image.open(rsrc("images/b2.png"))
frames2 = {0: b1, 1: b1, 2: b2, 3: b2}

p1 = Image.open(rsrc("images/p1.png"))
p2 = Image.open(rsrc("images/p2.png"))
frames3 = {0: p1, 1: p1, 2: p2, 3: p2}

BigFont = ImageFont.truetype(rsrc("fonts/big.ttf"), 19)
MassiveFont = ImageFont.truetype(rsrc("fonts/massive.ttf"), 19)
SmallFont = ImageFont.truetype(rsrc("fonts/small.ttf"), 8)


def get_ephemera(city="New York"):
    """
    Calculates next full moon, current moon phase (percent), next sunrise, and
    next sunset for specified city (default is New York). Times are local.

    :return: Dict specifying 'FULL', 'MOON', 'SET', 'RISE'
    """
    loc = ephem.city(city)
    obs = ephem.Observer()
    obs.lat = loc.lat
    obs.lon = loc.lon

    today = datetime.date.today()
    s = ephem.Sun()
    m = ephem.Moon()
    m.compute()

    # Calculate days left til full moon
    full_moon = ephem.localtime(ephem.next_full_moon(today)).date()
    days_til_full = full_moon - today
    days_til_full = f"{days_til_full.days}d"

    result = {
        "FULL": days_til_full,
        "MOON": f"{int(m.phase)}%",
        "RISE": ephem.localtime(obs.next_rising(s)).strftime("%H%M"),
        "SET": ephem.localtime(obs.next_setting(s)).strftime("%H%M"),
    }

    return result


def scroll_text(d, text, font=BigFont):
    w, h = d.im.size
    draw = ImageDraw.Draw(d.im)
    tw, th = draw.textsize(text, font=font)
    shift = 0 if font == BigFont else -2
    for x in range(w, 0 - tw, -1):
        d.reset()
        draw.text((x, h - th + shift), text, font=font)
        d.send()
        time.sleep(0.06)
    del draw


def display_text(d, text, font=SmallFont, offset=0, final=True):
    w, h = d.im.size
    draw = ImageDraw.Draw(d.im)
    tw, th = draw.textsize(text, font=font)
    shift = 0 if font == BigFont else -3
    if offset != 0:
        shift -= offset
    d.reset()
    draw.text(((w / 2) - (tw / 2), h - th + shift), text, font=font)
    if final:
        d.send()
    del draw


def blink_text(d, text, n=3):
    for i in range(n):
        display_text(d, text)
        time.sleep(0.5)
        d.reset()
        d.send()
        time.sleep(0.5)


def clock(d, duration=10, blink=True, font=BigFont, offset=0):
    w, h = d.im.size
    draw = ImageDraw.Draw(d.im)
    start = time.time()
    now = start
    while now < (start + duration):
        now = time.time()

        main_text = time.strftime("%H%M")
        sec_text = time.strftime("%S")

        main_w, main_h = draw.textsize(main_text, font=font)

        # We'll force a single column between each second character, so calc the width digit by digit
        sec_w = sec_h = 0
        for letter in sec_text:
            char_w, char_h = draw.textsize(letter, SmallFont)
            sec_w += char_w + 1
            sec_h += char_h

        total_w = main_w + sec_w - 2
        total_h = main_h

        if blink is True and int(now) % 2 == 0:
            d.reset()
            draw.text(
                ((w / 2) - (total_w / 2), h - total_h + offset + 3), main_text, font=font, align="lb"
            )
            draw.text(
                ((w / 2) - (total_w / 2) + main_w, h + offset - 4), sec_text[0], font=SmallFont, align="lb"
            )
            draw.text(
                ((w / 2) - (total_w / 2) + main_w + char_w - 1, h + offset - 4), sec_text[1], font=SmallFont, align="lb"
            )
            d.send()
        else:
            d.reset()
            draw.text(
                ((w / 2) - (total_w / 2), h - total_h + offset + 3), main_text, font=font, align="lb"
            )
            draw.text(
                ((w / 2) - (total_w / 2) + main_w, h + offset - 4), sec_text[0], font=SmallFont, align="lb"
            )
            draw.text(
                ((w / 2) - (total_w / 2) + main_w + char_w - 1, h + offset - 4), sec_text[1], font=SmallFont, align="lb"
            )

            # Show dot
            draw.point((w - 2, 1))

            # Invert for last 5 seconds of minute
            if time.localtime().tm_sec > 54:
                # Invert display
                d.im = d.im.point(lambda x: 255 - x)

            d.send()
        time.sleep(0.1)


def infodense(d, duration=120, ephem_duration=5, blink=True):
    """
    Displays time of day and ephemera in fixed 56x14 format
    """

    w, h = d.im.size
    draw = ImageDraw.Draw(d.im)
    ephemera = get_ephemera()
    start = time.time()
    now = start
    while now < (start + duration):
        now = int(time.time())
        hour = time.strftime("%H")
        minute = time.strftime("%M")
        separator = False if (blink and (now % 2)) else True

        # Clear display's image
        d.reset()

        # Draw hour, big and aligned to left edge
        tw, th = draw.textsize(hour, font=BigFont)
        draw.text((-1, h), hour, font=BigFont, anchor="lb")

        # Store current column at right edge of time
        current_col = tw - 1

        # Draw separator if applic
        if separator:
            sep_col = current_col
            draw.point((sep_col, h - 1))

        current_col += 1

        # Draw minute, big and aligned to current_col
        tw, th = draw.textsize(minute, font=BigFont)
        draw.text((current_col - 1, h), minute, font=BigFont, anchor="lb")

        current_col += tw

        # Calculate which ephem to draw
        eph_index = int(now / ephem_duration) % len(ephemera)

        # Draw ephemera name or graphic header
        eph_name = list(ephemera)[eph_index]
        if eph_name == "RISE":
            head = Image.open(rsrc("images/sunrise.png"))
            d.im.paste(head, (31, 0))
        elif eph_name == "SET":
            head = Image.open(rsrc("images/sunset.png"))
            d.im.paste(head, (31, 0))
        else:
            text_by_letter(d, eph_name, SmallFont, (current_col - 1, (h / 2)))
            # tw, th = draw.textsize(eph_name, font=SmallFont)
            # draw.text((current_col, (h / 2)), eph_name, font=SmallFont, anchor="lb")

        # Draw ephemera value
        val = str(ephemera[eph_name])
        text_by_letter(d, val, SmallFont, (current_col - 1, (h)))
        # draw.text(
        #     (current_col, (h)), val, font=SmallFont, anchor="lb"
        # )

        d.send()

        time.sleep(0.1)


def text_by_letter(d, text, font, coords, colspace=-1, anchor="lb"):
    w, h = d.im.size
    x, y = coords
    draw = ImageDraw.Draw(d.im)
    for char in text:
        tw, th = draw.textsize(char, font=font)
        draw.text((x, y), char, font=font, anchor=anchor)
        x = x + tw + colspace


def animate(disp, i, w, d=1):
    l, h = -w, 29
    if d < 0:
        l, h = h, l
    for x in range(l, h, d):
        im = i[abs(x % len(i))]
        disp.reset()
        disp.im.paste(im, (x, 0))
        disp.send()
        time.sleep(0.1)


def white(disp):
    disp.reset()
    draw = ImageDraw.Draw(disp.im)

    w, h = disp.im.size
    draw.rectangle([0, 0, w, h], fill=(255, 255, 255))
    disp.send()


def black(disp):
    disp.reset()
    disp.send()


#
# animations:
#


def alien_1(d):
    animate(d, frames1, 19, 1)


def alien_2(d):
    animate(d, frames2, 14, -1)


def gobble(d):
    animate(d, frames3, 14, 1)


def dot(d):
    draw = ImageDraw.Draw(d.im)
    w, h = d.im.size
    mw = w / 2
    mh = h / 2
    for i in range(0, w):
        d.reset()
        draw.ellipse([(mw - i, mh - i), (mw + i, mh + i)], fill=(255, 255, 255))
        d.send()
        time.sleep(0.6 / (i + 1))
    del draw


def mitch(d):
    w, h = d.im.size
    d.reset(white=True)
    for i in range(0, 89):
        j = str(i + 10000)
        frame = Image.open(rsrc(f"images/mitch{j[1:5]}.png"))
        d.im.paste(frame)
        d.send()
        time.sleep(0.04)


def john(d):
    w, h = d.im.size
    d.reset(white=True)
    for i in range(1000, 1207):
        j = str(i + 100000)
        frame = Image.open(rsrc(f"john/Sequence {j[1:6]}.png"))
        d.im.paste(frame)
        d.send()
        time.sleep(0.04)


def john2(d):
    w, h = d.im.size
    d.reset(white=True)
    for i in range(1000, 1451):
        j = str(i + 100000)
        frame = Image.open(rsrc(f"john2/Sequence {j[1:6]}.png"))
        d.im.paste(frame)
        d.send()
        time.sleep(0.04)


def john3(d):
    w, h = d.im.size
    d.reset(white=True)
    for i in range(1000, 1254):
        j = str(i + 100000)
        frame = Image.open(rsrc(f"john3/Sequence {j[1:6]}.png"))
        d.im.paste(frame)
        d.send()
        time.sleep(0.04)


def john4(d):
    w, h = d.im.size
    d.reset(white=True)
    for i in range(1000, 1319):
        j = str(i + 100000)
        frame = Image.open(rsrc(f"john4/Sequence {j[1:6]}.png"))
        d.im.paste(frame, box=(1, -5))
        d.send()
        time.sleep(0.04)


def wipe_right(d):
    w, h = d.im.size
    d.reset(white=True)
    d.send()
    time.sleep(0.5)
    for x in range(1, w + 1):
        draw = ImageDraw.Draw(d.im)
        xy = (0, 0)
        sz = (x, h)
        draw.rectangle([xy, sz], fill=(0, 0, 0))
        del draw
        d.send()
        time.sleep(0.07)


def wipe_down(d):
    w, h = d.im.size
    d.reset()
    d.send()
    time.sleep(0.5)
    for y in range(1, h + 1):
        draw = ImageDraw.Draw(d.im)
        xy = (0, 0)
        sz = (w, y)
        draw.rectangle([xy, sz], fill=(255, 255, 255))
        del draw
        d.send()
        time.sleep(0.1)


def curtain(d):
    w, h = d.im.size
    for x in range(1, w + 1):
        draw = ImageDraw.Draw(d.im)
        xy = (w - x, 0)
        sz = (x, h)
        draw.rectangle([(0, 0), (w, h)], fill=(255, 255, 255))
        draw.rectangle([xy, sz], fill=(0, 0, 0))
        del draw
        d.send()
        time.sleep(0.1)


transitions = [
    dot,
    alien_1,
    alien_2,
    curtain,
    wipe_right,
    wipe_down,
    gobble,
]
# transitions = [dot]
random.shuffle(transitions)
t_idx = 0


def rand(d):
    global t_idx
    f = transitions[t_idx]
    t_idx = (t_idx + 1) % len(transitions)
    f(d)
