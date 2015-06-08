#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import SMALLINT, INTEGER, VARCHAR, SMALLINT, BIGINT
from sqlalchemy.ext.declarative import declarative_base

from .config import DB_CONFIG

_db_engine = create_engine('sqlite:///loader.db')
_Session = sessionmaker(bind=_db_engine)
session = _Session(autocommit=False)

ModelBase = declarative_base()


class MpkLineModel(ModelBase):
	__tablename__ = 'mpk_lines'

	line_id = Column('line_id', INTEGER(), primary_key=True, nullable=False)
	line = Column('line', VARCHAR(length=10), nullable=False)
	type = Column('type', VARCHAR(length=20), nullable=False)


class MpkStopModel(ModelBase):
	__tablename__ = 'mpk_stops'

	id = Column(BIGINT(), primary_key=True, nullable=False)
	service_line_id = Column(INTEGER(), ForeignKey(MpkLineModel.line_id), nullable=False)
	stop_number = Column('stop_number', INTEGER(), nullable=False)
	stop_street = Column('stop_street', VARCHAR(length=200), nullable=False)
	timetable_id = Column('timetable_id', INTEGER(), nullable=False)
	direction = Column('direction', SMALLINT(), nullable=False)


class MpkStopsConnection(ModelBase):
	__tablename__ = 'mpk_stops_connections'

	id = Column(INTEGER(), primary_key=True, nullable=False)
	src_stop = Column(INTEGER(), ForeignKey(MpkStopModel.id), nullable=False)
	dst_stop = Column(INTEGER(), ForeignKey(MpkStopModel.id), nullable=False)
	time = Column(INTEGER(), nullable=False, default=0)
