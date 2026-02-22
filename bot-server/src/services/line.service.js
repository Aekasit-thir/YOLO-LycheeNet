const line = require('@line/bot-sdk');
require('dotenv').config();

const config = {
    channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN,
    channelSecret: process.env.CHANNEL_SECRET
};

const client = new line.Client(config);

exports.middleware = line.middleware(config);

exports.reply = (token, messages) => {
    const msgs = Array.isArray(messages) ? messages : [messages];
    return client.replyMessage(token, msgs);
};

exports.pushMessage = (userId, messages) => {
    const msgs = Array.isArray(messages) ? messages : [messages];
    return client.pushMessage(userId, msgs);
};

exports.getMessageContent = (messageId) => {
    return client.getMessageContent(messageId);
};