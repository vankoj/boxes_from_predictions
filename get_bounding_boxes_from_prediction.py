# %% md

# Object Detection Demo
# Welcome to the object detection inference walkthrough!  This notebook will walk you step by step through the process of using a pre-trained model to detect objects in an image. Make sure to follow the [installation instructions](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md) before you start.

# %% md

# Imports

# %%

import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
from object_detection.utils import ops as utils_ops

if StrictVersion(tf.__version__) < StrictVersion('1.12.0'):
  raise ImportError('Please upgrade your TensorFlow installation to v1.12.*.')


#%% md

## Env setup

#%%

# This is needed to display the images.
#%matplotlib inline

#%% md

## Object detection imports
#Here are the imports from the object detection module.

#%%

from utils import label_map_util

from utils import visualization_utils as vis_util

#%% md

# Model preparation 

CUR_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

#%% md

## Variables

#Any model exported using the `export_inference_graph.py` tool can be loaded here simply by changing `PATH_TO_FROZEN_GRAPH` to point to a new .pb file.  

#By default we use an "SSD with Mobilenet" model here. See the [detection model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) for a list of other models that can be run out-of-the-box with varying speeds and accuracies.

#%%


def get_predictions_from_image(frozen_inference_graph_path: str, label_map_path: str, img_to_predict_on):
	# Path to frozen detection graph. This is the actual model that is used for the object detection.
	PATH_TO_FROZEN_GRAPH = frozen_inference_graph_path #= os.path.join(MODEL_NAME, 'frozen_inference_graph.pb')

	# List of the strings that is used to add correct label for each box.
	PATH_TO_LABELS = label_map_path #= os.path.join('training', MODEL_PATH, 'label_map.pbtxt')

	#%% md

	## Load a (frozen) Tensorflow model into memory.

	#%%

	detection_graph = tf.Graph()
	with detection_graph.as_default():
		od_graph_def = tf.GraphDef()
		with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
			serialized_graph = fid.read()
			od_graph_def.ParseFromString(serialized_graph)
			tf.import_graph_def(od_graph_def, name='')

	#%% md

	## Loading label map
	#Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

	#%%

	category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

	#%% md

	## Helper code

	#%%

	def load_image_into_numpy_array(image):
	  (im_width, im_height) = image.size
	  return np.array(image.getdata()).reshape(
		  (im_height, im_width, 3)).astype(np.uint8)

	#%% md

	# Detection

	#%%

	#PATH_TO_OUTPUT_IMAGES_DIR = os.path.join(CUR_DIR_PATH, 'output_images')

	#if not os.path.exists(PATH_TO_OUTPUT_IMAGES_DIR):
	#	os.makedirs(PATH_TO_OUTPUT_IMAGES_DIR)

	# Size, in inches, of the output images.
	#IMAGE_SIZE = (60, 40)

	#%%

	def run_inference_for_single_image(image, graph):
		with graph.as_default():
			with tf.Session() as sess:
			  # Get handles to input and output tensors
			  ops = tf.get_default_graph().get_operations()
			  all_tensor_names = {output.name for op in ops for output in op.outputs}
			  tensor_dict = {}
			  for key in [
				  'num_detections', 'detection_boxes', 'detection_scores',
				  'detection_classes', 'detection_masks'
			  ]:
			    tensor_name = key + ':0'
			    if tensor_name in all_tensor_names:
			      tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
					  tensor_name)
			  if 'detection_masks' in tensor_dict:
				# The following processing is only for single image
			    detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
			    detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
				# Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
			    real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
			    detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
			    detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
			    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
					detection_masks, detection_boxes, image.shape[1], image.shape[2])
			    detection_masks_reframed = tf.cast(
					tf.greater(detection_masks_reframed, 0.5), tf.uint8)
				# Follow the convention by adding back the batch dimension
			    tensor_dict['detection_masks'] = tf.expand_dims(
					detection_masks_reframed, 0)
			  image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

			  # Run inference
			  output_dict = sess.run(tensor_dict,
									 feed_dict={image_tensor: image})

			  # all outputs are float32 numpy arrays, so convert types as appropriate
			  output_dict['num_detections'] = int(output_dict['num_detections'][0])
			  output_dict['detection_classes'] = output_dict[
				  'detection_classes'][0].astype(np.int64)
			  output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
			  output_dict['detection_scores'] = output_dict['detection_scores'][0]
			  if 'detection_masks' in output_dict:
			    output_dict['detection_masks'] = output_dict['detection_masks'][0]
		return output_dict

	#%%

	image_np = load_image_into_numpy_array(img_to_predict_on)
	# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
	image_np_expanded = np.expand_dims(image_np, axis=0)
	# Actual detection.
	output_dict = run_inference_for_single_image(image_np_expanded, detection_graph)
	#vis_util.visualize_boxes_and_labels_on_image_array(
	#	image_np,
	#    output_dict['detection_boxes'],
	#    output_dict['detection_classes'],
	#    output_dict['detection_scores'],
	#    category_index,
	#    instance_masks=output_dict.get('detection_masks'),
	#    use_normalized_coordinates=True,
	#    line_thickness=8)
	#plt.figure(figsize=IMAGE_SIZE)
	#plt.imshow(image_np)
	#plt.savefig(os.path.join(PATH_TO_OUTPUT_IMAGES_DIR, 'predicted.jpg'), bbox_inches='tight')
			
	

	print('Exported successfully!')
	return output_dict

	#%%

# Example call:
#print(get_predictions_from_image(os.path.join(CUR_DIR_PATH, 'my_model', 'frozen_inference_graph.pb'), os.path.join(CUR_DIR_PATH, 'my_model', 'label_map.pbtxt'), Image.open(os.path.join(CUR_DIR_PATH, 'predict.jpg'))))

