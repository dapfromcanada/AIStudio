"""
Detector Factory
Creates the appropriate detector based on model selection
"""

try:
    from ultralytics_detector import ULTRALYTICS_AVAILABLE, UltralyticsDetector
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    UltralyticsDetector = None


class DetectorFactory:
    """
    Factory class to create the appropriate detector based on model type
    """

    @staticmethod
    def create_detector(model_name, conf_threshold=0.25, filter_classes=None):
        """
        Create and return the appropriate detector based on model name

        Args:
            model_name: Name or path of the model file
            conf_threshold: Confidence threshold for detection
            filter_classes: List of class IDs or names to filter

        Returns:
            DetectorInterface: Instance of appropriate detector class

        Raises:
            ValueError: If model type cannot be determined
            ImportError: If required framework is not installed
        """
        # Determine model type based on file extension and name
        if model_name.endswith(".pt"):
            # Ultralytics models (.pt files)
            if not ULTRALYTICS_AVAILABLE:
                raise ImportError(
                    "Ultralytics not installed. Install with:\npip install ultralytics"
                )
            return UltralyticsDetector(model_name, conf_threshold, filter_classes)
        else:
            raise ValueError(
                f"Unknown model type: {model_name}\n"
                f"Supported formats:\n"
                f"  - Ultralytics: .pt files (yolov5, yolov8, yolov9, yolov10, yolo11, yolo12)"
            )

    @staticmethod
    def get_all_available_models():
        """
        Get all available models from all frameworks

        Returns:
            dict: Dictionary with framework names as keys and model lists as values
        """
        all_models = {}

        if ULTRALYTICS_AVAILABLE:
            all_models["Ultralytics"] = UltralyticsDetector.get_available_models()

        return all_models

    @staticmethod
    def get_all_models_flat_list():
        """
        Get a flat list of all available models from all frameworks

        Returns:
            list: Flat list of all model filenames
        """
        models_list = []

        if ULTRALYTICS_AVAILABLE:
            models_list.extend(UltralyticsDetector.get_all_models_list())

        return models_list

    @staticmethod
    def get_framework_status():
        """
        Check which frameworks are available

        Returns:
            dict: Dictionary with framework availability status
        """
        return {
            "Ultralytics": ULTRALYTICS_AVAILABLE,
        }
