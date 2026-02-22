# 🌿 YOLO-LycheeNet (AI + Line Bot)

แชทบอทตรวจโรคลิ้นจี่ผ่านไลน์ ใช้สถาปัตยกรรม Hybrid (Node.js & Python) ขับเคลื่อนด้วย Google Gemini API

## 🏗 Architecture
- **Controller (Front):** Node.js + Express (จัดการ Line Webhook)
- **AI Service (Back):** Python + Flask (เชื่อมต่อ Gemini)
- **Model:** Gemini 1.5 Flash (Prompt Engineering for Agriculture)

## 🚀 How to Run

### 1. Clone Repo
git clone (https://github.com/thew-wuttiphat/rubber-disease-bot.git)

### 2. Setup AI Service (Python)
cd ai-service
pip install -r requirements.txt
cp .env.example .env
# (ใส่ค่า API Key ใน .env)
python app.py

### 3. Setup Bot Server (Node.js)
cd ../bot-server
npm install
cp .env.example .env
# (ใส่ค่า Line Token ใน .env)
node index.js
