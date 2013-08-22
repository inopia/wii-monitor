import math
import struct
from time import time

import cwiid
import wmplugin

# Button flags
STICK_KEY_UP = 0x0001
STICK_KEY_DOWN = 0x0002
STICK_KEY_RIGHT = 0x0004
STICK_KEY_LEFT = 0x0008

# array indices
X = 0
Y = 1
OFF_X = 0
OFF_Y = 3
OFF_MAX = 0
OFF_MIN = 1
OFF_CENTER = 2

# misc
DEADZONE = 10
RANGE = 12

calibrated = False
wiimote = None
"""
Calibration data.    Since the center isn't guaranteed to be the
average of min and max, we distinguish (as in the cases are not
symmetric) between being below center vs. being above center.
"""
center_x = 128
center_y = 128
x_neg_range = 96
x_pos_range = 96
y_neg_range = 96
y_pos_range = 96

# in data, accumulate mouse motions for all the events in each
# batch.    After the batch, return it to wminput.
axis_data = [0, 0]
"""
/* bookkeeping info */
static unsigned char info_init = 0;
static cwiid_wiimote_t *wiimote;
static int plugin_id;
static struct wmplugin_info info;

/* function declarations */
wmplugin_info_t wmplugin_info;
wmplugin_init_t wmplugin_init;
wmplugin_exec_t wmplugin_exec;
static void process_nunchuk(struct cwiid_nunchuk_mesg *mesg);
static void calibrate_joystick(void);
"""

def wmplugin_info():
    buttons = []
    axis = [
        ("X", wmplugin.REL, RANGE, -RANGE, 0, 0),
        ("Y", wmplugin.REL, RANGE, -RANGE, 0, 0)
    ]
    parameters = []

    return buttons, axis, parameters


def wmplugin_init(id, arg_wiimote):
    global wiimote
    wiimote = arg_wiimote
    if wmplugin.set_rpt_mode(id, cwiid.RPT_STATUS | cwiid.RPT_NUNCHUK):
        return -1
    else:
        return 0


def wmplugin_exec(messages):
    global wiimote, calibrated

    axis_data[X] = 0
    axis_data[Y] = 0

    for mesg in messages:
        if mesg[0] == cwiid.MESG_STATUS:
            if mesg[1]["ext_type"] == cwiid.EXT_NUNCHUK:
                pass  # TODO calibration doesnt work, using magic values
                # _calibrate_joystick()
        elif mesg[0] == cwiid.MESG_NUNCHUK:
            _process_nunchuk(mesg[1])

    return [], axis_data


def _process_nunchuk(mesg):
    global axis_data

    # st(x|y): stick value along direction
    stx = mesg["stick"][cwiid.X]
    sty = mesg["stick"][cwiid.Y]

    # d(x|y)(n|p): "delta x, direction=negative"
    dxn = (center_x - DEADZONE) - stx
    dxp = stx - (center_x + DEADZONE)
    dyn = (center_y - DEADZONE) - sty
    dyp = sty - (center_y + DEADZONE)

    axis_data[0] = 0
    # += (vs =): to accumulate the result of multiple events.

    if dxn >= 0:
        axis_data[X] -= int(dxn * RANGE / x_neg_range)
    elif dxp >= 0:
        axis_data[X] += int(dxp * RANGE / x_pos_range)
    else:
        axis_data[X] = 0


    if dyn >= 0:
        axis_data[Y] -= int(dyn * RANGE / y_neg_range)
    elif dyp >= 0:
        axis_data[Y] += int(dyp * RANGE / y_pos_range)
    else:
        axis_data[Y] = 0

def _calibrate_joystick():
    global x_neg_range, x_pos_range, y_neg_range, y_pos_range, center_x, center_y

    params = {
        "flags": cwiid.RW_REG | cwiid.RW_DECODE,
        "offset": 0xA40028,
        "len": 0
    }

    # TODO this trhows MemoryError for some reason and I cannot figure it out
    rawbuf = wiimote.read(**params)

    buf = struct.unpack("6B", rawbuf)

    center_x = buf[OFF_X + OFF_CENTER];
    x_neg_range = (center_x - DEADZONE) - buf[OFF_X + OFF_MIN]
    x_pos_range = buf[OFF_X + OFF_MAX] - (center_x + DEADZONE)

    center_y = buf[OFF_Y + OFF_CENTER];
    y_neg_range = (center_y - DEADZONE) - buf[OFF_Y + OFF_MIN]
    y_pos_range = buf[OFF_Y + OFF_MAX] - (center_y + DEADZONE)
