
import os
import tkinter as tk

from PIL import Image, ImageTk
from tkinter import Tk, Frame, Button, Canvas, Scrollbar, E, W, N, S, RIGHT, LEFT, TOP, BOTH, END, BOTTOM, X, Y, SUNKEN, HORIZONTAL, VERTICAL, BOTH, YES
from tkinter import filedialog
from win32api import GetSystemMetrics

# My scripts:
from get_bounding_boxes_from_prediction import get_predictions_from_image

from ToolTip import ToolTip, CreateToolTip


CUR_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_HEIGHT = GetSystemMetrics(1)

bounding_boxes_coords_list = []
visual_bounding_boxes_list = []
mouse_btn1_down = False
drawing_box_x1, drawing_box_y1, drawing_box_x2, drawing_box_y2 = None, None, None, None
drawing_box_tmp = None


class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title('Testing the UI')
	
		# SIDE PANEL
		# Action buttons
		scrollbar = Scrollbar(master)


		open_file_btn = Button(master, text="Open image", command=self.open_image)
		open_file_btn.grid(row=0, column=0, rowspan=10, columnspan=10, sticky=N)
		
		# Bounding boxes scroll list
		scrollbar = Scrollbar(master)


		listbox = tk.Listbox(master, yscrollcommand=scrollbar.set)
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
		self.image_canvas.bind('<Motion>', self.mouse_motion)  # Setting the callback for mouse movement
		self.image_canvas.bind('<Button-1>', self.click_mouse_btn1)
		self.image_canvas.bind('<Button-3>', self.click_mouse_btn3)
		self.image_canvas.bind('<ButtonRelease-1>', self.release_mouse_btn1)


    def greet(self):
        print("Greetings!")
		mouse.pack_forget()
		print(root.winfo_width())
		print(root.winfo_height())
	
	
	def open_image(self):
		global visual_bounding_boxes_list
		file_path = filedialog.askopenfilename()
		print('file_path: ', file_path) # todo - remove
		
		self.im=Image.open(file_path)
		width,height=self.im.size
		self.image_canvas.config(scrollregion=(0,0,width,height))
		self.im2=ImageTk.PhotoImage(self.im)
		self.image_canvas.delete(self.imgtag)
		self.imgtag=self.image_canvas.create_image(0,0,anchor="nw",image=self.im2)
		# Remove the previous drawn boxes
		for visual_bounding_box in visual_bounding_boxes_list:
			print('item: ')
			for item in visual_bounding_box:
				self.image_canvas.delete(item)
		visual_bounding_boxes_list = []

	def mouse_motion(self, event):
		global drawing_box_x2, drawing_box_y2
		drawing_box_x2, drawing_box_y2 = event.x, event.y
		print('x:{}, y:{}'.format(drawing_box_x2, drawing_box_y2))
		
		global mouse_btn1_down
		if mouse_btn1_down:
			print('x1: {}, y1: {}, x2: {}, y2: {}'.format(drawing_box_x1, drawing_box_y1, drawing_box_x2, drawing_box_y2))
			global drawing_box_tmp
			try:
			  len(drawing_box_tmp)
			except:
				pass
			else:
				if len(drawing_box_tmp) > 0:
					for item in drawing_box_tmp[:-1]:
						self.image_canvas.delete(item)
					del drawing_box_tmp[-1]
			drawing_box_tmp = create_rectangle(drawing_box_x1, drawing_box_y1, drawing_box_x2, drawing_box_y2, fill='red', alpha=.8)


	def click_mouse_btn1(self, event):
		global drawing_box_x1, drawing_box_y1, mouse_btn1_down
		mouse_btn1_down = True
		
		drawing_box_x1, drawing_box_y1 = event.x, event.y
		print('x:{}, y:{}'.format(drawing_box_x1, drawing_box_y1))


	def click_mouse_btn3(self, event):
		global visual_bounding_boxes_list
		if len(visual_bounding_boxes_list) > 0:
			for item in visual_bounding_boxes_list[0]:
				self.image_canvas.delete(item)
			del visual_bounding_boxes_list[0]
		print('right')


	def release_mouse_btn1(self, event):
		global mouse_btn1_down, bounding_boxes_coords_list, visual_bounding_boxes_list, drawing_box_tmp
		mouse_btn1_down = False
		bounding_boxes_coords_list.append([drawing_box_x1, drawing_box_y1, drawing_box_x2, drawing_box_y2])
		visual_bounding_boxes_list.append(drawing_box_tmp)
		del drawing_box_tmp
		for visual_bnd_box, bnd_box_coords in zip(visual_bounding_boxes_list, bounding_boxes_coords_list):
			print(visual_bnd_box)
			CreateToolTip(self.image_canvas, visual_bnd_box[0], bnd_box_coords, text = 'todo - label name') # todo - to be done


def create_rectangle(x1, y1, x2, y2, **kwargs):
	global alpha, fill, image, img, my_gui
	return_list = []
	alpha = 1.0
    if 'alpha' in kwargs:
        alpha = int(kwargs.pop('alpha') * 255)
	fill = kwargs.pop('fill')
	fill = root.winfo_rgb(fill) + (alpha,)
	image = Image.new('RGBA', (abs(x2 - x1), abs(y2 - y1)), fill)
	img = ImageTk.PhotoImage(image)
	#my_gui.image_canvas.create_image(min(x1, x2), min(y1, y2), image=img)
	return_list.append(my_gui.image_canvas.create_image(min(x1, x2), min(y1, y2), anchor='nw', image=img))
    return_list.append(my_gui.image_canvas.create_rectangle(x1, y1, x2, y2, **kwargs))
	return_list.append(img)
	return return_list


root = Tk()
my_gui = MyFirstGUI(root)

root.mainloop()
