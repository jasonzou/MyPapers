# vim: fileencoding=utf-8
# Copyright (c) 2006, 2007, 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# from pybtex! project

import re
def split_name_list(string):
    """
    Split a list of names, separated by ' and '.

    >>> split_name_list('Johnson and Peterson')
    ['Johnson', 'Peterson']
    >>> split_name_list('Armand and Peterson')
    ['Armand', 'Peterson']
    >>> split_name_list('Armand and anderssen')
    ['Armand', 'anderssen']
    >>> split_name_list('What a Strange{ }and Bizzare Name! and Peterson')
    ['What a Strange{ }and Bizzare Name!', 'Peterson']
    >>> split_name_list('What a Strange and{ }Bizzare Name! and Peterson')
    ['What a Strange and{ }Bizzare Name!', 'Peterson']
    """
    return split_tex_string(string, ' and ')


def split_tex_string(string, sep=None, strip=True, filter_empty=False):
    """Split a string using the given separator (regexp).

    Everything at brace level > 0 is ignored.
    Separators at the edges of the string are ignored.

    >>> split_tex_string('')
    []
    >>> split_tex_string('     ')
    []
    >>> split_tex_string('   ', ' ', strip=False, filter_empty=False)
    [' ', ' ']
    >>> split_tex_string('.a.b.c.', r'\.')
    ['.a', 'b', 'c.']
    >>> split_tex_string('.a.b.c.{d.}.', r'\.')
    ['.a', 'b', 'c', '{d.}.']
    >>> split_tex_string('Matsui      Fuuka')
    ['Matsui', 'Fuuka']
    >>> split_tex_string('{Matsui      Fuuka}')
    ['{Matsui      Fuuka}']
    >>> split_tex_string('a')
    ['a']
    >>> split_tex_string('on a')
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

class Person(object):
    """Represents a person (usually human).

    >>> p = Person('Avinash K. Dixit')
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
    >>> p == Person(unicode(p))
    True
    >>> p = Person('Dixit, Jr, Avinash K. ')
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
    >>> p == Person(unicode(p))
    True

    >>> p = Person('abc')
    >>> print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    [] [] [] ['abc'] []
    >>> p = Person('Viktorov, Michail~Markovitch')
    >>> print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    ['Michail'] ['Markovitch'] [] ['Viktorov'] []
    """
    valid_roles = ['author', 'editor'] 
    style1_re = re.compile('^(.+),\s*(.+)$')
    style2_re = re.compile('^(.+),\s*(.+),\s*(.+)$')

    def __init__(self, string="", first="", middle="", prelast="", last="", lineage=""):
        self._first = []
        self._middle = []
        self._prelast = []
        self._last = []
        self._lineage = []
        string = string.strip()
        if string:
            self.parse_string(string)
        self._first.extend(split_tex_string(first))
        self._middle.extend(split_tex_string(middle))
        self._prelast.extend(split_tex_string(prelast))
        self._last.extend(split_tex_string(last))
        self._lineage.extend(split_tex_string(lineage))

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
            print '----------------------'
            print von, last
            print '++++++++++++++++++++++'
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

        parts = split_tex_string(name, ',')
        if len(parts) == 3: # von Last Roman, Jr, First
            parts1 = split_tex_string(parts[0])
            self._roman(parts1[-1])
            if self.hasRoman:
                parts1.pop()
            
            tmp = " ".join(parts1)
            
            process_von_last(split_tex_string(tmp))
            self._lineage.extend(split_tex_string(parts[1]))
            process_first_middle(split_tex_string(parts[2]))
        elif len(parts) == 2: # von Last Jr/Roman, First
            parts1 = split_tex_string(parts[0])
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
        
            #process_von_last(split_tex_string(parts[0]))
            process_von_last(split_tex_string(tmp))
            process_first_middle(split_tex_string(parts[1]))
        elif len(parts) == 1: # First von Last Jr/Roman
            parts = split_tex_string(name)
            
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
            self._lineage.extend(split_tex_string(self.apellation))
            
    def _roman(self, item):
        roman = ['I','II','III','IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
        self.hasRoman = False
        if item in roman:
            self.hasRoman = True
            self.roman = item
        if self.hasRoman:
            self._lineage.extend(split_tex_string(self.roman))

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

if __name__ == '__main__':
    p = Person('abc')
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    
    p = Person('Viktorov, Michail~Markovitch')
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    
    p = Person('fjdkladf {fjdlsjlfd zou}')
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    
    p = Person('Marcial L. Zeng')
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    
    p = Person("Mark N. Grimshaw")
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    
    
    p = Person("Bush III, G.W.")
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()

    p = Person("Bush III, Jr., G.W.")
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()

    
    p = Person("Bush III, G. W.")
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()

    p = Person("G.W. Bush III")
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()


    p = Person("Hammer, Jr., Zou ")
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
 
    p = Person("M.C. Hammer III Jr. ")
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    
    p = Person("M. C. Hammer Jr. III")
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()

    print split_tex_string("Charles Louis Xavier Joseph De la Vallee Poussin")
    print split_tex_string("Charles Louis Xavier Joseph {de la Vallee} Poussin")
    print split_tex_string("Charles Louis Xavier Joseph {{de la} Vallee} Poussin")
    print split_tex_string("Charles Louis Xavier Joseph a. b. c. {{de  {343} la} Vallee} Poussin")
     
    p = Person("von Frankenstein, Ferdinand Cecil, P.H.")
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
     

    p = Person("Charles Louis Xavier Joseph de la Vallee Poussin")
    print p.first(), p.middle(), p.prelast(), p.last(), p.lineage()
    
    