#!/usr/bin/env python

import json

from .utils import HtmlDownloader, MpkLinesExtractor, MpkStopsExtractor, MpkStopConnectionsExtractor, MpkTimetablesExtractor
from .config import MPK_URL, MPK_LINE_URL, MPK_TIMETABLE_URL
from .db import session, MpkLineModel, MpkStopModel, MpkStopsConnection, MpkTimetables
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

    def _get_all_stops(self):
        stops = {}
        for mpk_line, details in self._mpk_lines.iteritems():
            logger.debug('Extracting stops for %r', mpk_line)
            try:
                html = self._downloader.download_html(MPK_LINE_URL.format(lineId=mpk_line))
                extractor = MpkStopsExtractor(html)
                stops[mpk_line] = extractor.extract()
                logger.debug('MPK Stops extracted for %s', details['line'])
            except:
                logger.debug('Exception occurred')

        return stops

    def _store_stops_to_db(self):
        starting_stops = []
        for mpk_line, details in self._bus_stops.iteritems():
            for direction, stops_data in details.iteritems():
                start_point = stops_data[0]
                start_point['direction'] = direction
                start_point['service_line_id'] = mpk_line
                starting_stops.append(stops_data[0])
                for stop_data in stops_data:
                    stop_data['service_line_id'] = mpk_line
                    stop_data['direction'] = direction
                    html = self._get_stop_html(stop_data)

                    if self._mpk_stop_already_exists(stop_data):
                        logger.debug('Stop already exists')
                        continue

                    logger.debug('Adding new bus stop with details %s', stop_data)

                    obj = MpkStopModel(
                        timetable_id=stop_data['timetable_id'],
                        stop_street=stop_data['stop_street'],
                        stop_number=stop_data['stop_number'],
                        service_line_id=mpk_line,
                        direction=stop_data['direction']
                    )

                    session.add(obj)
                    session.commit()
                    if int(stop_data['direction']) == 1:
                        self._load_and_save_stop_timetable(html, stop_data)

        for conn_data in starting_stops:
            self._load_mpk_connection(html, conn_data)

    def _get_stop_html(self, mpk_stop):
        url = MPK_TIMETABLE_URL.format(
            direction=mpk_stop['direction'],
            line_id=mpk_stop['service_line_id'],
            timetable_id=mpk_stop['timetable_id'],
            stop_number=mpk_stop['stop_number']
        )
        logger.debug('Downloading html for stop')
        return self._downloader.download_html(url)

    def _mpk_stop_already_exists(self, mpk_stop):
        query = session.query(MpkStopModel).filter_by(
            stop_number=mpk_stop['stop_number'],
            service_line_id=mpk_stop['service_line_id'],
            direction=mpk_stop['direction']
        )

        return session.query(query.exists()).scalar()

    def _load_and_save_stop_timetable(self, html, mpk_stop):
        extractor = MpkTimetablesExtractor(html)
        self._save_timetables_to_db(extractor.extract(), mpk_stop)
        logger.debug('Saving timetables finished')

    def _load_mpk_connection(self, html, mpk_stop):
        extractor = MpkStopConnectionsExtractor(html)
        self._save_connections_to_db(extractor.extract())
        logger.debug('Loading mpk connections finished')

    def _save_connections_to_db(self, node):
        curr_node = node
        while curr_node is not None and curr_node.has_next():
            next_node = curr_node.next
            logger.info('Curr node: %s, next node: %s', curr_node, next_node)
            src_stop = session.query(MpkStopModel).filter_by(
                stop_number=curr_node.stop_number,
                service_line_id=curr_node.mpk_line_id
            ).first()
            dst_stop = session.query(MpkStopModel).filter_by(
                stop_number=next_node.stop_number,
                service_line_id=next_node.mpk_line_id
            ).first()

            if src_stop is not None and dst_stop is not None:
                row = session.query(MpkStopsConnection).filter_by(
                    src_stop=src_stop.id,
                    dst_stop=dst_stop.id
                ).first()

                if row is not None:
                    row.time = next_node.time_in_seconds
                else:
                    row = MpkStopsConnection(
                        src_stop=src_stop.id,
                        dst_stop=dst_stop.id,
                        time=next_node.time_in_seconds
                    )

                session.add(row)
                session.commit()

            curr_node = next_node

    def _save_timetables_to_db(self, data, mpk_stop):
        logger.debug('Saving timetable for %r', mpk_stop['stop_number'])
        stop_row = session.query(MpkStopModel).filter_by(
            stop_number=mpk_stop['stop_number'],
            service_line_id=mpk_stop['service_line_id']
        ).first()
        session.commit()
        logger.debug('Found Stop: %r', stop_row)
        for day_type, entry in data.iteritems():
            row_from_db = session.query(MpkTimetables).filter_by(
                timetable_id=mpk_stop['timetable_id'],
                service_line_id=mpk_stop['service_line_id'],
                stop_id=stop_row.id,
                day_type=day_type
            ).first()
            session.commit()

            logger.debug('Row from db: %r', row_from_db)
            if row_from_db:
                row_from_db.timetable = json.dumps(entry)
                session.add(row_from_db)
            else:
                row = MpkTimetables(
                    timetable_id=mpk_stop['timetable_id'],
                    service_line_id=mpk_stop['service_line_id'],
                    stop_id=stop_row.id,
                    day_type=day_type,
                    timetable=json.dumps(entry),
                )

                session.add(row)
            logger.debug('Commiting a timetable')
            session.commit()

    def run(self):
        logger.debug('<<<< Starting MPKLoader >>>>')
        self._mpk_lines = self._get_all_lines()
        self._store_lines_to_db()
        self._bus_stops = self._get_all_stops()
        self._store_stops_to_db()
