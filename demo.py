#! /usr/bin/env python

import sys
import time

from demo import animations
from flipdot import client, display


d = display.Display(56, 14,
                    panels={
                        1: ((0, 0), (28, 7)),
                        2: ((0, 7), (28, 7)),
                        3: ((28, 0), (28, 7)),
                        4: ((28, 7), (28, 7))
                    })


def transition(d):
    animations.rand(d)


def mainloop(d):
    # animations.black(d)
    # time.sleep(0.5)
    # animations.white(d)
    # time.sleep(0.50)
    # for i in range(0, 10):
    #     animations.john4(d)
    # animations.infodense(d, 120)
    animations.clock(d, 10, font=animations.MassiveFont, offset=-3)
    # animations.white(d)
    # time.sleep(2)
    # animations.black(d)
    # time.sleep(1)

    # animations.scroll_text(d, "BIG SCROLL", font=animations.BigFont)
    # transition(d)
    # transition(d)
    # transition(d)
    # transition(d)
    # animations.scroll_text(d, "Small scroll.", font=animations.SmallFont)
    # time.sleep(0.5)
    # transition(d)
    # d.reset()
    # d.send()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "udp":
        d.connect(client.UDPClient("localhost", 9999))
    else:
        d.connect(client.SerialClient('/dev/tty.usbserial-AB0LZJC6'))
    try:
        # intro(d)
        while True:
            mainloop(d)
    finally:
        d.disconnect()


if __name__ == "__main__":
    main()
