
from citeproc import * 
import json

STYLE = Style('./apa.csl')
print STYLE
REFS = json.loads(open('./refs.json').read())
print REFS
PROCESSED = process_bibliography(STYLE, REFS)
print PROCESSED
print format_bibliography(PROCESSED)
