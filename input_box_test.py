
from tkinter import *


class InputBox(object):
    def __init__(self, widget, bnd_box_coords, labels):
        self.widget = widget
        self.input_box_window = None
        self.id = None
        self.x = self.y = 0
        self.labels = labels
        self.labels.sort()

        text = 'test'
        # Display text in tooltip window
        self.text = text
        if self.input_box_window or not self.text:
            return
        x, y, cx, cy = bnd_box_coords  # self.widget.bbox("insert")
        if x > cx:
            x, cx = cx, x
        if y > cy:
            y, cy = cy, y
        x += abs(x - cx)
        y += abs(y - cy)
        # x = x + self.widget.winfo_rootx() + 57
        # y = y + cy + self.widget.winfo_rooty() +27
        self.input_box_window = ibw = Toplevel(self.widget)
        ibw.wm_overrideredirect(1)
        ibw.wm_geometry('+{}+{}'.format(150, 150))
        #ibw.wm_geometry('+{}+{}'.format(150, 150))
        self.label = Label(ibw, text=self.text, justify=LEFT,
                           background="#ffffe0", relief=SOLID, borderwidth=1,
                           font=("tahoma", "8", "normal"))
        self.label.pack(ipadx=1)

        self.string_var = StringVar()
        self.string_var.set(self.labels[0])
        # self.string_var.trace("w", lambda name, index, mode, sv=sv: callback(sv))
        self.option_menu = OptionMenu(ibw, self.string_var, *self.labels)
        self.option_menu.pack(ipadx=1)
        self.input_box = Entry(ibw, textvariable=self.string_var)
        self.input_box.pack(ipadx=1)
        print('toast: ', text)  # todo - remove

    def input(self, callback):
        callback(self.string_var.get())

    def hide(self):
        ibw = self.input_box_window
        self.input_box_window = None
        if ibw:
            ibw.destroy()


def CreateInputBox(widget, bnd_box_coords, labels, callback):
    input_box = InputBox(widget, bnd_box_coords, labels)
    #input_box.input('test', bnd_box_coords)

    def return_(event):
        input_box.input(callback)

    def escape(event):
        input_box.hide()

    # widget.tag_bind(item_id, '<Enter>', enter)
    # widget.tag_bind(item_id, '<Leave>', leave)
    input_box.input_box.bind('<Return>', return_)
    input_box.input_box.bind('<Escape>', escape)

    return input_box
