#!/usr/bin/env python

import sqlparse, sys, pprint

sql = open(sys.argv[1], 'r').read()
tree = sqlparse.parse(sql)
for st in tree:
    if st.get_type() != 'CREATE': continue
    # It looks like a function call because the table contents are in parens
    tbl = st.token_next_by_instance(0, sqlparse.sql.Function)
    tbl_name = tbl.token_next_by_instance(0, sqlparse.sql.Identifier)
    pprint.pprint(tbl_name.value)
    fields = tbl.token_next_by_instance(0, sqlparse.sql.Parenthesis)
    pprint.pprint(fields.flatten())
    break
