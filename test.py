
import os
import tkinter as tk

from PIL import Image, ImageTk
from tkinter import Tk, Frame, Label, Listbox, Button, Canvas, Scrollbar, E, W, N, S, RIGHT, LEFT, TOP, BOTH, END, BOTTOM, X, Y, SUNKEN, HORIZONTAL, VERTICAL, BOTH, YES
from tkinter import filedialog
from win32api import GetSystemMetrics


CUR_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_HEIGHT = GetSystemMetrics(1)


mouse_btn1_down = False
drawing_box_x1, drawing_box_y1, drawing_box_x2, drawing_box_y2 = None, None, None, None


class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title('Testing the UI')
	
		scrollbar = Scrollbar(master)


		open_file_btn = Button(master, text="Open image", command=self.open_image)
		open_file_btn.grid(row=0, column=0, rowspan=10, columnspan=10, sticky=N)
		#
		
		scrollbar = Scrollbar(master)


		listbox = Listbox(master, yscrollcommand=scrollbar.set)
		for i in range(1000):
			listbox.insert(END, str(i))
		listbox.grid(row=11, column=0, rowspan=90, columnspan=9, sticky=N+S)
		scrollbar.grid(row=11, column=10, rowspan=90, sticky=N+S)

		scrollbar.config(command=listbox.yview)
		
		#
		#
		self.image_canvas = Canvas(master, width=1000, height=850, bg='white')
		self.image_canvas.config(scrollregion=(0,0,1000, 1000))
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox('all'))
		self.image_canvas.config(highlightthickness=0)

		sbarV = Scrollbar(master, orient=VERTICAL)
		sbarH = Scrollbar(master, orient=HORIZONTAL)

		sbarV.config(command=self.image_canvas.yview)
		sbarH.config(command=self.image_canvas.xview)

		self.image_canvas.config(yscrollcommand=sbarV.set)
		self.image_canvas.config(xscrollcommand=sbarH.set)
		
		sbarV.grid(row=0, column=13, rowspan=100, sticky=N+S)
		sbarH.grid(row=100, column=12, sticky=W+E)
		
		self.image_canvas.grid(row=0, column=12, rowspan=100)
		
		self.im=Image.open(os.path.join(CUR_DIR_PATH, 'asd.png'))
		width,height=self.im.size
		self.image_canvas.config(scrollregion=(0,0,width,height))
		self.im2=ImageTk.PhotoImage(self.im)
		self.imgtag=self.image_canvas.create_image(0,0,anchor="nw",image=self.im2)
		#
		
		
		#self.image_canvas.create_rectangle(0, 0, 100, 100, fill='red')
		
		#-----------------------		
		#load = Image.open(os.path.join(CUR_DIR_PATH, 'UI_look.png'))
		#render = ImageTk.PhotoImage(load)

		#img = Label(master, image=render)
		#img.image = render
		##img.place(x=0, y=0)
		#img.pack()
		
		#----------------
		
		self.label = Label(master, text="This is our first GUI!")
        # self.label.pack()

        self.greet_button = Button(master, text="Greet", command=self.greet)
        # self.greet_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        # self.close_button.pack()
        
        #self.label.pack(side=BOTTOM)
        #self.greet_button.pack()
        #self.close_button.pack()


    def greet(self):
        print("Greetings!")
		mouse.pack_forget()
		print(root.winfo_width())
		print(root.winfo_height())
	
	
	def open_image(self):
		file_path = filedialog.askopenfilename()
		print('file_path: ', file_path) # todo - remove
		
		self.im=Image.open(file_path)
		width,height=self.im.size
		self.image_canvas.config(scrollregion=(0,0,width,height))
		self.im2=ImageTk.PhotoImage(self.im)
		self.image_canvas.delete(self.imgtag)
		self.imgtag=self.image_canvas.create_image(0,0,anchor="nw",image=self.im2)


def mouse_motion(event):
    x_mouse_on_screen, y_mouse_on_screen = event.x_root, event.y_root
	x_window_location, y_window_location = root.winfo_x(), root.winfo_y()
	global drawing_box_x2, drawing_box_y2
	drawing_box_x2, drawing_box_y2 = (x_mouse_on_screen - x_window_location - 9), (y_mouse_on_screen - y_window_location - 31)
	print('x:{}, y:{}'.format(drawing_box_x2, drawing_box_y2))
	mouse.pack_forget()
	#mouse.place(x=x, y=y)
	global mouse_btn1_down
	if mouse_btn1_down:
		print('x1: {}, y1: {}, x2: {}, y2: {}'.format(drawing_box_x1, drawing_box_y1, drawing_box_x2, drawing_box_y2))
		global drawing_box_tmp
		try:
		  drawing_box_tmp
		except NameError:
			pass
		else:
			my_gui.image_canvas.delete(drawing_box_tmp)
		drawing_box_tmp = my_gui.image_canvas.create_rectangle(drawing_box_x1, drawing_box_y1, drawing_box_x2, drawing_box_y2, fill='red')


def click_mouse_btn1(event):
	global mouse_btn1_down
	mouse_btn1_down = True
	
    x_mouse_on_screen, y_mouse_on_screen = event.x_root, event.y_root
	x_window_location, y_window_location = root.winfo_x(), root.winfo_y()
	global drawing_box_x1, drawing_box_y1
	drawing_box_x1, drawing_box_y1 = (x_mouse_on_screen - x_window_location - 9), (y_mouse_on_screen - y_window_location - 31)
	print('x:{}, y:{}'.format(drawing_box_x1, drawing_box_y1))
	click.pack_forget()
	#click.place(x=x, y=y)


def release_mouse_btn1(event):
	global mouse_btn1_down
	mouse_btn1_down = False


root = Tk()
root.bind('<Motion>', mouse_motion)  # Setting the callback for mouse movement
root.bind('<Button-1>', click_mouse_btn1)
root.bind('<ButtonRelease-1>', release_mouse_btn1)
my_gui = MyFirstGUI(root)

mouse = Label(root, text='a')
click = Label(root, text='AAA')
root.mainloop()
