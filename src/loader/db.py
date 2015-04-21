#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import SMALLINT, INTEGER, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

from .config import DB_CONFIG

db_engine = create_engine('sqlite:///loader.db')
Session = sessionmaker(bind=db_engine)
session = Session(autocommit=False)

ModelBase = declarative_base()


class BusLine(ModelBase):
	__tablename__ = 'bus_lines'

	line_id = Column('line_id', INTEGER(), primary_key=True, nullable=False)
	line = Column('line', VARCHAR(length=10), nullable=False)
	type = Column('type', VARCHAR(length=20), nullable=False)


class BusStop(ModelBase):
	__tablename__ = 'bus_stops'

	id = Column(INTEGER(), primary_key=True, nullable=False)
	stop_number = Column('stop_number', INTEGER(), nullable=False)
	line_id = Column('line_id', ForeignKey(BusLine.line_id))
	stop_name = Column('stop_name', VARCHAR(length=200), nullable=False)
	timetable_id = Column('timetable_id', INTEGER())
	direction = Column('direction', SMALLINT())


class BusStopsConnection(ModelBase):
	__tablename__ = 'bus_stops_connections'

	id = Column(INTEGER(), primary_key=True, nullable=False)
	src_bus_stop = Column(INTEGER(), ForeignKey(BusStop.stop_number), nullable=False)
	dst_bus_stop = Column(INTEGER(), ForeignKey(BusStop.stop_number), nullable=False)
	time = Column(INTEGER(), nullable=False, default=0)