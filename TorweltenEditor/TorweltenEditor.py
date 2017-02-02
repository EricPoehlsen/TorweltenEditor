import tkinter as tk
from application import Application

main = tk.Tk()
main.title("Torwelten Editor")
main.minsize(width="800", height="600")
screen = Application(main)
screen.pack(fill=tk.BOTH, expand=1)
main.mainloop()
