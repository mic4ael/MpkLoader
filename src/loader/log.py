#!/usr/bin/env python

import logging

_LOG_FILE = 'mpk_loader.log'

logger = logging.getLogger('MPKLoader')
logger.setLevel(logging.DEBUG)

_handler = logging.FileHandler(_LOG_FILE)
_handler.setLevel(logging.DEBUG)
_handler.setFormatter(logging.Formatter(
	'%(asctime)s [%(name)s][%(levelname)s] %(message)s'
))

logger.addHandler(_handler)