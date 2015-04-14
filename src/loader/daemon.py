#!/usr/bin/env python

from .utils import HtmlDownloader, MpkLinesExtractor, MpkStopsExtractor
from .config import MPK_URL, MPK_LINE_URL

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

	def _get_all_stops(self):
		stops = {}
		for mpk_line in self._mpk_lines:
			html = self._downloader.download_html(MPK_LINE_URL.format(lineId=mpk_line))
			extractor = MpkStopsExtractor(html)
			stops[mpk_line] = extractor.extract()

		return stops

	def run(self):
		self._mpk_lines = self._get_all_lines()
		self._bus_stops = self._get_all_stops()