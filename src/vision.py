import cv2
from ultralytics import YOLO

class BushXIVision:
    def __init__(self, model_name="yolov8n.pt"):
        self.model = YOLO(model_name)
        # Các vật thể robot dọn dẹp cần lưu tâm
        self.clean_targets = ["bottle", "cup", "chair", "couch", "dining table"]

    def process_frame(self, bgr_frame):
        """Quét ảnh và tìm kiếm mục tiêu dọn dẹp"""
        results = self.model(bgr_frame, stream=True)
        detected_objects = []

        for result in results:
            annotated_frame = result.plot()
            for box in result.boxes:
                label = self.model.names[int(box.cls)]
                if label in self.clean_targets:
                    x, y, w, h = box.xywh.tolist()[0]
                    detected_objects.append({
                        "label": label,
                        "center_2d": (x, y),
                        "bbox_size": (w, h)
                    })
        return annotated_frame, detected_objects
