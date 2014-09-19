#!/usr/bin/env python
"""cli.py: import bibtex into bibjson and load into bibserver"""

import os
import sys
import optparse
import inspect

# does setup of cfg
from bibserver import dao

def rebuild_db():
    '''Rebuild the db'''
    conn, db = dao.get_conn()
    conn.delete_index(db)
    conn.create_index(db)

def fixtures():
    '''fixtures'''
    import test.base
    for dict_ in test.base.fixtures['records']:
        dao.Record.upsert(dict_)

def convert(inpath):
    '''
    Convert from bibtex to bibjson.
    One argument expected: path to bibtex file.
    '''
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    import json
    parser = BibTexParser()
    with open(inpath) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    print json.dumps(bib_database.entries, indent=2, sort_keys=True)
    print(bib_database.entries)

def bulk_upload(colls_list):
    '''
    Take a collections list in a JSON file and use the bulk_upload importer.
    colls_list described in importer.py
    '''
    import bibserver.importer
    return bibserver.importer.bulk_upload(colls_list)
    
"""
==================================================
Misc stuff for setting up a command line interface
---------------------------------------------------
"""

def _module_functions(functions):
    '''module functions'''
    local_functions = dict(functions)
    for k, v in local_functions.items():
        if not inspect.isfunction(v) or k.startswith('_'):
            del local_functions[k]
    return local_functions

def _main(functions_or_object):
    '''main '''
    isobject = inspect.isclass(functions_or_object)
    if isobject:
        _methods = _object_methods(functions_or_object)
    else:
        _methods = _module_functions(functions_or_object)
    usage = '''%prog {action}
Actions:
    '''
    usage += '\n    '.join(
        ['%s: %s' % (name, m.__doc__.split('\n')[0]
            if m.__doc__ else '') for (name, m) in sorted(_methods.items())])
    parser = optparse.OptionParser(usage)
    # Optional: for a config file
    # parser.add_option('-c', '--config', dest='config',
    #         help='Config file to use.')
    options, args = parser.parse_args()

    if not args or not args[0] in _methods:
        parser.print_help()
        sys.exit(1)

    method = args[0]
    if isobject:
        getattr(functions_or_object(), method)(*args[1:])
    else:
        _methods[method](*args[1:])

__all__ = ['_main']

if __name__ == '__main__':
    print(locals())
    print("--------------------\n")
    print(globals())
    _main(locals())


