
from tkinter import *


class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.label = None

    def showtip(self, text):
        # Display text in tooltip window
        self.text = text
        if self.tipwindow or not self.text:
            return
        # x, y, cx, cy = bnd_box_coords  # self.widget.bbox("insert")
        # if x > cx:
        #     x, cx = cx, x
        # if y > cy:
        #     y, cy = cy, y
        # x += abs(x - cx)
        # y += abs(y - cy)
        # x = x + self.widget.winfo_rootx() + 57
        # y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (self.x + 10, self.y + 10))
        self.label = Label(tw, text=self.text, justify=LEFT,
                           background="#ffffe0", relief=SOLID, borderwidth=1,
                           font=("tahoma", "8", "normal"))
        self.label.pack(ipadx=1)
        print('toast: ', text)  # todo - remove

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def CreateToolTip(master, widget, item_id, bnd_box_coords, text):  # todo - remove bnd box
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()

    def mouse_motion(event):
        toolTip.x, toolTip.y = master.winfo_pointerx(), master.winfo_pointery()

    master.bind('<Motion>', mouse_motion)
    widget.tag_bind(item_id, '<Enter>', enter)
    widget.tag_bind(item_id, '<Leave>', leave)

    return toolTip
