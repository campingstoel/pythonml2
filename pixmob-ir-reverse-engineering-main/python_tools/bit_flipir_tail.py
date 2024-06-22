import PySimpleGUI as sg
import serial
import clipboard
import time
from pixmob_conversion_funcs import bits_to_arduino_string
import config as cfg

# BitFlipIR
# This is a quick-and-dirty program requested by @Sean1983 to give a user a quick UI with some "bit"
# values in a list, where they can click on one to "flip" that bit and automatically send the new data via IR

# What to start the window's bit list at

STARTING_BITS = [1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1]
TAIL_START_BITS = [0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1]
# Make this bigger or smaller to change the size of everything in the GUI
SIZE_SCALING = 1.8

# How long to wait between sends after pressing "Resend 10x" (seconds).
RESEND_DELAY = 0.075

tailcode_mode = False

arduino = serial.Serial(port=cfg.ARDUINO_SERIAL_PORT, baudrate=cfg.ARDUINO_BAUD_RATE, timeout=.1)

############################################################
tailM = [sg.Column([[sg.Button(TAIL_START_BITS[tail_bit_num], pad=(0, 0), key=f"bit_{tail_bit_num+len(STARTING_BITS)}", button_color="green" if TAIL_START_BITS[tail_bit_num] == 1 else "red")], [sg.Text(tail_bit_num+len(STARTING_BITS), font='Helvitica 6')]], element_justification='c', pad=(0, 0)) for tail_bit_num in range(len(TAIL_START_BITS))],[sg.Text("", key="tail_text")],

layout = [[sg.Text("", key="scan_text")],
         [sg.Column([[sg.Button(STARTING_BITS[bit_num], pad=(0, 0), key=f"bit_{bit_num}", button_color="green" if STARTING_BITS[bit_num] == 1 else "red")], [sg.Text(bit_num, font='Helvitica 6')]], element_justification='c', pad=(0, 0)) for bit_num in range(len(STARTING_BITS))],
         [sg.Push(),sg.Column(tailM, key="ShowTailMenu", visible = False)],

          [sg.Button("Resend", key="resend"), sg.Button("Resend 10x", key="resend_10x"), sg.Button("Use Tailcode", key="use_tailcode"),
          sg.Push(), sg.Button("Copy to clipboard", key="copy"), sg.Button("Paste from clipboard", key="paste")],
         [sg.Text("", key="error_text", font='Helvitica 11 bold')],
         [sg.Exit()]]


window = sg.Window('BitFlipIR', layout, scaling=SIZE_SCALING)


def send_effect_from_bits(effect_bits):
    arduino_string_ver = bits_to_arduino_string(effect_bits)
    arduino.write(bytes(arduino_string_ver, 'utf-8'))

    print(f"Sent effect: {','.join([str(bit) for bit in effect_bits])} arduino string: {arduino_string_ver}")
def update_button_colors(window):
    try:
        [window[f"bit_{bit_num}"].update(button_color="green" if window[f"bit_{bit_num}"].get_text() == "1" else "red")
         for bit_num in range(len(STARTING_BITS))]
        [window[f"bit_{tail_bit_num+len(STARTING_BITS)}"].update(button_color="green" if window[f"bit_{tail_bit_num+len(STARTING_BITS)}"].get_text() == "1" else "red")
         for tail_bit_num in range(len(TAIL_START_BITS))]
    except:
        time.sleep(0.0075)
        [window[f"bit_{bit_num}"].update(button_color="green" if window[f"bit_{bit_num}"].get_text() == "1" else "red")
         for bit_num in range(len(STARTING_BITS))]
        [window[f"bit_{tail_bit_num+len(STARTING_BITS)}"].update(button_color="green" if window[f"bit_{tail_bit_num+len(STARTING_BITS)}"].get_text() == "1" else "red")
         for tail_bit_num in range(len(TAIL_START_BITS))]

while True:
    event, values = window.read()

    # Set all the button colors
    update_button_colors(window)

    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == "use_tailcode" and tailcode_mode == False:
        tailcode_mode = True
        window[f"ShowTailMenu"].update(visible=True)
        continue
    elif event == "use_tailcode" and tailcode_mode == True:
        tailcode_mode = False
        window[f"ShowTailMenu"].update(visible=False)
        continue
    elif event == "resend" :
        print("Will resend")  # Continue without changing bits
    elif event == "resend_10x":
        window[f"resend_10x"].disabled = True

        print("Will resend 10x")
        for _ in range(9):  # 9 because we will also resend one time later
            new_selected_bits = [int(window[f"bit_{bit_num}"].get_text()) for bit_num in range(len(STARTING_BITS))]
            new_tail_bits = [int(window[f"bit_{tail_bit_num+len(STARTING_BITS)}"].get_text()) for tail_bit_num in range(len(TAIL_START_BITS))]
            try:
                if tailcode_mode:
                    send_effect_from_bits(new_selected_bits + new_tail_bits)
                    time.sleep(RESEND_DELAY)
                else:
                    send_effect_from_bits(new_selected_bits)
            except:
                pass  # Error will still be shown from before
        time.sleep(1.5)
        window[f"resend_10x"].disabled=False
        continue
    elif event == "copy":
        clipboard.copy(str([int(window[f"bit_{bit_num}"].get_text()) for bit_num in range(len(STARTING_BITS))]))
        continue
    elif event == "paste":
        try:
            pasted_array = clipboard.paste()[1:-1].split(", ") if len(clipboard.paste()[1:-1].split(", ")) == len(
                clipboard.paste()[1:-1].split(",")) else clipboard.paste()[1:-1].split(",")
        except:
            sg.PopupError("Pasted text not in valid format (ex: [1,0,1,0])")
            continue

        if len(pasted_array) == len(STARTING_BITS):
            [window[f"bit_{bit_num}"].update('1' if pasted_array[bit_num] == '1' else 0) for bit_num in range(len(STARTING_BITS))]
            update_button_colors(window)
        else:
            sg.PopupError("Pasted text not in valid format, or not same length as STARTING BITS")
            continue
    elif window[event].get_text() == '1':
        window[event].update('0', button_color="darkred")
    else:
        window[event].update('1', button_color="darkgreen")

    new_selected_bits = [int(window[f"bit_{bit_num}"].get_text()) for bit_num in range(len(STARTING_BITS))]
    new_tail_bits = [int(window[f"bit_{tail_bit_num+len(STARTING_BITS)}"].get_text()) for tail_bit_num in range(len(TAIL_START_BITS))]
    try:
        if tailcode_mode == True:
            send_effect_from_bits(new_selected_bits + new_tail_bits)
            window["error_text"].update(error_msg)
        else:
            send_effect_from_bits(new_selected_bits)
    except:
        error_msg = "Invalid bit string (not sent). "
        if new_selected_bits[0] == 0:
            error_msg += "The bit list shouldn't start with a 0."
        elif new_selected_bits[-1] == 0:
            error_msg += "The bit list shouldn't end with a 0."
        else:
            error_msg += "The bit list probably has too many of the same bit in a row."
        window["error_text"].update(error_msg)
    else:
        window["error_text"].update("")
        window["scan_text"].update(f"Sent: {new_selected_bits}")
        window["tail_text"].update(f"Sent: {new_tail_bits}")

window.close()