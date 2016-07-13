# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import sys

import neovim

try:
    from yapf import yapf_api
    FormatCode = yapf_api.FormatCode
    _has_yapf = True
except ImportError:
    sys.stderr.write("Could not import yapf_api. Have you set "
                     "g:yapf_format_yapf_location correctly?")
logger = logging.getLogger('nvim_yapf')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('nvim_yapf.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def log(key='key', value='value'):
    logger.info('{}={}'.format(key, value))


@neovim.plugin
class TestPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim

    @neovim.command("YapfFormat", range='', nargs='*')
    def testcommand(self, args, range):
        if not _has_yapf:
            return
        self.buffer = self.nvim.current.buffer
        self.cur_line = self.buffer[:].index(self.nvim.current.line)
        self.full_format = args and args[0] == 'full'
        self.range = (self.full_format and [0, len(self.buffer)]) or None
        pos = self.nvim.eval('getpos(".")')
        self._format()
        self.nvim.eval('setpos(".", {})'.format(pos))

    def _get_up(self):
        up_text = self.buffer[:self.cur_line]
        for index, line in sorted(enumerate(up_text), reverse=True):
            if line and not line.startswith(' '):
                return index
        return 0

    def _get_down(self):
        down_text = self.buffer[self.cur_line:]
        for index, line in enumerate(down_text, self.cur_line):
            if line and not line.startswith(' '):
                space = 0
                for line in reversed(self.buffer[self.cur_line:index]):
                    if not line:
                        space += 1
                    else:
                        break
                return index - space
        return len(self.buffer[:])

    def _get_scope(self):
        up, down = self.range or (self._get_up(), self._get_down())
        scope_text = self.buffer[up:down]
        text = '\n'.join(scope_text)
        return text, up, down

    def _format(self, ):
        text, up, down = self._get_scope()
        try:
            formated_text, ok = FormatCode(text, filename='<stdin>')
        except (SyntaxError, IndentationError):
            text = '\n'.join(self.buffer[:])
            up, down = 0, len(self.buffer[:])
            formated_text, ok = FormatCode(text, filename='<stdin>')
        if not ok:
            return
        formated_range = formated_text.splitlines()
        self.nvim.current.buffer[up:down] = formated_range
