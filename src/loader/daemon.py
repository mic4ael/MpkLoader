#!/usr/bin/env python

from .utils import HtmlDownloader, MpkLinesExtractor, MpkStopsExtractor
from .config import MPK_URL, MPK_LINE_URL
from .db import session, BusLine, BusStop
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
			if session.query(BusLine).get(mpk_line) is not None:
				logger.debug('Busline with id %r is already in the database', mpk_line)
				continue

			logger.debug('MPK Line: %r, Details: %s', mpk_line, details)
			obj = BusLine(
				line=details['line'],
				type=details['type'],
				line_id=mpk_line
			)

			session.add(obj)

		session.commit()
		logger.debug('Storing to db successfully finished')

	def _get_all_stops(self):
		stops = {}
		for mpk_line in self._mpk_lines:
			html = self._downloader.download_html(MPK_LINE_URL.format(lineId=mpk_line))
			extractor = MpkStopsExtractor(html)
			stops[mpk_line] = extractor.extract()

		return stops

	def _store_stops_to_db(self):
		for mpk_line, details in self._bus_stops.iteritems():
			for direction, stops_data in details.iteritems():
				for bus_data in stops_data:
					logger.debug('Adding new bus stop for line %s, details %s', mpk_line, bus_data)

					obj = BusStop(
						direction=direction,
						line_id=mpk_line,
						timetable_id=bus_data['timetable_id'],
						stop_name=bus_data['stop_name'],
						stop_number=bus_data['stop_number']
					)

					session.add(obj)

		session.commit()

	def run(self):
		logger.debug('<<<< Starting MPKLoader >>>>')
		self._mpk_lines = self._get_all_lines()
		self._store_lines_to_db()
		self._bus_stops = self._get_all_stops()
		self._store_stops_to_db()