"""
Ultralytics YOLO Detector Implementation
Supports YOLOv5, YOLOv8, YOLOv9, YOLOv10, YOLO11, YOLO12
"""

import os
from pathlib import Path

import cv2

try:
    from ultralytics import YOLO

    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    print("Warning: Ultralytics not installed. Install with: pip install ultralytics")

from detector_interface import DetectorInterface

# Available Ultralytics YOLO models organized by version and size
ULTRALYTICS_MODELS = {
    "YOLOv5": {
        "nano": "yolov5n.pt",
        "small": "yolov5s.pt",
        "medium": "yolov5m.pt",
        "large": "yolov5l.pt",
        "xlarge": "yolov5x.pt",
    },
    "YOLOv8": {
        "nano": "yolov8n.pt",
        "small": "yolov8s.pt",
        "medium": "yolov8m.pt",
        "large": "yolov8l.pt",
        "xlarge": "yolov8x.pt",
    },
    "YOLOv9": {
        "compact": "yolov9c.pt",
        "extended": "yolov9e.pt",
    },
    "YOLOv10": {
        "nano": "yolov10n.pt",
        "small": "yolov10s.pt",
        "medium": "yolov10m.pt",
        "balanced": "yolov10b.pt",
        "large": "yolov10l.pt",
        "xlarge": "yolov10x.pt",
    },
    "YOLO11": {
        "nano": "yolo11n.pt",
        "small": "yolo11s.pt",
        "medium": "yolo11m.pt",
        "large": "yolo11l.pt",
        "xlarge": "yolo11x.pt",
    },
    "YOLO12": {
        "nano": "yolo12n.pt",
        "small": "yolo12s.pt",
        "medium": "yolo12m.pt",
        "large": "yolo12l.pt",
        "xlarge": "yolo12x.pt",
    },
}

# Flat list of all Ultralytics models
ULTRALYTICS_MODELS_LIST = [
    "yolov5n.pt",
    "yolov5s.pt",
    "yolov5m.pt",
    "yolov5l.pt",
    "yolov5x.pt",
    "yolov8n.pt",
    "yolov8s.pt",
    "yolov8m.pt",
    "yolov8l.pt",
    "yolov8x.pt",
    "yolov9c.pt",
    "yolov9e.pt",
    "yolov10n.pt",
    "yolov10s.pt",
    "yolov10m.pt",
    "yolov10b.pt",
    "yolov10l.pt",
    "yolov10x.pt",
    "yolo11n.pt",
    "yolo11s.pt",
    "yolo11m.pt",
    "yolo11l.pt",
    "yolo11x.pt",
    "yolo12n.pt",
    "yolo12s.pt",
    "yolo12m.pt",
    "yolo12l.pt",
    "yolo12x.pt",
]

# Model size information
MODEL_SIZE_INFO = {
    "nano": {
        "speed": "Fastest",
        "accuracy": "Good",
        "params": "~3M",
        "description": "Ultra-lightweight model for edge devices and real-time applications. Best for mobile and embedded systems.",
    },
    "small": {
        "speed": "Very Fast",
        "accuracy": "Better",
        "params": "~11M",
        "description": "Balanced model offering good speed and accuracy. Suitable for most general-purpose applications.",
    },
    "medium": {
        "speed": "Fast",
        "accuracy": "Great",
        "params": "~25M",
        "description": "Mid-range model with excellent balance between performance and accuracy. Ideal for production systems.",
    },
    "balanced": {
        "speed": "Fast",
        "accuracy": "Great",
        "params": "~19M",
        "description": "Specially optimized variant (YOLOv10) providing efficient inference with strong detection capabilities.",
    },
    "large": {
        "speed": "Moderate",
        "accuracy": "Excellent",
        "params": "~43M",
        "description": "High-accuracy model for demanding applications. Requires more computational resources but delivers superior results.",
    },
    "xlarge": {
        "speed": "Slower",
        "accuracy": "Best",
        "params": "~68M",
        "description": "State-of-the-art model with maximum accuracy. Best for offline processing and high-precision requirements.",
    },
    "compact": {
        "speed": "Fast",
        "accuracy": "Great",
        "params": "~25M",
        "description": "YOLOv9 compact variant with improved architecture and efficient feature extraction.",
    },
    "extended": {
        "speed": "Moderate",
        "accuracy": "Excellent",
        "params": "~58M",
        "description": "YOLOv9 extended variant with enhanced detection capabilities and advanced feature fusion.",
    },
}

# Model version descriptions
ULTRALYTICS_VERSION_INFO = {
    "YOLOv5": {
        "description": "Classic and reliable YOLO version. Widely used, well-documented, and highly compatible with various platforms.",
        "release_year": "2020",
        "framework": "Ultralytics",
    },
    "YOLOv8": {
        "description": "Modern architecture with improved accuracy and speed. Offers better feature extraction and multi-scale detection.",
        "release_year": "2023",
        "framework": "Ultralytics",
    },
    "YOLOv9": {
        "description": "Advanced model with Programmable Gradient Information (PGI) and GELAN architecture for superior performance.",
        "release_year": "2024",
        "framework": "Ultralytics",
    },
    "YOLOv10": {
        "description": "End-to-end optimized model, eliminating NMS post-processing for faster inference.",
        "release_year": "2024",
        "framework": "Ultralytics",
    },
    "YOLO11": {
        "description": "Cutting-edge model with enhanced feature extraction and improved detection accuracy across all object sizes.",
        "release_year": "2024",
        "framework": "Ultralytics",
    },
    "YOLO12": {
        "description": "Attention-centric real-time detector (NeurIPS 2025). Advanced attention mechanisms with turbo optimization for improved speed and accuracy.",
        "release_year": "2025",
        "framework": "Ultralytics",
        "note": "Also available from third-party repo (sunsmarterjie) with optimized implementation",
    },
}


class UltralyticsDetector(DetectorInterface):
    """
    Ultralytics YOLO detector implementation
    Supports YOLOv5, YOLOv8, YOLOv9, YOLOv10, YOLO11, YOLO12
    """

    def __init__(
        self, model_name="yolo11x.pt", conf_threshold=0.25, filter_classes=None
    ):
        """
        Initialize Ultralytics YOLO detector

        Args:
            model_name: YOLO model name (e.g., 'yolo11x.pt', 'yolov8n.pt')
            conf_threshold: Confidence threshold for detection
            filter_classes: List of class IDs or names to filter detections (optional)
        """
        if not ULTRALYTICS_AVAILABLE:
            raise ImportError(
                "Ultralytics not installed. Install with: pip install ultralytics"
            )

        super().__init__(model_name, conf_threshold, filter_classes)

        print(f"Loading Ultralytics YOLO model: {model_name}")
        self.model = YOLO(model_name)
        print("Model loaded successfully!")

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
        print(f"Processing: {image_path}")

        # Run detection
        results = self.model.predict(
            source=image_path, conf=self.conf_threshold, save=False, verbose=True
        )

        # Get detections
        result = results[0]
        boxes = result.boxes

        print(f"Found {len(boxes)} detections")

        # Display or save
        if show or output_path:
            annotated = result.plot()

            if show:
                cv2.imshow("Detections", annotated)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            if output_path:
                cv2.imwrite(output_path, annotated)
                print(f"Saved to: {output_path}")

        return results

    def detect_batch(self, input_folder, output_folder, save_txt=False):
        """
        Run detection on all images in a folder

        Args:
            input_folder: Path to input images
            output_folder: Path to save annotated images
            save_txt: Save detection results as text files
        """
        # Create output directory
        os.makedirs(output_folder, exist_ok=True)

        # Get all image files
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
        image_files = []
        for ext in image_extensions:
            image_files.extend(Path(input_folder).glob(f"*{ext}"))
            image_files.extend(Path(input_folder).glob(f"*{ext.upper()}"))

        print(f"Found {len(image_files)} images to process")

        # Process images
        for i, img_path in enumerate(image_files, 1):
            print(f"Processing {i}/{len(image_files)}: {img_path.name}")

            # Run detection
            results = self.model.predict(
                source=str(img_path),
                conf=self.conf_threshold,
                save=False,
                verbose=False,
            )

            # Get detections
            result = results[0]
            boxes = result.boxes

            # Filter by class if specified
            if self.filter_classes and len(boxes) > 0:
                filtered_indices = []
                for idx, box in enumerate(boxes):
                    cls_id = int(box.cls[0])
                    if cls_id in self.filter_classes:
                        filtered_indices.append(idx)

                if filtered_indices:
                    boxes = [boxes[i] for i in filtered_indices]
                else:
                    boxes = []

            if len(boxes) > 0:
                print(f"  Found {len(boxes)} detections")

                # Save annotated image
                annotated = result.plot()
                output_path = os.path.join(output_folder, img_path.name)
                cv2.imwrite(output_path, annotated)

                # Save text file if requested
                if save_txt:
                    txt_path = os.path.join(output_folder, img_path.stem + ".txt")
                    with open(txt_path, "w") as f:
                        for box in boxes:
                            cls_id = int(box.cls[0])
                            conf = float(box.conf[0])
                            xyxy = box.xyxy[0].tolist()
                            f.write(
                                f"{cls_id} {conf:.4f} {xyxy[0]:.2f} {xyxy[1]:.2f} {xyxy[2]:.2f} {xyxy[3]:.2f}\n"
                            )
            else:
                print("  No detections found")

        print(f"\nDetection complete! Results saved to {output_folder}")

    @staticmethod
    def get_available_models():
        """Return dictionary of available models organized by version"""
        return ULTRALYTICS_MODELS

    @staticmethod
    def get_all_models_list():
        """Return flat list of all available model names"""
        return ULTRALYTICS_MODELS_LIST

    @staticmethod
    def get_model_info(size_key):
        """Get information about a model size"""
        return MODEL_SIZE_INFO.get(size_key, {})

    @staticmethod
    def get_version_info(version_key):
        """Get information about a model version"""
        return ULTRALYTICS_VERSION_INFO.get(version_key, {})
