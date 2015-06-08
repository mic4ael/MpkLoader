#!/usr/bin/env python

from bs4 import BeautifulSoup as BS
from .config import LANG, LINEID_REGEX, STOP_REGEX

import requests
import re

def get(url):
	headers = {
		'Accept-Language': LANG,
		'Connection': 'close'
	}

	return requests.get(url, headers=headers)


class HtmlDownloader(object):

	@classmethod
	def download_html(cls, url):
		def prepare_html(html):
			html = re.sub(' {2,}', '', html)
			return html

		return prepare_html(get(url).text)


class Extractor(object):

	def __init__(self, html):
		self._html_tree = BS(html, "lxml")

	def extract(self, **kwargs):
		raise NotImplemented


class MpkLinesExtractor(Extractor):

	def extract(self):
		mpk_lines = {}
		divs = self._html_tree.find_all('div', class_='dLines')
		for div in divs:
			vehicle_type = div.find_next('th').text.strip()
			for link in div.find_next('td').find_all('a'):
				line_id = re.search(LINEID_REGEX, link['href']).group(1)
				mpk_lines[line_id] = {
					'line': link.text.strip(),
					'type': vehicle_type
				}

		return mpk_lines


class MpkStopsExtractor(Extractor):

	def extract(self):
		stops = {}
		for t in self._html_tree.find_all('td', class_='transfers'):
			t.extract()

		tds = self._html_tree.find('div', id='dRoute').find_all('td', class_='version')
		for td in tds:
			trs = td.find_all('tr')
			for tr in trs:
				links = tr.find_all('a')
				for link in links:
					result = re.search(STOP_REGEX, link['href'])
					direction, timetable_id, stop_number = result.groups()
					stop_street = link.text.strip()
					if direction not in stops:
						stops[direction] = []

					stops[direction].append({
						'timetable_id': timetable_id,
						'stop_street': stop_street,
						'stop_number': stop_number
					})

		return stops