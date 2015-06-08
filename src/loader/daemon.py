#!/usr/bin/env python

from .utils import HtmlDownloader, MpkLinesExtractor, MpkStopsExtractor
from .config import MPK_URL, MPK_LINE_URL
from .db import session, MpkLineModel, MpkStopModel
from .log import logger

from bs4 import BeautifulSoup as BS


class MpkLoader(object):

	def __init__(self):
		self._downloader = HtmlDownloader
		self._mpk_lines = None
		self._bus_stops = None

	def _get_all_lines(self):
		html = self._downloader.download_html(MPK_URL)
		extractor = MpkLinesExtractor(html)
		return extractor.extract()

	def _store_lines_to_db(self):
		for mpk_line, details in self._mpk_lines.iteritems():
			if session.query(MpkLineModel).get(mpk_line) is not None:
				logger.debug('MPK service %s row already exists', details['line'])
				continue

			logger.debug('MPK service: %s, Type: %s', details['line'], details['type'])
			obj = MpkLineModel(
				line=details['line'],
				type=details['type'],
				line_id=mpk_line
			)

			session.add(obj)

		session.commit()
		logger.debug('Storing to db successfully finished')

	def _get_all_stops(self):
		stops = {}
		for mpk_line, details in self._mpk_lines.iteritems():
			html = self._downloader.download_html(MPK_LINE_URL.format(lineId=mpk_line))
			extractor = MpkStopsExtractor(html)
			stops[mpk_line] = extractor.extract()
			logger.debug('MPK Stops extracted for service %s', details['line'])

		return stops

	def _store_stops_to_db(self):
		for mpk_line, details in self._bus_stops.iteritems():
			for direction, stops_data in details.iteritems():
				for stop_data in stops_data:

					logger.debug('Adding new bus stop with details %s', stop_data)

					obj = MpkStopModel(
						timetable_id=stop_data['timetable_id'],
						stop_street=stop_data['stop_street'],
						stop_number=stop_data['stop_number'],
						direction=direction,
						service_line_id=mpk_line
					)

					session.add(obj)

		session.commit()

	def run(self):
		logger.debug('<<<< Starting MPKLoader >>>>')
		self._mpk_lines = self._get_all_lines()
		self._store_lines_to_db()
		self._bus_stops = self._get_all_stops()
		self._store_stops_to_db()