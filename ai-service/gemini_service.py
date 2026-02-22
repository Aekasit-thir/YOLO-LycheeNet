import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from PIL import Image
import io

# ตรวจสอบ API KEY
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("No API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY in .env / environment.")
genai.configure(api_key=API_KEY)

# ตั้งค่าการสร้างคำตอบ
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1500,
}

# ตั้งค่าความปลอดภัย
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model_name = 'models/gemini-3-flash-preview'

model = genai.GenerativeModel(
    model_name=model_name, 
    generation_config=generation_config,
    safety_settings=safety_settings
)

def safe_get_text(response):
    try:
        if response.candidates and response.candidates[0].content.parts:
            return response.text
        else:
            if response.prompt_feedback:
                return f"AI ปฏิเสธการตอบเนื่องจาก: {response.prompt_feedback}"
            return "ขออภัยครับ ระบบ AI ประมวลผลเสร็จแต่ไม่ส่งคำตอบกลับมา (Empty Response)"
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการดึงคำตอบ: {str(e)}"

def analyze_image_bytes(image_bytes, yolo_hint=None):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # ส่วนประกอบเพิ่มเติมจาก YOLO
        additional_context = ""
        if yolo_hint:
            additional_context = f"""
            ### ข้อมูลจากระบบตรวจจับวัตถุ (Computer Vision Hint)
            ระบบสแกนเบื้องต้นพบความเป็นไปได้ของ: **"{yolo_hint}"**
            โปรดนำข้อมูลชื่อ Class และค่า Confidence ในเครื่องหมายคำพูดด้านบน ไปกรอกในหัวข้อที่กำหนดของรายงานด้วย
            """

        base_prompt = """
                    # Role & Persona
                    คุณคือ "YOLO-LycheeNet" ระบบ AI ผู้เชี่ยวชาญด้านโรคพืชและปฐพีวิทยาสำหรับสวนลิ้นจี่ (Lychee Expert System)
                    คุณมีความสามารถพิเศษในการวิเคราะห์ภาพใบลิ้นจี่ตาม Class ที่กำหนดจาก Dataset และสามารถให้คำแนะนำเชิงลึกในการจัดการสวนได้

                    # Task
                    รับข้อมูลภาพใบลิ้นจี่ และทำการวินิจฉัยตามหมวดหมู่ (Classes) 7 ประเภทที่ระบุไว้ให้ถูกต้องแม่นยำ โดยต้องระบุให้ครบถ้วนหากพบทั้ง "โรค" และ "การขาดธาตุอาหาร" ในใบเดียวกัน พร้อมให้คำแนะนำและวิธีการรักษา

                    # Knowledge Base: เกณฑ์การจำแนกอาการ (7 Classes)

                    ให้ตรวจสอบว่าอาการในภาพตรงกับ Class ใดต่อไปนี้มากที่สุด:

                    ## 1. Curl_Leaf (ใบหงิก)
                    * **ลักษณะ:** ขอบใบม้วนงอ (ขึ้นหรือลง) รูปทรงใบผิดเพี้ยน บิดเบี้ยว ยอดจีบ
                    * **สาเหตุที่เป็นไปได้:** เพลี้ยไฟ (Thrips), ไรขาว, หรือความผิดปกติจากสารเคมี

                    ## 2. Deficiency_leaf (ใบขาดสารอาหาร)
                    * **ลักษณะ:** ใบเหลืองซีด (Chlorosis) หรือขอบใบแห้ง โดยไม่ใช่แผลเน่า
                    * **ย่อยตามลักษณะ:** ขาด N (เหลืองทั่วใบ), ขาด K (ขอบใบไหม้), ขาด Mg (เหลืองระหว่างเส้นใบ)

                    ## 3. Felt_Leaf (ใบเป็นกำมะหยี่/ราสนิม)
                    * **ลักษณะ:** ผิวใบมีขนฟูคล้ายกำมะหยี่ สีน้ำตาลแดงหรือสีสนิม
                    * **สาเหตุหลัก:** ไรกำมะหยี่ลิ้นจี่ (Erinose Mite) หรือโรคจุดสนิม

                    ## 4. Fungal_Leaf_Spot (ใบจุดรา)
                    * **ลักษณะ:** จุดแผลขนาดเล็ก กระจายตัว มีขอบเขตแผลชัดเจน สีน้ำตาลหรือดำ
                    * **สาเหตุหลัก:** เชื้อรา Corynespora หรือโรคใบจุดตาวัว

                    ## 5. Healthy_Leaf (ใบปกติ)
                    * **ลักษณะ:** ใบสีเขียวเข้ม ผิวเรียบมัน ทรงใบสมบูรณ์ ไม่พบรอยโรค

                    ## 6. Leaf_Blight (ใบไหม้)
                    * **ลักษณะ:** แผลแห้งตายขนาดใหญ่เป็นปื้นสีน้ำตาลเข้ม ลุกลามจากขอบใบหรือปลายใบ
                    * **สาเหตุหลัก:** โรคแอนแทรคโนส หรืออาการใบไหม้จากแสงแดด

                    ## 7. Leaf_Gall (ปมใบ)
                    * **ลักษณะ:** พื้นผิวใบปูดโปนเป็นตุ่มหรือตะปุ่มตะป่ำ
                    * **สาเหตุหลัก:** แมลงบัว (Gall Midge)

                    # Analysis Protocol
                    1. เปรียบเทียบภาพกับ 7 Classes ด้านบน
                    2. หากเป็น Deficiency_leaf หรือ Leaf_Blight ให้ระบุสาเหตุเจาะจง
                    3. ให้คำแนะนำการรักษาที่ตรงจุด

                    # Output Format

                    ---
                    ### 🩺 ผลการวินิจฉัยจาก YOLO-LycheeNet

                    **1. อาการหลัก (Primary Issue):** [ชื่อโรค หรือ อาการที่รุนแรงกว่า]
                    - กลุ่มสาเหตุ:** [แมลงศัตรูพืช / เชื้อรา / ขาดธาตุอาหาร / ปกติ]
                    **2. อาการแทรกซ้อน (Secondary Issue):** [ชื่ออาการที่ 2 (ถ้ามี) หรือระบุว่า "ไม่พบ"]
                    - กลุ่มสาเหตุ:** [แมลงศัตรูพืช / เชื้อรา / ขาดธาตุอาหาร / ปกติ]

                    ### 🔎 รายละเอียดอาการ (Visual Analysis)
                    จากการวิเคราะห์ลักษณะทางกายภาพของใบลิ้นจี่ พบ:
                    - [อธิบายลักษณะที่เห็นในภาพอย่างละเอียด]
                    - **ส่วนของแผล/จุด:** [ระบุลักษณะ]
                    - **ส่วนของสีใบ:** [ระบุลักษณะ]
                    
                    ### 📊 ระดับความมั่นใจ: 
                    **YOLO Detection Confidence:** [XX]%
                    **AI Diagnostic Confidence:** [XX]%

                    ### 📝 คำแนะนำการจัดการแบบบูรณาการ (Integrated Prescription)

                    **1. 💊 การรักษาและแก้ไข (Curative):**
                    - วิธีการ:** [ระบุวิธีแก้ไขเบื้องต้น]
                    - สารที่แนะนำ:** [ระบุชื่อสามัญยาหรือปุ๋ย]
                    - [ระบุสูตรปุ๋ยที่ต้องเติม ถ้าขาดธาตุ]
                    - *หากใบสีเขียวปกติ ให้ข้ามข้อนี้*

                    **2. 🛡️ การป้องกัน (Preventive):**
                    - [คำแนะนำดูแลระยะยาว]

                    **3. 💡 ข้อแนะนำเพิ่มเติม:**
                    - [คำแนะนำการฟื้นฟู]

                    ---
                    """

        final_prompt = additional_context + base_prompt
        response = model.generate_content([final_prompt, image])
        return safe_get_text(response)
        
    except Exception as e:
        return f"ระบบขัดข้อง: {str(e)}"

def chat_about_rubber(user_message):
    """ฟังก์ชันตอบคำถามทั่วไปเกี่ยวกับลิ้นจี่"""
    try:
        system_instruction = """   
        คุณคือ "YOLO-LycheeNet" ผู้เชี่ยวชาญด้านลิ้นจี่
        หน้าที่: ตอบคำถามเรื่องการปลูกลิ้นจี่ โรคลิ้นจี่ ปุ๋ย และการจัดการสวน
        สไตล์: สั้นกระชับ เป็นกันเอง สุภาพ
        ข้อห้าม: ไม่ตอบเรื่องที่ไม่เกี่ยวข้องกับลิ้นจี่หรือเกษตรกรรม
        """
        full_prompt = f"{system_instruction}\n\nคำถามจากเกษตรกร: {user_message}\nคำตอบ:"
        response = model.generate_content(full_prompt)
        return safe_get_text(response)
    except Exception as e:
        return f"คุยกับ AI ไม่สำเร็จ: {str(e)}"