require('dotenv').config();
const express = require('express');
const path = require('path');
const lineRoutes = require('./src/routes/line.routes');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));
app.use('/', lineRoutes);

app.listen(PORT, () => {
    console.log(`Node.js Server is running on port ${PORT}`);
});