import serial
import time
from python_tools.pixmob_conversion_funcs import bits_to_arduino_string
from python_tools.effect_definitions import base_color_effects, tail_codes, special_effects
import datetime

EFFECTS_TO_SHOW = [
    {
        "main_effect": "RED",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
    {
        "main_effect": "WHITISH",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
    {
        "main_effect": "RED",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
    {
        "main_effect": "WHITISH",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
    {
        "main_effect": "RED",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
        {
        "main_effect": "WHITISH",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
    {
        "main_effect": "RED",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
            {
        "main_effect": "WHITISH",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
    {
        "main_effect": "RED",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
            {
        "main_effect": "WHITISH",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
    {
        "main_effect": "RED",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
            {
        "main_effect": "WHITISH",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
    {
        "main_effect": "RED",
        "tail_code": None,
        "duration": .5,
        "hold_with_repeated_send": True
    },
]


arduino = serial.Serial(port="COM3", baudrate=115200, timeout=.1)
time.sleep(2.5)

def send_effect(main_effect, tail_code, sleep_after_send=False):
    if main_effect in base_color_effects:
        effect_bits = base_color_effects[main_effect]
        if tail_code:
            if tail_code in tail_codes:
                effect_bits = effect_bits + tail_codes[tail_code]
            else:
                raise Exception("Invalid tail code name. See tail_codes in effect_definitions.py for options.")
    elif main_effect in special_effects:
        effect_bits = special_effects[main_effect]
        if tail_code:
            raise Exception("Tail code effects only supported on simple color effects found in base_color_effects of "
                            "effect_definitions.py. Set TAIL_CODE to None or choose a MAIN_EFFECT from base_color_effects "
                            "(instead of special_effects).")
    else:
        raise Exception("Invalid MAIN_EFFECT. See base_color_effects and special_effects in effect_definitions.py for "
                        "options.")
    arduino_string_ver = bits_to_arduino_string(effect_bits)
    arduino.write(bytes(arduino_string_ver, 'utf-8'))
    if sleep_after_send:
         # Wait for enough time for the arduino to transmit this code
        time.sleep(0.01 + 0.0008 * len(effect_bits))
    print(f"Sent effect: {main_effect}, {'no tail effect' if not tail_code else 'tail: ' + tail_code}.")

for effect_instance in EFFECTS_TO_SHOW:
    if effect_instance.get("main_effect"):
        if effect_instance.get("hold_with_repeated_send", None):
            start_time = datetime.datetime.now()
            while (datetime.datetime.now() - start_time).total_seconds() <= effect_instance["duration"]:
                send_effect(effect_instance.get("main_effect"), effect_instance.get("tail_code", None), sleep_after_send=True)
        else:
            send_effect(effect_instance.get("main_effect"), effect_instance.get("tail_code", None))
            time.sleep(effect_instance["duration"])
    else:
        time.sleep(effect_instance["duration"])
time.sleep(0.1)
