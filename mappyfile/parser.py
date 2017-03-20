import os, logging
from io import open
from lark import Lark

class Parser(object):

    def __init__(self, cwd=None, expand_includes=True):
        self.cwd = cwd
        self.expand_includes = expand_includes

        gf = os.path.join(os.path.dirname(__file__), "mapfile_lark.g")
        grammar_text = open(gf).read()

        self.g = Lark(grammar_text, parser='earley', lexer='standard')

    def strip_quotes(self, s):
        return s.strip("'").strip('"')

    def load_includes(self, text):

        lines = text.split('\n')
        includes = {}

        for idx, l in enumerate(lines):
            if l.strip().lower().startswith('include'):
                if '#' in l:
                    l = l[:l.index('#')]

                parts = [p for p in l.split()]

                assert (len(parts) == 2)
                assert (parts[0].lower() == 'include')
                fn = os.path.join(self.cwd, self.strip_quotes(parts[1]))
                try:
                    include_text = self.open_file(fn)
                except IOError as ex:
                    logging.warning("Include file '%s' not found", fn)
                    raise ex
                # recursively load any further includes
                includes[idx] = self.load_includes(include_text)
    
        for idx, txt in includes.items():
            lines.pop(idx) # remove the original include
            lines.insert(idx, txt)

        return '\n'.join(lines)

    def open_file(self, fn):
        return open(fn, "r", encoding="utf-8").read() # specify unicode for Python 2.7

    def parse_file(self, fn):

        self.cwd = os.path.dirname(fn)

        text = self.open_file(fn)
        return self.parse(text)

    def parse(self, text):

        if self.expand_includes == True:
            text = self.load_includes(text)

        text += '\n'
        return self.g.parse(text+'\n')
