const express = require('express');
const router = express.Router();
const lineController = require('../controllers/line.controller');
const lineService = require('../services/line.service');

router.post('/callback', lineService.middleware, lineController.callback);

module.exports = router;