
import os
import tkinter as tk

from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import font
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
drawing_box_x1, drawing_box_y1, drawing_box_x2, drawing_box_y2 = (None, None,
                                                                  None, None)
drawing_box_tmp = None


class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        self.width = SCREEN_WIDTH * .75
        self.height = SCREEN_HEIGHT * .75
        self.first_window_resize_counter = 0
        self.shift_down = False
        self.image_canvas_focused = False
        self.image_path, self.inference_graph_path, self.label_map_path = '', \
            '', ''

        master.title('Testing the UI')

        # SIDE PANEL
        # Action buttons
        buttons_font = font.Font(family='Arial', size=10)
        open_img_btn = tk.Button(master, text="Open\nimage",
                                 command=self.open_image,
                                 font=buttons_font)
        load_model_btn = tk.Button(master, text="Load\nmodel",
                                   command=self.load_inference_graph,
                                   font=buttons_font)
        load_label_map_btn = tk.Button(master, text="Load\nlabel map",
                                       command=self.load_label_map,
                                       font=buttons_font)
        predict_btn = tk.Button(master, text="Predict",
                                command=self.predict,
                                font=buttons_font)
        open_img_btn.grid(row=0, column=0, rowspan=5,
                          columnspan=5)
        load_model_btn.grid(row=0, column=5, rowspan=5,
                            columnspan=5)
        load_label_map_btn.grid(row=5, column=3, rowspan=5,
                                columnspan=7)
        predict_btn.grid(row=5, column=0, rowspan=5,
                         columnspan=5)

        # Scroll list for bounding boxes coordinates and predictions
        self.listbox_scrollbar = tk.Scrollbar(master)

        self.listbox = tk.Listbox(master,
                                  yscrollcommand=self.listbox_scrollbar.set)
        for i in range(1000):
            self.listbox.insert(tk.END, str(i))
        self.listbox.grid(row=11, column=0, rowspan=90,
                          columnspan=9, sticky=tk.N + tk.S)
        self.listbox_scrollbar.grid(row=11,
                                    column=10,
                                    rowspan=90,
                                    sticky=tk.N + tk.S)
        self.listbox_scrollbar.config(command=self.listbox.yview)

        #
        #
        img_canvas_width, img_canvas_height = (
            self.width - self.listbox.winfo_width() -
            self.listbox_scrollbar.winfo_width() - 17,
            self.height - 17)
        self.image_canvas = tk.Canvas(master,
                                      width=img_canvas_width,
                                      height=img_canvas_height,
                                      bg='white')
        print(self.image_canvas.bbox('all'))
        # self.image_canvas.config(scrollregion=(0, 0, 1000, 1000))
        # self.image_canvas.configure(scrollregion=self.image_canvas.bbox('all'))
        self.image_canvas.config(highlightthickness=0)  # Canvas margin

        sbarV = tk.Scrollbar(master, orient=tk.VERTICAL)
        sbarH = tk.Scrollbar(master, orient=tk.HORIZONTAL)

        sbarV.config(command=self.image_canvas.yview)
        sbarH.config(command=self.image_canvas.xview)

        self.image_canvas.config(yscrollcommand=sbarV.set)
        self.image_canvas.config(xscrollcommand=sbarH.set)

        sbarV.grid(row=0, column=13, rowspan=100, sticky=tk.N + tk.S)
        sbarH.grid(row=100, column=12, sticky=tk.W + tk.E)

        self.image_canvas.grid(row=0, column=12, rowspan=100)

        self.im = Image.open(os.path.join(CUR_DIR_PATH, 'asd.png'))
        width, height = self.im.size
        self.image_canvas.config(scrollregion=(0, 0, width, height))
        self.im2 = ImageTk.PhotoImage(self.im)
        self.imgtag = self.image_canvas.create_image(
            0, 0, anchor="nw", image=self.im2)
        #

        # Setting the callback for mouse movement
        self.master.bind("<Configure>", self.on_resize_window)
        self.master.bind('<KeyPress>', self.key_down)
        self.master.bind("<KeyRelease>", self.key_up)

        self.image_canvas.bind('<Enter>', self.image_canvas_entered)
        self.image_canvas.bind('<Leave>', self.image_canvas_left)
        self.image_canvas.bind('<Motion>', self.mouse_motion)
        self.image_canvas.bind('<Button-1>', self.click_mouse_btn1)
        self.image_canvas.bind('<Button-3>', self.click_mouse_btn3)
        self.image_canvas.bind('<ButtonRelease-1>', self.release_mouse_btn1)
        self.image_canvas.bind_all('<MouseWheel>', self.mouse_wheel)
        # self.image_canvas.bind_all('<Key>', self.key_event)

    def on_resize_window(self, event):
        if self.first_window_resize_counter > 10:
            if (self.width != self.master.winfo_width() or
                    self.height != self.master.winfo_height()):
                img_canvas_width, img_canvas_height = (
                    self.master.winfo_width() - self.listbox.winfo_width() -
                    self.listbox_scrollbar.winfo_width() - 17,
                    self.master.winfo_height() - 17)
                self.image_canvas.config(width=img_canvas_width,
                                         height=img_canvas_height)
                print(self.width, self.height)  # todo - remove
        else:
            self.first_window_resize_counter += 1
        self.width = self.master.winfo_width()
        self.height = self.master.winfo_height()

    def open_image(self):
        global visual_bounding_boxes_list
        file_path = filedialog.askopenfilename(
            filetypes=[
                ('Image files',  '.jpg .jpeg .png .bmp .gif .ppm .tiff')],
            title='Open image')

        if len(file_path) > 0:
            self.image_path = file_path
            print('image_path: ', self.image_path)  # todo - remove
            self.im = Image.open(self.image_path)
            width, height = self.im.size
            self.image_canvas.config(scrollregion=(0, 0, width, height))
            self.im2 = ImageTk.PhotoImage(self.im)
            self.image_canvas.delete(self.imgtag)
            self.imgtag = self.image_canvas.create_image(
                0, 0, anchor="nw", image=self.im2)
            # Remove the previous drawn boxes
            for visual_bounding_box in visual_bounding_boxes_list:
                for item in visual_bounding_box:
                    self.image_canvas.delete(item)
            visual_bounding_boxes_list = []

    def load_inference_graph(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('PB Files', '.pb')],
            title='Load frozen inference graph')
        if len(file_path) > 0:
            self.inference_graph_path = file_path

    def load_label_map(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('PBTXT Files', '.pbtxt')],
            title='Load label map')
        if len(file_path) > 0:
            self.label_map_path = file_path

    def predict(self):
        if (len(self.image_path) > 0 and
            len(self.inference_graph_path) > 0 and
                len(self.label_map_path) > 0):
            global predictions_dict
            img_to_predict_on = Image.open(self.image_path)
            predictions_dict = get_predictions_from_image(
                self.inference_graph_path,
                self.label_map_path,
                img_to_predict_on)
            plot_predictions(predictions_dict)

    def image_canvas_entered(self, event):
        self.image_canvas_focused = True

    def image_canvas_left(self, event):
        self.image_canvas_focused = False

    def mouse_motion(self, event):
        global drawing_box_x2, drawing_box_y2
        drawing_box_x2, drawing_box_y2 = event.x, event.y
        print('x:{}, y:{}'.format(drawing_box_x2, drawing_box_y2))

        global mouse_btn1_down
        if mouse_btn1_down:
            print('x1: {}, y1: {}, x2: {}, y2: {}'.format(
                drawing_box_x1, drawing_box_y1,
                drawing_box_x2, drawing_box_y2))
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
            drawing_box_tmp = create_rectangle(
                drawing_box_x1, drawing_box_y1,
                drawing_box_x2, drawing_box_y2, fill='red', alpha=.8)

    def click_mouse_btn1(self, event):
        global drawing_box_x1, drawing_box_y1, mouse_btn1_down
        mouse_btn1_down = True

        drawing_box_x1, drawing_box_y1 = event.x, event.y
        print('x:{}, y:{}'.format(drawing_box_x1, drawing_box_y1))

    def click_mouse_btn3(self, event):
        global visual_bounding_boxes_list
        if len(visual_bounding_boxes_list) > 0:
            for item_to_remove in visual_bounding_boxes_list[0][:-1]:
                self.image_canvas.delete(item_to_remove)
            item_to_remove = visual_bounding_boxes_list[0][-1].tipwindow
            if item_to_remove is not None:
                item_to_remove.destroy()
            del visual_bounding_boxes_list[0]
        print('right')

    def release_mouse_btn1(self, event):
        global mouse_btn1_down, bounding_boxes_coords_list, \
            visual_bounding_boxes_list, drawing_box_tmp
        mouse_btn1_down = False
        try:
            drawing_box_tmp
        except NameError:
            pass
        else:
            bounding_boxes_coords_list.append(
                [drawing_box_x1, drawing_box_y1,
                 drawing_box_x2, drawing_box_y2])
            visual_bounding_boxes_list.append(drawing_box_tmp)
            drawing_box_tmp.append(CreateToolTip(
                self.image_canvas, drawing_box_tmp[0],
                bounding_boxes_coords_list[-1], text='todo - label name ' +
                str(drawing_box_tmp[0])))
            # todo - to be done
            del drawing_box_tmp

    def mouse_wheel(self, event):
        if self.image_canvas_focused:
            if self.shift_down:
                self.image_canvas.xview_scroll(int(-1 * (event.delta / 120)),
                                               'units')
            else:
                self.image_canvas.yview_scroll(int(-1 * (event.delta / 120)),
                                               'units')

    def key_down(self, event):
        print('key_down: ', event.keysym)
        if event.keysym[:5] == 'Shift':
            self.shift_down = True

    def key_up(self, event):
        print('key_up: ', event.keysym)
        if event.keysym[:5] == 'Shift':
            self.shift_down = False


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
    # my_gui.image_canvas.create_image(min(x1, x2), min(y1, y2), image=img)
    return_list.append(my_gui.image_canvas.create_image(
        min(x1, x2), min(y1, y2), anchor='nw', image=img))
    return_list.append(my_gui.image_canvas.create_rectangle(
        x1, y1, x2, y2, **kwargs))
    return_list.append(img)
    return return_list


def plot_predictions(predictions_dict: dict):  # todo - to be done
    ...


root = tk.Tk()
my_gui = MyFirstGUI(root)

root.mainloop()
