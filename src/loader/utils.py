#!/usr/bin/env python


from bs4 import BeautifulSoup as BS
from .config import LANG, LINEID_REGEX, STOP_REGEX, TIMETABLE_REGEX
from .log import logger

import requests
import re


class HtmlDownloader(object):

    session = requests.Session()

    @classmethod
    def get(cls, url):
        headers = {
            'Accept-Language': LANG
        }

        return cls.session.get(url, timeout=10, headers=headers)

    @classmethod
    def download_html(cls, url):
        def prepare_html(html):
            html = re.sub(' {2,}', '', html)
            return html

        ret_value = prepare_html(cls.get(url).text)
        logger.debug('Downloading finished')
        return ret_value


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

                    tmp = tr.find('td')
                    if tmp:
                        if tmp.text.strip():
                            stop_street = tmp.text.strip() + " - " + link.text.strip()
                        else:
                            stop_street = link.text.strip()
                    else:
                        stop_street = link.text.strip()

                    if direction not in stops:
                        stops[direction] = []

                    stops[direction].append({
                        'timetable_id': timetable_id,
                        'stop_street': stop_street,
                        'stop_number': stop_number
                    })

        return stops


class MpkStopConnectionsExtractor(Extractor):

    STYLE_FOR_VISIBLE_DIV = 'visibility: visible'

    def extract(self):
        timetables = self._html_tree.find_all('div', class_='timeSet')
        for timetable in timetables:
            if timetable.has_attr('style') and self.STYLE_FOR_VISIBLE_DIV in timetable['style']:
                schedule_table = timetable.find_next('table')
                self._find_root(schedule_table)
                return self._parse_schedule_table(schedule_table.find_next('table'))

    def _find_root(self, table):
        td = table.find('td')
        link = td.find('a')['href']
        line_id, stop_number = self._parse_url_for_data(link)
        self._root_node = Node(next_=None, time_=0, stop_number=stop_number, mpk_line_id=line_id)

    def _parse_schedule_table(self, table):
        table_data = table.find_all('td')
        prev_node = self._root_node
        time_total = 0
        for td in table_data:
            prev_node = self._parse_single_data_row(td, prev_node, time_total)
            time_total += prev_node.time_in_minutes

        return self._root_node

    def _parse_single_data_row(self, td, previous, time_total):
        link = td.find('a')['href']
        mpk_line_id, stop_number = self._parse_url_for_data(link)
        time_value = td.find('span').text.strip()
        time_value = int(re.sub(r'[^\d]', '', time_value)) - time_total
        next_node = Node(None, time_value, mpk_line_id, stop_number)
        previous.next = next_node
        return next_node

    def _parse_url_for_data(self, link):
        return re.search(TIMETABLE_REGEX, link).groups()


class MpkTimetablesExtractor(Extractor):

    def extract(self):
        day_types = self._html_tree.find_all('div', class_='dayType')
        day_types_dict = self._get_day_types()
        result = {}
        for day_type in day_types:
            id = day_types_dict[int(day_type['id'][-2:])]
            timetable_trs = day_type.find('div', class_='tableDayType').find_all('tr')
            for tr in timetable_trs:
                hour = int(tr.find('th').text.strip())
                minutes = [re.sub(r'\D*', '', minute.text.strip()) for minute in tr.find_all('a', class_='minute')]
                if id not in result:
                    result[id] = {hour: minutes}
                else:
                    result[id].update({hour: minutes})

        return result

    def _get_day_types(self):
        day_types = self._html_tree.find('div', id='dDayTypeNames').find_all('a')
        result = {}
        for item in day_types:
            result[int(item['id'][-2:])] = item.text.strip()
        return result


class Node(object):

    def __init__(self, next_=None, time_=0, mpk_line_id=None, stop_number=None):
        self._next = next_
        self._time = time_
        self._mpk_line_id = mpk_line_id
        self._stop_number = stop_number

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value):
        self._next = value

    @property
    def mpk_line_id(self):
        return self._mpk_line_id

    @mpk_line_id.setter
    def mpk_line_setter(self, value):
        self._mpk_line_id = value

    @property
    def time_in_seconds(self):
        return self._time * 60

    @property
    def time_in_minutes(self):
        return self._time

    @property
    def stop_number(self):
        return self._stop_number

    def has_next(self):
        return self._next is not None

    def __str__(self):
        return 'Time: {time}, Line: {line}, Stop: {stop}'.format(
            time=self._time,
            line=self._mpk_line_id,
            stop=self._stop_number
        )
