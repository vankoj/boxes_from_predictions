
import os
import itertools
import tkinter as tk

from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import font
from win32api import GetSystemMetrics
from threading import Thread

# Custom scripts:
from get_bounding_boxes_from_prediction import get_predictions_from_image
from ToolTip import ToolTip, CreateToolTip


CUR_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_HEIGHT = GetSystemMetrics(1)

bounding_boxes_coords_list = []
visual_bounding_boxes_list = []
all_labels_list = []
predictions_dict = {}
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
        self.image, self.img_width, self.img_height = None, None, None
        self.img_tag = None

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

        # WORKSPACE
        # Canvas for the opened image
        img_canvas_width, img_canvas_height = (
            self.width - self.listbox.winfo_width() -
            self.listbox_scrollbar.winfo_width() - 17,
            self.height - 17)
        self.image_canvas = tk.Canvas(master,
                                      width=img_canvas_width,
                                      height=img_canvas_height,
                                      bg='white')
        self.image_canvas.config(highlightthickness=0)  # Canvas margin

        vertical_scroll_bar = tk.Scrollbar(master, orient=tk.VERTICAL)
        horizontal_scroll_bar = tk.Scrollbar(master, orient=tk.HORIZONTAL)

        vertical_scroll_bar.config(command=self.image_canvas.yview)
        horizontal_scroll_bar.config(command=self.image_canvas.xview)

        self.image_canvas.config(yscrollcommand=vertical_scroll_bar.set)
        self.image_canvas.config(xscrollcommand=horizontal_scroll_bar.set)

        vertical_scroll_bar.grid(row=0, column=13,
                                 rowspan=100, sticky=tk.N + tk.S)
        horizontal_scroll_bar.grid(row=100, column=12,
                                   sticky=tk.W + tk.E)

        self.image_canvas.grid(row=0, column=12, rowspan=100)

        # todo - pick up initial image
        self.open_image(os.path.join(CUR_DIR_PATH, 'asd.png'))

        # Setting move/resize event callback
        self.master.bind("<Configure>", self.on_resize_window)
        # Setting keyboard keys event callbacks
        self.master.bind('<KeyPress>', self.key_down)
        self.master.bind("<KeyRelease>", self.key_up)
        # Setting enter and leave callbacks for the canvas
        self.image_canvas.bind('<Enter>', self.image_canvas_entered)
        self.image_canvas.bind('<Leave>', self.image_canvas_left)
        # Setting mouse event callbacks
        self.image_canvas.bind('<Motion>', self.mouse_motion)
        self.image_canvas.bind('<Button-1>', self.click_mouse_btn1)
        self.image_canvas.bind('<Button-3>', self.click_mouse_btn3)
        self.image_canvas.bind('<ButtonRelease-1>', self.release_mouse_btn1)
        self.image_canvas.bind_all('<MouseWheel>', self.mouse_wheel)

    def click(self, evt):
        x, y = self.image_canvas.canvasx(
            evt.x), self.image_canvas.canvasy(evt.y)
        self.image_canvas.create_oval(x - 5, y - 5, x + 5, y + 5)

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
        else:
            self.first_window_resize_counter += 1
        self.width = self.master.winfo_width()
        self.height = self.master.winfo_height()

    def open_image(self, file_path=None):
        global visual_bounding_boxes_list
        if file_path is None:
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ('Image files',  '.jpg .jpeg .png .bmp .gif .ppm .tiff')],
                title='Open image')

        if len(file_path) > 0:
            self.image_path = file_path
            self.image = Image.open(self.image_path)
            # Get the image dimensions
            self.img_width, self.img_height = self.image.size
            self.image_canvas.config(scrollregion=(0, 0,
                                                   self.img_width,
                                                   self.img_height))
            self.im2 = ImageTk.PhotoImage(self.image)
            self.image_canvas.delete(self.img_tag)
            self.img_tag = self.image_canvas.create_image(
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
        global all_labels_list
        file_path = filedialog.askopenfilename(
            filetypes=[('PBTXT Files', '.pbtxt')],
            title='Load label map')
        if len(file_path) > 0:
            self.label_map_path = file_path
            all_labels_list = read_label_map(self.label_map_path)

    def predict(self):
        # predictions_dict = {
        #     'detection_boxes':   [[.1, .1, .2, .5]],
        #     'detection_classes': [20],
        #     'detection_scores':  [.92]
        # }
        # plot_predictions(predictions_dict)
        if (len(self.image_path) > 0 and
            len(self.inference_graph_path) > 0 and
                len(self.label_map_path) > 0):
            global predictions_dict
            prediction_thread = Thread(target=predict_thread,
                                       args=(predictions_dict, ))
            prediction_thread.start()

    def image_canvas_entered(self, event):
        self.image_canvas_focused = True

    def image_canvas_left(self, event):
        self.image_canvas_focused = False

    def mouse_motion(self, event):
        global drawing_box_x2, drawing_box_y2
        x, y = (int(self.image_canvas.canvasx(event.x)),
                int(self.image_canvas.canvasy(event.y)))
        print('x:{}, y:{}'.format(x, y))

        global mouse_btn1_down
        if mouse_btn1_down:
            drawing_box_x2, drawing_box_y2 = \
                max(0, min(x, self.img_width)), \
                max(0, min(y, self.img_height))

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
                drawing_box_x2, drawing_box_y2,
                fill='red', alpha=.8)

    def click_mouse_btn1(self, event):
        global drawing_box_x1, drawing_box_y1, mouse_btn1_down
        mouse_btn1_down = True

        drawing_box_x1, drawing_box_y1 = \
            int(self.image_canvas.canvasx(event.x)), \
            int(self.image_canvas.canvasy(event.y))
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
            len(drawing_box_tmp)
        except:
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
    global my_gui
    return_list = []
    alpha = 1
    if 'alpha' in kwargs:
        alpha = int(kwargs.pop('alpha') * 255)
    fill = kwargs.pop('fill')
    fill = root.winfo_rgb(fill) + (alpha,)
    _image_ = Image.new('RGBA', (abs(x2 - x1), abs(y2 - y1)), fill)
    _img_ = ImageTk.PhotoImage(_image_)
    # my_gui.image_canvas.create_image(min(x1, x2), min(y1, y2), image=img)
    return_list.append(my_gui.image_canvas.create_image(
        min(x1, x2), min(y1, y2), anchor='nw', image=_img_))
    return_list.append(my_gui.image_canvas.create_rectangle(
        x1, y1, x2, y2, **kwargs))
    return_list.append(_img_)
    return return_list


def predict_thread(predictions_dict: dict, min_score_thresh=.5):
    img_to_predict_on = Image.open(my_gui.image_path)
    predictions_dict = get_predictions_from_image(
        frozen_inference_graph_path=my_gui.inference_graph_path,
        label_map_path=my_gui.label_map_path,
        img_to_predict_on=img_to_predict_on)
    plot_predictions(predictions_dict=predictions_dict, min_score_thresh=.5)


def plot_predictions(predictions_dict: dict, min_score_thresh=.5):
    global bounding_boxes_coords_list, visual_bounding_boxes_list, \
        detection_classes_list, detection_scores_list, all_labels_list, my_gui
    # Remove the previous drawn boxes
    for visual_bounding_box in visual_bounding_boxes_list:
        for item in visual_bounding_box:
            my_gui.image_canvas.delete(item)
    visual_bounding_boxes_list = []
    # Copy the contents of the dictionary
    bounding_boxes_coords_list = list(
        predictions_dict['detection_boxes'].copy())
    detection_classes_list = list(
        predictions_dict['detection_classes'].copy())
    detection_scores_list = list(
        predictions_dict['detection_scores'].copy())
    # Drawing each predicted box with score > min_score_thresh
    for iterator, (bnd_box, class_, score) in \
        enumerate(
            zip(bounding_boxes_coords_list,
                detection_classes_list,
                detection_scores_list)):
        if score > min_score_thresh:
            bnd_box[0] = int(bnd_box[0] * my_gui.img_height)
            bnd_box[1] = int(bnd_box[1] * my_gui.img_width)
            bnd_box[2] = int(bnd_box[2] * my_gui.img_height)
            bnd_box[3] = int(bnd_box[3] * my_gui.img_width)
            drawing_box_tmp = create_rectangle(
                bnd_box[1], bnd_box[0],
                bnd_box[3], bnd_box[2],
                fill='red', alpha=.8)
            drawing_box_tmp.append(CreateToolTip(
                widget=my_gui.image_canvas,
                item_id=drawing_box_tmp[0],
                bnd_box_coords=bnd_box,
                text=all_labels_list[class_ - 1]
            ))
            visual_bounding_boxes_list.append(drawing_box_tmp)


def read_label_map(label_map_path: str):
    prefix = 'display_name: '

    with open(label_map_path) as file:
        lines = [line.strip() for line in file]  # Sroring each line in a list
    items = [list(itertools.islice(lines[i:i+5], 5))  # Each item in a list
             for i in range(0, len(lines), 5)]
    # Each line with 'display_name'
    classes = [item[3] for item in items]
    classes = [_class[len(prefix):] for _class in classes if _class.startswith(
        prefix)]  # Each class name with quotes
    # Each class name in a list
    classes = [_class.strip('\"') for _class in classes]

    return classes  # Return a list with the classes names


root = tk.Tk()
my_gui = MyFirstGUI(root)

root.mainloop()
