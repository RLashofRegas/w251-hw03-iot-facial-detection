"""Classes for neural face detector implementation."""
import numpy as np
import tensorflow as tf
from PIL import Image
from typing import Tuple, Union, List, Dict
from .face_detector import IFaceDetector


class NeuralFaceDetector(IFaceDetector):
    """Uses a pretrained neural network to detect faces."""

    def __init__(
            self, graph_path: str, input_size: Tuple[int, int],
            detection_threshold: float = 0.5) -> None:
        """Initialize the classifier."""
        self.input_x = input_size[0]
        self.input_y = input_size[1]
        self.tf_graph = tf.compat.v1.GraphDef()
        with open(graph_path, 'rb') as graph:
            self.tf_graph.ParseFromString(graph.read())
        self.tf_config = tf.compat.v1.ConfigProto()
        self.tf_config.gpu_options.allow_growth = True
        self.tf_session = tf.compat.v1.Session(config=self.tf_config)
        tf.import_graph_def(self.tf_graph, name='')
        self.tf_input: tf.Tensor = self.tf_session.graph.get_tensor_by_name(
            'image_tensor:0')
        self.tf_scores = self.tf_session.graph.get_tensor_by_name(
            'detection_scores:0')
        self.tf_boxes = self.tf_session.graph.get_tensor_by_name(
            'detection_boxes:0')
        self.tf_classes = self.tf_session.graph.get_tensor_by_name(
            'detection_classes:0')
        self.tf_num_detections = self.tf_session.graph.get_tensor_by_name(
            'num_detections:0')
        self.detection_threshold = detection_threshold

    def __del__(self) -> None:
        """Release Tensorflow resources."""
        self.tf_session.close()

    def get_faces(self, image: Union[np.ndarray, str]) -> List[List[int]]:
        """
        Return faces for an image.

        Args:
            image: image to classify.
                Either an image as an ndarray or path to an image on disk.

        Returns:
            array of tuples for coordinates of faces (x, y, w, h)
        """
        pillow_image: Image
        if(isinstance(image, str)):
            pillow_image = Image.open(image)
        else:
            pillow_image = Image.fromarray(image)
        processed_image = self._preprocess_image(pillow_image)
        boxes = self._get_faces_from_network(processed_image)
        np_image: np.ndarray = np.array(pillow_image)
        scaler = np.array(
            [np_image.shape[0],
             np_image.shape[1],
             np_image.shape[0],
             np_image.shape[1]])
        scaled_boxes: List[List[int]] = [box * scaler for box in boxes]
        return [[box[1], box[0], box[3] - box[1], box[2] - box[0]]
                for box in scaled_boxes]

    def _get_faces_from_network(self, image: np.ndarray) -> List[np.ndarray]:
        feed_dict: Dict[tf.Tensor, np.ndarray] = {
            self.tf_input: image[None, ...]
        }
        scores, boxes_batch, classes, num_detections = self.tf_session.run(
            [self.tf_scores, self.tf_boxes, self.tf_classes, self.
             tf_num_detections],
            feed_dict=feed_dict)
        # index by 0 to remove batch dimension
        boxes: List[np.ndarray] = [box for box, score in zip(
            boxes_batch[0], scores[0]) if score >= self.detection_threshold]
        return boxes

    def _preprocess_image(self, pillow_image: Image) -> np.ndarray:
        resized_image = np.array(
            pillow_image.resize(
                (self.input_x, self.input_y)))
        return resized_image
