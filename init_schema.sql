CREATE TABLE mpk_lines
(
  line_id serial NOT NULL,
  type text NOT NULL,
  line text NOT NULL,
  CONSTRAINT primary_key_mpk_lines PRIMARY KEY (line_id)
)
WITH (
  OIDS=FALSE
);


CREATE TABLE mpk_stops
(
  id serial NOT NULL,
  service_line_id BIGINT NOT NULL,
  stop_number INTEGER NOT NULL,
  stop_street TEXT NOT NULL,
  timetable_id INTEGER NOT NULL,
  CONSTRAINT primary_key_mpk_stops PRIMARY KEY (id),
  CONSTRAINT fk_service_line_id FOREIGN KEY(service_line_id)
	REFERENCES mpk_lines(line_id)
)
WITH (
  OIDS=FALSE
);


CREATE TABLE  mpk_stops_connections
(
  id serial NOT NULL,
  src_stop BIGINT NOT NULL,
  dst_stop BIGINT NOT NULL,
  time INTEGER NOT NULL,
  CONSTRAINT primary_key_mpk_stops_connections PRIMARY KEY (id),
  CONSTRAINT fk_src_stop FOREIGN KEY(src_stop)
  REFERENCES mpk_stops(id),
  CONSTRAINT fk_dst_stop FOREIGN KEY(src_stop)
  REFERENCES mpk_stops(id)
)
WITH (
  OIDS=FALSE
);