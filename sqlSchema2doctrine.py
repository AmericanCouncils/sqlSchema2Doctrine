#!/usr/bin/env python

import re, sys

tablePattern = re.compile(
    r'CREATE\s+TABLE[\s\w= ]*`(?P<name>\w+)`\s*\((?P<def>.+?)\)[\w= ]*;',
    re.DOTALL
)

columnPattern = re.compile(
    r'^\s*`(?P<name>\w+)`\s*(?P<type>\S+)\s*(?P<options>.*)',
    re.MULTILINE
)

keyPattern = re.compile(
    r'(?P<primary>(?:PRIMARY)?)\s*KEY\s*(?:`\w+`)?\s*\(`(?P<name>\w+)`\)'
)

defaultValuePattern = re.compile(
    r"\bDEFAULT\s+(?P<value>(?:[\d.-]+|'[^']+'|NULL))\b"
)

notNullPattern = re.compile(
    r"\bNOT\s+NULL\b"
)

autoIncrementPattern = re.compile(
    r"\bAUTO_INCREMENT\b"
)

intColPattern = re.compile(
    r"(\w*)int\(?"
)
stringColPattern = re.compile(
    r"\w*char(?:\((\d+)\))?"
)

def doctrineType(col):
    col = col.rstrip(",")
    intMatch = intColPattern.match(col)
    if intMatch:
        subtype = intMatch.group(1)
        if subtype == "tiny" or subtype == "small":
            return "smallint"
        elif subtype == "big":
            return "bigint"
        else:
            return "integer"
    elif col == "timestamp":
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
    else:
        r.append('"notnull" => false')

    if autoIncrementPattern.search(options):
        r.append('"autoincrement" => true')
    defaultValue = defaultValuePattern.search(options)
    if defaultValue:
        r.append('"default" => %s' % (defaultValue.group('value')))

    stringMatch = stringColPattern.match(col)
    if stringMatch and stringMatch.group(1) is not None:
        r.append('"length" => %s' % int(stringMatch.group(1)))

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

    for key in keyPattern.finditer(tbl.group('def')):
        if key.group('primary') == "PRIMARY":
            print "$%s->setPrimaryKey([\"%s\"]);" % (
                tbl.group('name'),
                key.group('name')
            )
        else:
            print "$%s->addIndex([\"%s\"]);" % (
                tbl.group('name'),
                key.group('name')
            )

    print
