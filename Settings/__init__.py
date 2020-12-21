from os.path import isfile
from tkinter import *
from pathlib import Path

window = Tk()

txt_msg_broken_cfg = 'RenderPipeline plugins configuration is broken. \n' \
                     'Click OK to quit'
cli_msg_broken_cfg = 'RenderPipeline plugins configuration is broken. Exiting...'

# Gets the requested values of the height and widht.
width = window.winfo_reqwidth()
height = window.winfo_reqheight()

# Gets both half the screen width/height and window width/height
pos_right = int(window.winfo_screenwidth() / 2 - width / 2)
pos_down = int(window.winfo_screenheight() / 2 - height / 2)

game_dir = str(Path.cwd())
error_img = "{0}/Settings/UI/ui_tex/korlan_logo_tengri_sm.png".format(game_dir)


def msg_box_error():
    if isfile(error_img):
        window.title("Korlan: Daughter of the Steppes")
        window.geometry('540x150')
        # Positions the window in the center of the page.
        window.geometry("+{}+{}".format(pos_right, pos_down))
        window.configure(bg='black')
        window.resizable(0, 0)

        img = PhotoImage(file=error_img)

        canvas = Canvas(window, width=70, height=43)
        canvas.create_image((0, 0), image=img, anchor=NW)
        canvas.place(x=30, y=30)

        lbl = Label(window, text=txt_msg_broken_cfg, font=("Open Sans", 12))
        lbl.config(anchor=CENTER)
        lbl.configure(bg='black', fg='white')
        lbl.place(x=120, y=30)

        btn = Button(window, text="OK", width=6, height=1,
                     bg="black", fg="white", command=window.destroy)
        btn.place(x=250, y=90)

        window.mainloop()
