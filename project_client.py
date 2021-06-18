# -*- coding: utf-8 -*-
"""
Created on Sat Jun 12 14:10:32 2021

@author: Andrea Zacconi, Luigi Incarnato
"""
import tkinter as tk
import socket
from time import sleep
import threading
import Domande as questions
from random import randint

#DATA THAT WE USE IN THE PROGRAM
window_main = tk.Tk()
window_main.title("Game Client")

client_name = ""
opponent_client_name = ""
client_score = 0
opponent_client_score = 0
client_choice = ""
game_rounds = 0
GAME_TIMER = 15
TOTAL_NUMBER_OF_ROUNDS = 5

thread = "Run"

player_answer = ""


#POSSIBLE ROLES FOR THE GAME
dictionaryRole = {
    
    "Alberto Angela" : { 1 : questions.HistoryQuestions,
                         2 : questions.HistoryOptions},
    
    "Matthew Mercer" : { 1 : questions.RoleQuestions,
                         2 : questions.RoleOptions},
    
    "Notch" : { 1 : questions.VideoGameQuestions,
                2 : questions.VideoGameOptions}
    
    }

#NETWORK CLIENT
client = None
HOST_ADDR = '127.0.0.1'
HOST_PORT = 8080

#FUNCTION FOR A RANDOM ROLE
def random_dictionary():
    var = randint(1, 3)
    if var == 1:
        return "Alberto Angela"
    elif var == 2:
        return "Matthew Mercer"
    else:
        return "Notch"
    
#BTN CREATION FOR QUESTIONS AND TRAP
def questions_creation():
    global btn_question_1, btn_question_2, btn_question_3, player_answer
    player_answer = "false"
    random_trap = randint(1, 3)
    
    if random_trap == 1:
        btn_question_1.config(command = lambda : question_choice("trap"))
        btn_question_2.config(command = lambda : question_choice("question2"))
        btn_question_3.config(command = lambda : question_choice("question3"))
    elif random_trap == 2:
        btn_question_1.config(command = lambda : question_choice("question1"))
        btn_question_2.config(command = lambda : question_choice("trap"))
        btn_question_3.config(command = lambda : question_choice("question3"))
    else:
        btn_question_1.config(command = lambda : question_choice("question1"))
        btn_question_2.config(command = lambda : question_choice("question2"))
        btn_question_3.config(command = lambda : question_choice("trap"))

#INITIAL GUI: NAME INSERTION AND SERVER CONNECTION
#-------------------------------------------------
top_welcome_frame = tk.Frame(window_main)
lbl_name = tk.Label(top_welcome_frame, text = "Name:")
lbl_name.pack(side = tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side = tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text = "Connect", command = lambda : connect())
btn_connect.pack(side = tk.LEFT)
top_welcome_frame.pack(side = tk.TOP)

top_message_frame = tk.Frame(window_main)
lbl_line = tk.Label(top_message_frame, text="-----------------------------------------------------------").pack()
lbl_welcome = tk.Label(top_message_frame, text = "")
lbl_welcome.pack()
lbl_line_server = tk.Label(top_message_frame, text="-----------------------------------------------------------")
lbl_line_server.pack_forget()
top_message_frame.pack(side = tk.TOP)
#-------------------------------------------------


#SECONDARY GUI: LABELS FOR VARIUS DATAS
#-------------------------------------------------
top_frame = tk.Frame(window_main)
top_left_frame = tk.Frame(top_frame, highlightbackground = "green", highlightcolor = "green", highlightthickness=1)
lbl_your_name = tk.Label(top_left_frame, text = "Your name: " + client_name, font = "Helvetica 13 bold")
lbl_opponent_name = tk.Label(top_left_frame, text = "Opponent: " + opponent_client_name)
lbl_your_name.grid(row = 0, column = 0, padx = 5, pady = 8)
lbl_opponent_name.grid(row = 1, column = 0, padx = 5, pady = 8)
top_left_frame.pack(side = tk.LEFT, padx = (10, 10))


top_right_frame = tk.Frame(top_frame, highlightbackground = "green", highlightcolor = "green", highlightthickness = 1)
lbl_game_round = tk.Label(top_right_frame, text = "Round (x), time remaining: ", foreground = "blue", font = "Helvetica 14 bold")
lbl_timer = tk.Label(top_right_frame, text = " ", font = "Helvetica 24 bold", foreground = "blue")
lbl_game_round.grid(row = 0, column = 0, padx = 5, pady = 5)
lbl_timer.grid(row = 1, column = 0, padx = 5, pady = 5)
top_right_frame.pack(side = tk.RIGHT, padx = (10, 10))

top_frame.pack_forget()
#-------------------------------------------------


#TERTIARY GUI: GAME LOG
#-------------------------------------------------
middle_frame = tk.Frame(window_main)

lbl_line = tk.Label(middle_frame, text = "-----------------------------------------------------------").pack()
lbl_line = tk.Label(middle_frame, text = "---- GAME LOG ----", font = "Helvetica 13 bold", foreground = "blue").pack()
lbl_line = tk.Label(middle_frame, text = "-----------------------------------------------------------").pack()
#ROLE CREATION
role = random_dictionary()
lbl_your_role = tk.Label(middle_frame, text = "Your role is: " + role, font = "Helvetica 13 bold")
lbl_your_role.pack()

round_frame = tk.Frame(middle_frame)
#BTNS CREATION
btn_question_1 = tk.Button(round_frame, text = "1")
btn_question_2 = tk.Button(round_frame, text = "2")
btn_question_3 = tk.Button(round_frame, text = "3")      
questions_creation()
btn_question_1.grid(row = 0, column = 0)
btn_question_2.grid(row = 0, column = 1)
btn_question_3.grid(row = 0, column = 2)
round_frame.pack(side = tk.TOP)

lbl_question = tk.Label(middle_frame, text = "", font = "Helvetica 13 bold")

final_frame = tk.Frame(middle_frame)
lbl_line = tk.Label(final_frame, text = "-----------------------------------------------------------").pack()
lbl_final_result = tk.Label(final_frame, text = " ", font = "Helvetica 13 bold", foreground = "blue")
lbl_final_result.pack()
lbl_line = tk.Label(final_frame, text = "-----------------------------------------------------------").pack()
final_frame.pack(side = tk.TOP)

middle_frame.pack_forget()
#-------------------------------------------------


#TAKING THE QUESTION AND ALL HIS OPTIONS BASED ON THE BUTTON SELECTION
question = None
correct_answer = None
question_number = None

#FINAL GUI: ANSWERS
#-------------------------------------------------
button_frame = tk.Frame(window_main)

#BTNS ANSWERS CREATION
btn_answer_1 = tk.Button(button_frame, text = "1", state = tk.DISABLED)
btn_answer_2 = tk.Button(button_frame, text = "2", state = tk.DISABLED)
btn_answer_3 = tk.Button(button_frame, text = "3", state = tk.DISABLED)
lbl_answer_1 = tk.Label(button_frame, text = "")
lbl_answer_2 = tk.Label(button_frame, text = "")
lbl_answer_3 = tk.Label(button_frame, text = "")
btn_answer_1.grid(row = 0, column = 0)
btn_answer_2.grid(row = 1, column = 0)
btn_answer_3.grid(row = 2, column = 0)
lbl_answer_1.grid(row = 0, column = 1)
lbl_answer_2.grid(row = 1, column = 1)
lbl_answer_3.grid(row = 2, column = 1)
button_frame.pack(side = tk.BOTTOM)
button_frame.pack_forget()

#FUNCTION TAKE QUESTION ANS HIS ANSWRERS
def question_choice(arg):
    global client_choice, question, correct_answer, question_number, lbl_question, btn_question_1, btn_question_2, btn_question_3
    client_choice = arg 
    if client_choice == "trap":
        client.send(("Game_Round" + str(game_rounds) + client_choice).encode())
        enable_disable_buttons2("disable")
    else:
        question_number = randint(1, 7)
        question = dictionaryRole[role][1][question_number]
        correct_answer = dictionaryRole[role][2][question_number][1]
        lbl_question.config(text = question)
        lbl_question.pack()
        enable_disable_buttons2("disable")
        create_answers()
        
#FUNCTION CREATE ANSWERS
def create_answers():
    global btn_answer_1, btn_answer_2, btn_answer_3, lbl_answer_1, lbl_answer_2, lbl_answer_3
    random_answers = []
    x = 1
    while True:
        random_number = randint(1, 3)
        if random_number not in random_answers:
            random_answers.append(random_number)
            if x == 1:
                answer = dictionaryRole[role][2][question_number][random_number]
                btn_answer_1.config(command = lambda : result(answer))
                lbl_answer_1.config(text = answer)
                x = x + 1
            elif x == 2:
                answer2 = dictionaryRole[role][2][question_number][random_number]
                btn_answer_2.config(command = lambda : result(answer2))
                lbl_answer_2.config(text = answer2)
                x = x + 1
            elif x == 3:
                answer3 = dictionaryRole[role][2][question_number][random_number]
                btn_answer_3.config(command = lambda : result(answer3))
                lbl_answer_3.config(text = answer3)
                break;
            
    enable_disable_buttons1("enable")
            
#FUNCTION SCORE RESULT
def result(arg):
    
    global client_score, player_answer
    
    if arg == correct_answer:
        player_answer = "true"
        client_score += 1
        client.send(("Game_Round" + str(game_rounds) + "correct").encode())
    else:
        player_answer = "true"
        client.send(("Game_Round" + str(game_rounds) + "incorrect").encode())
        
    enable_disable_buttons1("disable")
    
#FUNCTION CONNECT
def connect():
    global client_name
    if len(ent_name.get()) < 1:
        tk.messagebox.showerror(title = "ERROR!!!", message = "You MUST enter your first name <e.g. John>")
    else:
        client_name = ent_name.get()
        lbl_your_name["text"] = "Your name: " + client_name
        connect_to_server(client_name)
       
#FUNCTION CONNECT TO SERVER
def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR, client_name
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode())

        btn_connect.config(state = tk.DISABLED)
        ent_name.config(state = tk.DISABLED)
        lbl_name.config(state = tk.DISABLED)
        enable_disable_buttons1("disable")

        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title = "ERROR!!!", message = "Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")

#FUNCTION TIMER PER ROND
def count_down(my_timer, nothing):
    global game_rounds, thread
    
    thread = "Run"
    
    if game_rounds <= TOTAL_NUMBER_OF_ROUNDS:
        game_rounds += 1

    lbl_game_round["text"] = "Round " + str(game_rounds) + ", time remaining: "  
    while my_timer > 0:
        my_timer = my_timer - 1
        lbl_timer["text"] = my_timer
        sleep(1)
        
    if(player_answer == "false"):
        client.send(("Game_Round" + str(game_rounds) + "incorrect").encode())
    
    thread = "Finished"

#FUNCTION TO DISABLE THE ANSWERS BUTTONS
def enable_disable_buttons1(todo):
    if todo == "disable":
        btn_answer_1.config(state = tk.DISABLED)
        btn_answer_2.config(state = tk.DISABLED)
        btn_answer_3.config(state = tk.DISABLED)
    else:
        btn_answer_1.config(state = tk.NORMAL)
        btn_answer_2.config(state = tk.NORMAL)
        btn_answer_3.config(state = tk.NORMAL)
        
#FUNCTION TO DISABLE THE QUESTIONS BUTTONS
def enable_disable_buttons2(todo): 
    if todo == "disable":
        btn_question_1.config(state = tk.DISABLED)
        btn_question_2.config(state = tk.DISABLED)
        btn_question_3.config(state = tk.DISABLED)
    else:
        btn_question_1.config(state = tk.NORMAL)
        btn_question_2.config(state = tk.NORMAL)
        btn_question_3.config(state = tk.NORMAL)
        
#FUNCTION TO RESTART THE ROUND
def reset():
    global role 
    while(thread!="Finished"):
        sleep(1)
    
    lbl_question.config(text = "")
    lbl_answer_1.config(text = "")
    lbl_answer_2.config(text = "")
    lbl_answer_3.config(text = "")
    role = random_dictionary()
    lbl_your_role["text"] = "Your role is:" + role
    questions_creation()
    enable_disable_buttons2("enable")  
    threading._start_new_thread(count_down, (GAME_TIMER, ""))
    
#FUNCTION MESSAGE TO AND FROM SERVER
def receive_message_from_server(sck, m):
    global client_name, opponent_client_name, game_rounds
    global client_choice, opponent_client_choice, opponent_client_score, thread1
    while True:
        from_server = sck.recv(4096)
        
        print(from_server.decode())

        if not from_server: break

        if from_server.startswith("welcome".encode()):
            if from_server == "welcome1":
                lbl_welcome["text"] = "Server says: Welcome " + client_name + "! Waiting for player 2"
            elif from_server == "welcome2":
                lbl_welcome["text"] = "Server says: Welcome " + client_name + "! Game will start soon"
            lbl_line_server.pack()

        elif from_server.startswith("opponent_name$".encode()):
            opponent_client_name = from_server.replace("opponent_name$".encode(), "".encode())
            lbl_opponent_name["text"] = "Opponent: " + opponent_client_name.decode()
            top_frame.pack()
            middle_frame.pack()
            button_frame.pack()

            threading._start_new_thread(count_down, (GAME_TIMER, ""))
            lbl_welcome.config(state = tk.DISABLED)
            lbl_line_server.config(state = tk.DISABLED)
            
                
        elif from_server.startswith("$trapped".encode()):           
            lbl_final_result["text"] = "You won with: " + str(client_score) + " point because your oppenent has been trapped"

        elif from_server.startswith("$opponent_result".encode()):
            opponent_client_choice = from_server.replace("$opponent_result".encode(), "".encode())

            if opponent_client_choice.decode() == "correct":
                opponent_client_score += 1
                
            reset()
            if game_rounds == TOTAL_NUMBER_OF_ROUNDS:
                final_result = ""
                color = ""
                if client_score > opponent_client_score:
                    final_result = "(You Won!!!)"
                    color = "green"
                elif client_score < opponent_client_score:
                    final_result = "(You Lost!!!)"
                    color = "red"
                else:
                    final_result = "(Draw!!!)"
                    color = "black"

                lbl_final_result["text"] = "FINAL RESULT: " + str(client_score) + " - " + str(opponent_client_score) + " " + final_result
                lbl_final_result.config(foreground = color)

                enable_disable_buttons1("disable")
                game_rounds = 0
                client_score = 0
                opponent_client_score = 0
                
    sck.close()

window_main.mainloop()
