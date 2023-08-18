#!/usr/bin/env python3
'''Hello to the world from ev3dev.org'''

import os
import sys
import socket
import time
from ev3dev2.motor import MoveTank, SpeedPercent, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D

# state constants
ON = True
OFF = False
SERVER = None
CLIENT = None
PORT = 6969

def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)


def reset_console():
    '''Resets the console to the default state'''
    print('\x1Bc', end='')


def set_cursor(state):
    '''Turn the cursor on or off'''
    if state:
        print('\x1B[?25h', end='')
    else:
        print('\x1B[?25l', end='')


def set_font(name):
    '''Sets the console font

    A full list of fonts can be found with `ls /usr/share/consolefonts`
    '''
    os.system('setfont ' + name)

def clientProgram(client: socket.socket):
    movetank = MoveTank(OUTPUT_B, OUTPUT_C)
    while True:
        message = client.recv(1024).decode()
        if not message:
            break
        elif message != "!DISCONNECT":
            commands = message.split()
            command = commands[0].lower().strip()
            param = float(commands[1])
            print(command, param)
            if command == "fw":
                movetank.on_for_seconds(SpeedPercent(50), SpeedPercent(50), param)
            elif command == "bw":
                movetank.on_for_seconds(SpeedPercent(-50), SpeedPercent(-50), param)
            elif command == "lf":
                movetank.on_for_seconds(SpeedPercent(-50), SpeedPercent(50), param)
            elif command == "ri":
                movetank.on_for_seconds(SpeedPercent(50), SpeedPercent(-50), param)
                

        else:
            client.send(message.encode("utf-8"))
            client.close()
            break

def main():
    '''The main function of our program'''

    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-TerminusBold14')
    # set up temporary server socket
    # to find out server IP
    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.bind((socket.gethostbyname(socket.gethostname()), PORT))
    # server_socket.listen()
    # print("Waiting for connection at " + socket.gethostbyname(socket.gethostname()))
    # conn, addr = server_socket.accept()
    # print("Connection from " + addr[0])
    # SERVER = addr[0]
    # print("Closing connection, restarting as client")
    # conn.close()
    SERVER="169.254.79.176"
    CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    CLIENT.connect((SERVER, PORT))
    print("Connected")
    clientProgram(CLIENT)
    print("Disconnected. Exiting in 5 seconds.")
    # wait a bit so you have time to look at the display before the program
    # exits
    time.sleep(5)

if __name__ == '__main__':
    main()
