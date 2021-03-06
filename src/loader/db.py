#!/usr/bin/env python


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import INTEGER, VARCHAR, BIGINT, SMALLINT, TEXT
from sqlalchemy.ext.declarative import declarative_base

from .config import DB_CONFIG

_db_engine = create_engine('postgresql://{username}:{password}@{host}:{port}/{database}'.format(**DB_CONFIG))
_Session = sessionmaker(bind=_db_engine)
session = _Session(autocommit=False)

ModelBase = declarative_base()


class MpkLineModel(ModelBase):
    __tablename__ = 'mpk_lines'

    line_id = Column(BIGINT(), primary_key=True, nullable=False)
    line = Column(VARCHAR(length=10), nullable=False)
    type = Column(VARCHAR(length=20), nullable=False)


class MpkStopModel(ModelBase):
    __tablename__ = 'mpk_stops'

    id = Column(BIGINT(), primary_key=True, nullable=False)
    service_line_id = Column(INTEGER(), ForeignKey(MpkLineModel.line_id), nullable=False)
    stop_number = Column(INTEGER(), nullable=False)
    stop_street = Column(VARCHAR(length=200), nullable=False)
    timetable_id = Column(INTEGER(), nullable=False)
    direction = Column(SMALLINT(), nullable=False)


class MpkStopsConnection(ModelBase):
    __tablename__ = 'mpk_stops_connections'

    id = Column(BIGINT(), primary_key=True, nullable=False)
    src_stop = Column(BIGINT(), ForeignKey(MpkStopModel.id), nullable=False)
    dst_stop = Column(BIGINT(), ForeignKey(MpkStopModel.id), nullable=False)
    time = Column(INTEGER(), nullable=False, default=0)


class MpkTimetables(ModelBase):
    __tablename__ = 'mpk_timetables'

    id = Column(BIGINT(), primary_key=True, nullable=False)
    timetable_id = Column(INTEGER(), nullable=False)
    service_line_id = Column(INTEGER(), ForeignKey(MpkLineModel.line_id), nullable=False,)
    stop_id = Column(INTEGER(), ForeignKey(MpkStopModel.id), nullable=False)
    day_type = Column(TEXT(), nullable=False)
    timetable = Column(TEXT(), nullable=False)
