"""
Abstract base class for object detectors
All detector implementations must inherit from this interface
"""

from abc import ABC, abstractmethod


class DetectorInterface(ABC):
    """
    Abstract base class for object detectors
    All detector implementations (Ultralytics, Megvii, etc.) must inherit from this
    """

    def __init__(self, model_name, conf_threshold=0.25, filter_classes=None):
        """
        Initialize detector

        Args:
            model_name: Path or name of the model file
            conf_threshold: Confidence threshold for detection (0.0-1.0)
            filter_classes: List of class IDs or names to filter detections (optional)
        """
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        self.filter_classes = filter_classes

    @abstractmethod
    def detect_single(self, image_path, output_path=None, show=False):
        """
        Run detection on a single image

        Args:
            image_path: Path to input image
            output_path: Path to save annotated image (optional)
            show: Display image with detections

        Returns:
            Detection results
        """
        pass

    @abstractmethod
    def detect_batch(self, input_folder, output_folder, save_txt=False):
        """
        Run detection on all images in a folder

        Args:
            input_folder: Path to input images
            output_folder: Path to save annotated images
            save_txt: Save detection results as text files
        """
        pass

    @staticmethod
    @abstractmethod
    def get_available_models():
        """
        Return dictionary of available models organized by version

        Returns:
            dict: Model dictionary with versions and sizes
        """
        pass

    @staticmethod
    @abstractmethod
    def get_all_models_list():
        """
        Return flat list of all available model names

        Returns:
            list: List of model filenames
        """
        pass

    @staticmethod
    def get_model_info(size_key):
        """
        Get information about a model size (nano, small, medium, etc.)

        Args:
            size_key: Model size key (e.g., 'nano', 'small', 'xlarge')

        Returns:
            dict: Model size information
        """
        return {}

    @staticmethod
    def get_version_info(version_key):
        """
        Get information about a model version

        Args:
            version_key: Model version key (e.g., 'YOLOv8', 'YOLOv11')

        Returns:
            dict: Model version information
        """
        return {}
