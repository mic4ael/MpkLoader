#!/usr/bin/env python

import logging

_LOG_FILE = 'mpk_loader.log'
_SQL_LOG_FILE = 'sql.log'

logger = logging.getLogger('MPKLoader')
logger.setLevel(logging.DEBUG)

_handler = logging.FileHandler(_LOG_FILE)
_handler.setLevel(logging.DEBUG)
_handler.setFormatter(logging.Formatter(
	'%(asctime)s [%(name)s][%(levelname)s] %(message)s'
))

logger.addHandler(_handler)

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(logging.Formatter(
	'%(asctime)s [%(name)s][%(levelname)s] %(message)s'
))

logger.addHandler(_console_handler)

_sql_logger = logging.getLogger('sqlalchemy.engine')
_sql_logger.setLevel(logging.INFO)

_sql_file_handler = logging.FileHandler(_SQL_LOG_FILE)
_sql_file_handler.setLevel(logging.DEBUG)
_sql_file_handler.setFormatter(logging.Formatter(
	'%(asctime)s [%(name)s][%(levelname)s] %(message)s'
))

_sql_logger.addHandler(_sql_file_handler)
