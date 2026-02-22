import os
import io
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image

# ================= PATH =================

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'best.onnx')

# =======================================

try:
    model = YOLO(model_path, task='detect')
    print(f"✅ YOLO Model loaded: {model_path}")
except Exception as e:
    print(f"❌ Failed to load YOLO model: {e}")
    model = None

# =======================================

def detect_disease(image_bytes):
    if model is None:
        return None, None

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        results = model(
            img,
            imgsz=640,
            conf=0.25,      # ปรับลด
            iou=0.45,
            device='cpu',
            verbose=True
        )

        detected_info = []

        if results and results[0].boxes is not None and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls_id]
                detected_info.append(f"{class_name} ({conf*100:.2f}%)")

        disease_text = ", ".join(detected_info) if detected_info else "ไม่พบโรค"

        annotated_frame = results[0].plot(
            labels=True,
            boxes=True,
            line_width=2,
            font_size=1.0
        )

        annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        final_image = Image.fromarray(annotated_rgb)

        output_buffer = io.BytesIO()
        final_image.save(output_buffer, format='JPEG', quality=95)

        return output_buffer.getvalue(), disease_text

    except Exception as e:
        print(f"⚠️ YOLO Error: {e}")
        return None, None