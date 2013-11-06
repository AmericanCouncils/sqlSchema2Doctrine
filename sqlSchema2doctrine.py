#!/usr/bin/env python

import re, sys

tablePattern = re.compile(
    r'CREATE TABLE [\w= ]*`(?P<name>\w+)` \((?P<def>.+?)\)[\w= ]*;',
    re.DOTALL
)

columnPattern = re.compile(
    r'`(?P<name>\w+)` (?P<type>\S+) (?P<options>.+)'
)

defaultValuePattern = re.compile(
    r"\bDEFAULT (?P<value>(?:\w+|'[^']+'))"
)

notNullPattern = re.compile(
    r"\bNOT NULL"
)

sql = open(sys.argv[1], 'r').read()
for tbl in tablePattern.finditer(sql):
    print tbl.group('name')
    for col in columnPattern.finditer(tbl.group('def')):
        print "N: %s   T: %s" % (col.group('name'), col.group('type'))
        defaultValue = defaultValuePattern.search(col.group('options'))
        if defaultValue:
            print "   DEFAULT %s" % (defaultValue.group('value'))
        if notNullPattern.search(col.group('options')):
            print "   NOT NULL"
    print
