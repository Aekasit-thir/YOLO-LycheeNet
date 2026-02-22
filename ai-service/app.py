import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import base64
from dotenv import load_dotenv

# 1. โหลด .env ก่อนเสมอ เพื่อให้ API Key เข้าสู่ระบบก่อนเรียกใช้ gemini_service
load_dotenv() 

from flask import Flask, request, jsonify
import gemini_service
import yolo_service # ในไฟล์นี้คุณต้องแก้เป็น task='segment' และ plot(masks=True) แล้ว

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    try:
        image_file = request.files['image']
        image_bytes = image_file.read()

        # 2. เรียกใช้ YOLO (ซึ่งตอนนี้เป็นโมเดล Polygon/Segment)
        # yolo_image_bytes ที่ได้มาตอนนี้จะเป็นรูปที่มี "การระบายสีทับรอยโรค" (Mask) แทนกรอบสี่เหลี่ยม
        yolo_image_bytes, detected_disease_name = yolo_service.detect_disease(image_bytes)

        # 3. ส่งข้อมูลให้ Gemini วิเคราะห์คำแนะนำการรักษา
        # ส่ง yolo_hint เพื่อให้ AI รู้ว่า YOLO ตรวจเจอโรคอะไรเบื้องต้น
        gemini_text = gemini_service.analyze_image_bytes(image_bytes, yolo_hint=detected_disease_name)
        
        response_data = {
            'text': gemini_text,
            'image_base64': None
        }

        # 4. จัดการรูปภาพที่จะแสดงผลบนหน้าเว็บ
        if yolo_image_bytes:
            # ใช้รูปที่วาด Polygon (Segmentation) แล้ว
            img_b64_str = base64.b64encode(yolo_image_bytes).decode('utf-8')
            response_data['image_base64'] = img_b64_str
        else:
            # กรณีตรวจไม่พบ ให้ส่งรูปต้นฉบับกลับไป
            img_b64_str = base64.b64encode(image_bytes).decode('utf-8')
            response_data['image_base64'] = img_b64_str

        return jsonify(response_data)

    except Exception as e:
        print(f"❌ Analyze Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
        
    user_message = data['message']
    
    # --- จุดที่แก้ไข: เปลี่ยนชื่อฟังก์ชันให้เป็นเรื่องลิ้นจี่ตามที่เทรนไว้ ---
    # ตรวจสอบชื่อฟังก์ชันใน gemini_service.py ด้วยว่าชื่อ chat_about_lychee หรือไม่
    try:
        reply = gemini_service.chat_about_lychee(user_message)
    except AttributeError:
        # กรณีคุณยังไม่ได้เปลี่ยนชื่อฟังก์ชันใน gemini_service
        reply = gemini_service.chat_about_rubber(user_message)
        
    return jsonify({'reply': reply})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("✅ LITCHI-CARE-TH (Polygon Mode) Ready!")
    print("🚀 API Running on http://localhost:5001")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)