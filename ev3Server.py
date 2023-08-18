import socket
import threading
import sys
import printlogger
import tkinter as tk

HOST = socket.gethostbyname(socket.gethostname())
PORT = 6969
FORMAT = "utf-8"
ADDR = (HOST, PORT)
MAX_CONNECTIONS = 1
EVENT_SERVER_STOP = threading.Event()
EVENT_SERVER_CONNECT = threading.Event()
EVENT_CLIENT_DISCONNECT = threading.Event()
# CONNECTED_CLIENTS = threading.BoundedSemaphore(MAX_CONNECTIONS)
CLIENTS = []
SERVER_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER_SOCK.bind(ADDR)
TEXT_OUT = None
TEXT_IN = None
PL = None
SB = None
ROOT = None

def socket_reader(conn: socket.socket, addr:str, printlogger: printlogger.PrintLogger):
    """
    Read data coming in through a socket, print it to console.
    If incoming message reads '!DISCONNECT' closes connection.
    Assumes client side would first send '!DISCONNECT' and close client socket.
    Reading from socket will block until data is received or socket is closed.

    conn: Socket to read from. Reading will block until data is received or socket is closed.
    addr: Sender IP
    printlogger: Unused. Intended for printing to GUI instead of console.
    """

    while not EVENT_CLIENT_DISCONNECT.is_set():
        message = conn.recv(1024)
        if message:
            message = message.decode(FORMAT)
            if message != "!DISCONNECT":
                print(f"{addr[0]}: {message}")
            else:
                print(f"[DISCONNECT] {addr[0]} terminated connection")
                EVENT_CLIENT_DISCONNECT.set()
                # CONNECTED_CLIENTS.release()
                CLIENTS.remove(conn)
                break
        else:
            print(f"[DISCONNECT] Disconnected from {addr}")
            EVENT_CLIENT_DISCONNECT.set()
            # CONNECTED_CLIENTS.release()
            CLIENTS.remove(conn)
            break

def socket_writer(message: str, printlogger: printlogger.PrintLogger):
    """
    Attempts to write data to all active sockets.
    If incoming message reads '!DISCONNECT' instructs connected client(s) to close their sockets.

    message: The data to write to the socket.
    printlogger: Unused. Intended for printing to GUI instead of console.
    """
    
    if len(CLIENTS) != 0:
        if message.strip().lower() != "bye":
            for conn in CLIENTS:
                message = message.encode(FORMAT)
                conn.send(message)
        else:
            for conn in CLIENTS:
                conn.send("!DISCONNECT".encode(FORMAT))
    else:
        print("[WARN] No active connections")

def server_start():
    """
    Main server loop. Listens for incoming connections and reads from each of them
    in separate threads. Also registers incoming connections for socket_writer.
    Will block until a new connection is established.
    Will only allow MAX_CONNECTIONS number of connection requests.
    """

    print(f"[START] Server started")
    SERVER_SOCK.listen(MAX_CONNECTIONS)
    print(f"[READY] Listening on {ADDR[0]}, {ADDR[1]}")
    try:
        while not EVENT_SERVER_STOP.is_set():
            clients = len(CLIENTS)
            plural = ""
            if len(CLIENTS) != 1:
                plural = "s"
            print(f"[STATUS] {clients} active connection{plural}")
            conn, addr = SERVER_SOCK.accept()
            # CONNECTED_CLIENTS.acquire()
            print(f"[CONNECT] Incoming connection from {addr[0]}")
            CLIENTS.append(conn)
            handle_read = threading.Thread(target=socket_reader, args=(conn, addr, PL))
            EVENT_CLIENT_DISCONNECT.clear()
            handle_read.start()
    except:
        pass
    finally:
            SERVER_SOCK.close()

def cli_handler(event:tk.Event):
    """
    Handle command input from text input field.
    Takes input and sends it to socket_writer.
    """

    message = TEXT_IN.get()
    TEXT_IN.delete(0, len(message))
    print(f"> {message}")
    socket_writer(message=message, printlogger=PL)
    
def on_closing():
    """
    Handle closing of application window.
    Raises flag for server to stop.
    Closes all active connections.
    Destroys all GUI elements.
    """

    EVENT_SERVER_STOP.set()
    for conn in CLIENTS:
        conn.close()
    SERVER_SOCK.close()
    ROOT.destroy()



if __name__ == '__main__':
    ROOT = tk.Tk()
    TEXT_OUT_FRAME = tk.Frame(ROOT)
    TEXT_OUT_FRAME.pack()
    TEXT_OUT = tk.Text(TEXT_OUT_FRAME)
    TEXT_OUT.pack(side="left")
    SB = tk.Scrollbar(TEXT_OUT_FRAME, orient="vertical", command=TEXT_OUT.yview)
    SB.pack(side="right", fill="y")
    TEXT_IN = tk.Entry()
    TEXT_IN.pack(side="bottom", fill="x")
    PL = printlogger.PrintLogger(TEXT_OUT)
    sys.stdout = PL



    server = threading.Thread(target=server_start)
    server.start()
    ROOT.protocol("WM_DELETE_WINDOW", on_closing)
    ROOT.bind("<Return>", cli_handler)
    ROOT.mainloop()