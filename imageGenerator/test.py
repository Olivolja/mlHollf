from tkinter import *

root = Tk()
main_cnv = Canvas(root, width=1000, height=1000, bg="red")
main_cnv.pack(side=LEFT)

entry_cnv = Canvas(root, width=200, height=1000, bg="green")
entry_cnv.pack(side=RIGHT)

force_dict = {"force_0" : ["down", 1]}
moment_dict = {"moment_0" : ("cv", 2)}
load_dict = {"load_0": ("up", 3)}

f_label = Label(main_cnv, text=str(force_dict["force_0"]))
f_label.pack()

m_label = Label(main_cnv, text=str(moment_dict["moment_0"]))
m_label.pack()

l_label = Label(main_cnv, text=str(load_dict["load_0"]))
l_label.pack()

for key in force_dict:
    label = Label(entry_cnv, text=key)
    entry = Entry(entry_cnv)
    force_dict[key].append(entry)
    label.pack(side=LEFT)
    entry.pack(side=RIGHT)
    print(label.cget("text"))
def calculate():
    print("got to calculate")
    for key in force_dict:
        magnitude = force_dict[key][2].get()
        force_dict[key][1] = magnitude
    main_cnv.update()
    print(force_dict)
calc = Button(root, text="Calculate", command=lambda: calculate())
calc.pack(side=BOTTOM)
mainloop()
