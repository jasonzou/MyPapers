#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""cli.py: import bibtex into bibjson and load into bibserver"""
"""PyBtex project: person => PersonalName 
"""
import os
import sys
import optparse
import inspect

import re

# does setup of cfg
from bibserver import dao
from bibserver.importer import *

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
        
def split_string(string, sep=None, strip=True, filter_empty=False):
    """Split a string using the given separator (regexp).

    Everything at brace level > 0 is ignored.
    Separators at the edges of the string are ignored.

    >>> split_string('')
    []
    >>> split_string('     ')
    []
    >>> split_string('   ', ' ', strip=False, filter_empty=False)
    [' ', ' ']
    >>> split_string('.a.b.c.', r'\.')
    ['.a', 'b', 'c.']
    >>> split_string('.a.b.c.{d.}.', r'\.')
    ['.a', 'b', 'c', '{d.}.']     
    >>> split_string('Matsui      Fuuka')     
    ['Matsui', 'Fuuka']     
    >>> split_string('{Matsui      Fuuka}')     
    ['{Matsui      Fuuka}']     
    >>> split_string('a')     
    ['a']
    >>> split_string('on a')
    ['on', 'a']
    """
    if sep is None:
        sep = '[\s~]+'
        filter_empty = True
    sep_re = re.compile(sep)
    brace_level = 0
    name_start = 0
    result = []
    string_len = len(string)
    pos = 0
    for pos, char in enumerate(string):
        if char == '{':
            brace_level += 1
        elif char == '}':
            brace_level -= 1
        elif brace_level == 0 and pos > 0:
            match = sep_re.match(string[pos:])
            if match:
                sep_len = len(match.group())
                if pos + sep_len < string_len:
                    result.append(string[name_start:pos])
                    name_start = pos + sep_len
    if name_start < string_len:
        result.append(string[name_start:])
    if strip:
        result = [part.strip() for part in result]
    if filter_empty:
        result = [part for part in result if part]
    return result
        
"""
	$authors = "Mark N. Grimshaw and 
    Bush III, G.W. & M. C. Hammer Jr. 
    and von Frankenstein, Ferdinand Cecil, P.H. 
    & Charles Louis Xavier Joseph de la Vallee Poussin and et. al";
"""
class PersonalName(object):
    """Represents a person (usually human).

    >>> p = PersonalName('Avinash K. Dixit')
    >>> print p.first()
    ['Avinash']
    >>> print p.middle()
    ['K.']
    >>> print p.prelast()
    []
    >>> print p.last()
    ['Dixit']
    >>> print p.lineage()
    []
    >>> print unicode(p)
    Dixit, Avinash K.
    >>> p == PersonalName(unicode(p))
    True
    >>> p = PersonalName('Dixit, Jr, Avinash K. ')
    >>> print p.first()
    ['Avinash']
    >>> print p.middle()
    ['K.']
    >>> print p.prelast()
    []
    >>> print p.last()
    ['Dixit']
    >>> print p.lineage()
    ['Jr']
    >>> print unicode(p)
    Dixit, Jr, Avinash K.
    >>> p == PersonalName(unicode(p))
    True

    >>> p = PersonalName('abc')
    >>> print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    [] [] [] ['abc'] []
    >>> p = PersonalName('Viktorov, Michail~Markovitch')
    >>> print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    ['Michail'] ['Markovitch'] [] ['Viktorov'] []
    """
    def __init__(self, string="", first="", middle="", prelast="", last="", lineage=""):
        self._first = []
        self._middle = []
        self._prelast = []
        self._last = []
        self._lineage = []
        
        # strip trailing spaces
        string = string.strip()

        # get rid of double spaces
        string = re.sub("\s{2,}", ' ', string)
        
        if string:
            self.parse_string(string)
        self._first.extend(split_string(first))
        self._middle.extend(split_string(middle))
        self._prelast.extend(split_string(prelast))
        self._last.extend(split_string(last))
        self._lineage.extend(split_string(lineage))

    def parse_string(self, name):
        """Extract various parts of the name from a string.
        Supported formats are:
         - von Last, First
         - von Last, Jr, First
         - First von Last
        (see BibTeX manual for explanation)
        """
        def process_first_middle(parts):
            try:
                self._first.append(parts[0])
                self._middle.extend(parts[1:])
            except IndexError:
                pass

        def process_von_last(parts):
            von, last = rsplit_at(parts, lambda part: part.islower())
            if von and not last:
                last.append(von.pop())
            self._prelast.extend(von)
            self._last.extend(last)

        def find_pos(lst, pred):
            for i, item in enumerate(lst):
                if pred(item):
                    return i
            return i + 1

        def split_at(lst, pred):
            """Split the given list into two parts.

            The second part starts with the first item for which the given
            predicate is True.
            """
            pos = find_pos(lst, pred)
            return lst[:pos], lst[pos:]

        def rsplit_at(lst, pred):
            rpos = find_pos(reversed(lst), pred)
            pos = len(lst) - rpos
            return lst[:pos], lst[pos:]

        parts = split_string(name, ',')
        if len(parts) == 3: # von Last Roman, Jr, First
            parts1 = split_string(parts[0])
            self._roman(parts1[-1])
            if self.hasRoman:
                parts1.pop()
            tmp = " ".join(parts1)
            process_von_last(split_string(tmp))
            self._lineage.extend(split_string(parts[1]))
            process_first_middle(split_string(parts[2]))
        elif len(parts) == 2: # von Last Jr/Roman, First
            parts1 = split_string(parts[0])
            self._apellation(parts1[-1])
            if self.apellation:
                parts1.pop()
            self._roman(parts1[-1])
            if self.hasRoman:
                parts1.pop()
            self._apellation(parts1[-1])
            if self.apellation:
                parts1.pop()
            tmp = " ".join(parts1)
            #process_von_last(split_string(parts[0]))
            process_von_last(split_string(tmp))
            process_first_middle(split_string(parts[1]))
        elif len(parts) == 1: # First von Last Jr/Roman
            parts = split_string(name)
            self._apellation(parts[-1])
            if self.apellation:
                parts.pop()
            self._roman(parts[-1])
            if self.hasRoman:
                parts.pop()
            self._apellation(parts[-1])
            if self.apellation:
                parts.pop()
            first_middle, von_last = split_at(parts, lambda part: part.islower())
            if not von_last and first_middle:
                last = first_middle.pop()
                von_last.append(last)
            process_first_middle(first_middle)
            process_von_last(von_last)
        else:
            raise Error('Invalid name format: %s' % name)

    def _apellation(self, name):
        hasApellation = False
        rr = re.compile("Sr\.|jr\.", re.IGNORECASE)
        isMatch = re.search(rr, name)
        if (isMatch):
            apellation = isMatch.group()
            hasApellation = True
        
        if (hasApellation):
            if (apellation.lower() == "jr."):
                self.apellation = "Jr."
            else:
                self.apellation = "Sr."
        else:
            self.apellation = ""
        if hasApellation:
            self._lineage.extend(split_string(self.apellation))
            
    def _roman(self, item):
        roman = ['I','II','III','IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
        self.hasRoman = False
        if item in roman:
            self.hasRoman = True
            self.roman = item
        if self.hasRoman:
            self._lineage.extend(split_string(self.roman))

    def __eq__(self, other):
        if not isinstance(other, Person):
            return super(Person, self) == other
        return (
                self._first == other._first
                and self._middle == other._middle
                and self._prelast == other._prelast
                and self._last == other._last
                and self._lineage == other._lineage
        )

    def __unicode__(self):
        # von Last, Jr, First
        von_last = ' '.join(self._prelast + self._last)
        jr = ' '.join(self._lineage)
        first = ' '.join(self._first + self._middle)
        return ', '.join(part for part in (von_last, jr, first) if part)

    def __repr__(self):
        return 'Person({0})'.format(repr(unicode(self)))

    def get_part_as_text(self, type):
        names = getattr(self, '_' + type)
        return ' '.join(names)

    def get_part(self, type, abbr=False):
        names = getattr(self, '_' + type)
        return names

    #FIXME needs some thinking and cleanup
    def bibtex_first(self):
        """Return first and middle names together.
        (BibTeX treats all middle names as first)
        """
        return self._first + self._middle

    def first(self, abbr=False):
        return self.get_part('first', abbr)
    def middle(self, abbr=False):
        return self.get_part('middle', abbr)
    def prelast(self, abbr=False):
        return self.get_part('prelast', abbr)
    def last(self, abbr=False):
        return self.get_part('last', abbr)
    def lineage(self, abbr=False):
        return self.get_part('lineage', abbr)
  
    def __str__(self):
        string = "First: %s; Middle: %s; von: %s; Last: %s; Jr:%s" % (self.first(), 
                    self.middle(), self.prelast(), 
                    self.last(), self.lineage())
        return string
    
    def __repr__(self):
        return { "firstname": self.first(),
            "middlename": self.middle(),
            "von": self.prelast(),
            "lastname": self.last(),
            "apellation": self.lineage() }
        
        
def parseNames(names):
    inputNames = names.strip()
    
    #annonymous

    delimit = "##!!##"
    rr = re.compile("\s+(and|&)\s+", re.IGNORECASE)
    authorsList = re.sub(rr, delimit, inputNames).split(delimit)
    
    for value in authorsList:
        if value.lower().startswith('et. al'):
            etAl = true
            print("etal is true")
    
    authors = list()
    
    for value in authorsList:
        # parse each name into tempAuthor
        tempAuthor = PersonalName(value)
        authorInfo = dict()
        
        #print(authorStr)
        authorInfo["raw"] = value
        authorInfo["firstname"] = " ".join(tempAuthor.first())
        authorInfo["middlename"] = " ".join(tempAuthor.middle())
        authorInfo["von"] = " ".join(tempAuthor.prelast())
        authorInfo["lastname"] = " ".join(tempAuthor.last())
        authorInfo["apellation"] = " ".join(tempAuthor.lineage())
        authors.append(authorInfo)
        
    return authors
    #for key in authorArray.keys():
    #    print authorArray[key]
    #print(authorsList)
    
    

from bibtexparser.customization import *
def myAuthor(record):
    if "author" in record:
        if record["author"]:
            record["authorList"] = parseNames(record["author"])
        else:
            del record["author"]
    return record
    
def customizations(record):
    record = type(record)
    record = link(record)
    record = doi(record)
    record = myAuthor(record)
    record = keyword(record)

    return record

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
        parser.customization = customizations
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    myRecords = list()
    num = 1
    records = dict()
    for record in bib_database.entries:
        record1 = dict()
        record1 = record
        record1["_id"] = num
        record1["collection"] = "test01"
        num = num + 1
        
        myRecords.append(record1)
        #temp = json.dumps(record, indent=2, sort_keys=True)
        #t
        #myRecords
    records["records"] = myRecords
    return records

def convertPrint(inpath):
    records = convert(inpath)
    
    print json.dumps(records, indent=2, sort_keys=True)

def bulk_upload(inpath):
    '''
    Take a collections list in a JSON file and use the bulk_upload importer.
    colls_list described in importer.py
    '''
    jsonin = convert(inpath)
    
    importer = Importer("jason")
    return importer.upload(jsonin, "test01")
    
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
    _main(locals())


