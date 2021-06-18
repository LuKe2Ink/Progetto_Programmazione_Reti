# -*- coding: utf-8 -*-
"""
Created on Sat Jun 12 15:30:28 2021

@author: Andrea Zacconi, Luigi Incarnato
"""

import tkinter as tk
import socket
import threading
from time import sleep


window = tk.Tk()
window.title("Server")

#GUI OF SERVER
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Address: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="**********Client List**********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=10, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = '127.0.0.1'
HOST_PORT = 8080
client_name = " "
clients = []
clients_names = []
player_data = []

flag = "Not trapped"

#FUNCTION START SERVER
def start_server():
    global server, HOST_ADDR, HOST_PORT
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print (socket.AF_INET)
    print (socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Address: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)

#FUNCTION STOP SERVER
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)

#FUNCTION ACCEPT CLIENT
def accept_clients(the_server, y):
    while True:
        if len(clients) < 2:
            client, addr = the_server.accept()
            clients.append(client)
            threading._start_new_thread(send_receive_client_message, (client, addr))

#FUNCTION SEND MESSAGE TO CLIENT
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, player_data, player0, player1,flag

    client_msg = " "

    client_name = client_connection.recv(4096)
    if len(clients) < 2:
        client_connection.send("welcome1".encode())
    else:
        client_connection.send("welcome2".encode())

    clients_names.append(client_name)
    update_client_names_display(clients_names)

    if len(clients) > 1:
        sleep(1)
        clients[0].send(("opponent_name$" + clients_names[1].decode()).encode())
        clients[1].send(("opponent_name$" + clients_names[0].decode()).encode())

    while True:
        data = client_connection.recv(4096)
        if not data: break
    
        player_result = data[11:len(data)]
        
        if player_result.decode() == 'trap':
            flag = "Trapped"
            break

        msg = {
            "result": player_result,
            "socket": client_connection
        }

        if len(player_data) < 2:
            player_data.append(msg)

        if len(player_data) == 2:
            
            if flag != "Trapped":
                player_data[0].get("socket").send(("$opponent_result" + player_data[1].get("result").decode()).encode())
                player_data[1].get("socket").send(("$opponent_result" + player_data[0].get("result").decode()).encode())
    
                player_data = []

    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    clients[0].send(("$trapped").encode())
    client_connection.close()

    update_client_names_display(clients_names)


#GET INDEX CLIENT
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx

#FUNCTION UPDATE GUI SERVER
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c.decode()+"\n")
    tkDisplay.config(state=tk.DISABLED)


window.mainloop()