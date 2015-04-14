#!/usr/bin/env python

MPK_URL = 'http://www.mpk.lodz.pl/rozklady/linie.jsp'
MPK_LINE_URL = 'http://www.mpk.lodz.pl/rozklady/trasa.jsp?lineId={lineId}'

UPDATE_INTERVAL = 120
LANG = 'pl-PL'
LINEID_REGEX = 'lineId=(\d+)'