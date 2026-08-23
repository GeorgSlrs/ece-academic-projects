from tkinter import *
from tkinter import messagebox
import tkinter as tk
import os

root=Tk()
root.title("MENU")
root.geometry("500x600")
C = Canvas(root, bg="blue", height=250, width=300)
filename = PhotoImage(file = "menupic.png")
background_label = Label(root, image=filename)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
my_menu = Menu(root)
root.config(menu = my_menu)

def info():
    messagebox.showinfo(title="geia", message="Ο ΣΚΟΠΟΣ ΤΟΥ ΠΑΙΧΝΙΔΙΟΥ ΕΙΝΑΙ ΝΑ ΚΑΤΕΥΘΥΝΕΤΕ ΤΟ ΒΑΤΡΑΧΑΚΙ ΣΤΑ ΣΠΙΤΙΑ ΧΩΡΙΣ ΝΑ ΧΤΥΠΗΣΕΤΕ ΤΑ ΕΜΠΟΔΙΑ. ΕΧΕΤΕ 3 ΖΩΕΣ ΚΑΘΩΣ ΚΑΙ ΥΠΑΡΧΕΙ ΠΕΡΙΟΡΙΣΜΟΣ ΧΡΟΝΟΥ Ο ΟΠΟΙΟΣ ΒΡΙΣΚΕΤΑΙ ΣΤΗΝ ΠΡΑΣΙΝΗ ΜΠΑΡΑ. Ο ΒΑΤΡΑΧΟΣ ΚΟΥΝΙΕΤΑΙ ΜΕ ΤΑ ΚΟΥΜΠΙΑ WASD 'Η ΤΑ ΒΕΛΑΚΙΑ.")

file_menu = Menu(my_menu)
my_menu.add_cascade(label = "ΠΛΗΡΟΦΟΡΙΕΣ ΠΑΙΧΝΙΔΙΟΥ", command=info)

def frogger():
    os.system("frogger.py")

button2 = tk.Button( root, text = "Exit",fg="black",bg="green",command=exit)
button2.config(width=20, height=4)
button1 = tk.Button( root, text = "Start",fg="black",bg="green",command = frogger)
button1.config(width=20, height=4)
button1.place(x=175,y=220)
button2.place(x=175,y=310)


root.mainloop()
