const axios = require('axios');
const FormData = require('form-data');
require('dotenv').config();

const analyzeImage = async (imageStream) => {
    try {
        const form = new FormData();
        form.append('image', imageStream, { filename: 'image.jpg' });

        const response = await axios.post(process.env.PYTHON_API_URL, form, {
            headers: { ...form.getHeaders() },
            maxContentLength: Infinity,
            maxBodyLength: Infinity
        });

        return response.data; 
    } catch (error) {
        console.error("AI Image Service Error:", error.message);
        return { 
            text: "ระบบวิเคราะห์ภาพขัดข้องชั่วคราว", 
            image_base64: null 
        };
    }
};

const chatWithAI = async (message) => {
    try {
        const chatUrl = process.env.PYTHON_API_URL.replace('/analyze', '/chat');
        const response = await axios.post(chatUrl, { message: message });
        return response.data.reply;
    } catch (error) {
        console.error("AI Chat Service Error:", error.message);
        return "ขออภัย ระบบขัดข้องชั่วคราว";
    }
};

module.exports = { analyzeImage, chatWithAI };