#!/usr/bin/env python

from .utils import HtmlDownloader, MpkLinesExtractor, MpkStopsExtractor, MpkTimetableExtractor
from .config import MPK_URL, MPK_LINE_URL, MPK_TIMETABLE_URL
from .db import session, MpkLineModel, MpkStopModel, MpkStopsConnection
from .log import logger


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
            logger.debug('MPK Stops extracted for %s', details['line'])

        return stops

    def _store_stops_to_db(self):
        for mpk_line, details in self._bus_stops.iteritems():
            for direction, stops_data in details.iteritems():
                start_point = stops_data[0]
                start_point['direction'] = direction
                start_point['service_line_id'] = mpk_line
                self._load_mpk_connection(stops_data[0])
                for stop_data in stops_data:
                    stop_data['service_line_id'] = mpk_line
                    stop_data['direction'] = direction

                    if self._mpk_stop_already_exists(stop_data):
                        continue

                    logger.debug('Adding new bus stop with details %s', stop_data)

                    obj = MpkStopModel(
                        timetable_id=stop_data['timetable_id'],
                        stop_street=stop_data['stop_street'],
                        stop_number=stop_data['stop_number'],
                        service_line_id=mpk_line
                    )

                    session.add(obj)

        session.commit()

    def _mpk_stop_already_exists(self, mpk_stop):
        query = session.query(MpkStopModel).filter_by(
            stop_number=mpk_stop['stop_number'],
            service_line_id=mpk_stop['service_line_id']
        )

        return session.query(query.exists()).scalar()

    def _load_mpk_connection(self, mpk_stop):
        url = MPK_TIMETABLE_URL.format(
            direction=mpk_stop['direction'],
            line_id=mpk_stop['service_line_id'],
            timetable_id=mpk_stop['timetable_id'],
            stop_number=mpk_stop['stop_number']
        )
        html = self._downloader.download_html(url)
        extractor = MpkTimetableExtractor(html)
        self._save_connections_to_db(extractor.extract())

    def _save_connections_to_db(self, node):
        iter = node
        while iter is not None and iter.has_next():
            next = iter.next
            row = session.query(MpkStopsConnection).filter_by(
                src_stop=iter._stop_number,
                dst_stop=next._stop_number
            ).first()

            if row is not None:
                row.time = next.time
            else:
                row = MpkStopsConnection(
                    src_stop=iter._stop_number,
                    dst_stop=next._stop_number,
                    time=next.time
                )

            session.add(row)
            session.commit()
            iter = next

    def run(self):
        logger.debug('<<<< Starting MPKLoader >>>>')
        self._mpk_lines = self._get_all_lines()
        self._store_lines_to_db()
        self._bus_stops = self._get_all_stops()
        self._store_stops_to_db()
