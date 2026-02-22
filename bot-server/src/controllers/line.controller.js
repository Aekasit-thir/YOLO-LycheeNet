const fs = require('fs');
const path = require('path');
const lineService = require('../services/line.service');
const aiService = require('../services/ai.service');

const publicDir = path.join(__dirname, '../../public');
const imagesDir = path.join(publicDir, 'detected_images');

if (!fs.existsSync(publicDir)) fs.mkdirSync(publicDir);
if (!fs.existsSync(imagesDir)) fs.mkdirSync(imagesDir);

exports.callback = (req, res) => {
    res.sendStatus(200);
    const events = req.body.events;
    events.forEach(event => handleEvent(event));
};

async function handleEvent(event) {
    const userId = event.source.userId;
    const replyToken = event.replyToken;

    try {
        if (event.type === 'message' && event.message.type === 'image') {
            const imageStream = await lineService.getMessageContent(event.message.id);
            const aiResult = await aiService.analyzeImage(imageStream);
            const messages = [];

            if (aiResult.image_base64) {
                const fileName = `detected_${userId}_${Date.now()}.jpg`;
                const filePath = path.join(imagesDir, fileName);
                
                fs.writeFileSync(filePath, Buffer.from(aiResult.image_base64, 'base64'));
                
                const imageUrl = `${process.env.BASE_URL}/detected_images/${fileName}`;
                
                messages.push({
                    type: 'image',
                    originalContentUrl: imageUrl,
                    previewImageUrl: imageUrl
                });
            }

            if (aiResult.text) {
                messages.push({ type: 'text', text: aiResult.text });
            }

            if (messages.length > 0) {
                await lineService.pushMessage(userId, messages);
            }

        } else if (event.type === 'message' && event.message.type === 'text') {
            const userText = event.message.text;
            
            if (userText.length < 2) return;

            const replyText = await aiService.chatWithAI(userText);
            
            await lineService.reply(replyToken, { type: 'text', text: replyText });
        }

    } catch (error) {
        console.error('Processing Error:', error);
    }
}