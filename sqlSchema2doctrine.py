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
    r"\bDEFAULT (?P<value>(?:\w+|'[^']+'))\b"
)

notNullPattern = re.compile(
    r"\bNOT NULL\b"
)

autoIncrementPattern = re.compile(
    r"\bAUTO_INCREMENT\b"
)

intColPattern = re.compile(
    r"(\w*)int\(?"
)
stringColPattern = re.compile(
    r"\w*char\(?"
)

def doctrineType(col):
    intMatch = intColPattern.match(col)
    if intMatch:
        subtype = intMatch.group(1)
        if subtype == "tiny" or subtype == "small":
            return "smallint"
        elif subtype == "big":
            return "bigint"
        else:
            return "integer"
    elif stringColPattern.match(col):
        return "string"
    elif col.startswith("enum") or col.startswith("set"):
        return "string"
    elif col.startswith("double") or col.startswith("float"):
        return "float"
    else:
        return col

def doctrineOptions(col, options):
    r = []
    if notNullPattern.search(options):
        r.append('"notnull" => true')
    if autoIncrementPattern.search(options):
        r.append('"autoincrement" => true')
    defaultValue = defaultValuePattern.search(options)
    if defaultValue:
        r.append('"default" => %s' % (defaultValue.group('value')))
    return r

sql = open(sys.argv[1], 'r').read()
for tbl in tablePattern.finditer(sql):
    print "$%s = $schema->createTable(\"%s\");" % (
        tbl.group('name'),
        tbl.group('name')
    )

    for col in columnPattern.finditer(tbl.group('def')):
        print "$%s->addColumn(\"%s\", \"%s\", [%s]);" % (
            tbl.group('name'),
            col.group('name'),
            doctrineType(col.group('type')),
            ", ".join(doctrineOptions(col.group('type'), col.group('options')))
        )
        defaultValue = defaultValuePattern.search(col.group('options'))
        #if defaultValue:
            #print "   DEFAULT %s" % (defaultValue.group('value'))
        #if notNullPattern.search(col.group('options')):
            #print "   NOT NULL"

    print
