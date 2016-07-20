# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import difflib
import logging
import sys

import neovim

try:
    from yapf import yapf_api
    FormatCode = yapf_api.FormatCode
    _has_yapf = True
except ImportError:
    sys.stderr.write(
        "Could not import yapf_api., Please use sudo pip install yapf at first")
DEBUG = False
if DEBUG:
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


buffer_dict = {}


@neovim.plugin
class YapfPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim

    @neovim.command("YapfFormater", range='', nargs='*')
    def yapf_command(self, args, range):
        self.buffer = self.nvim.buffers[self.nvim.current.buffer.number]
        if not _has_yapf or not self.buffer.name.endswith('.py'):
            return
        self.cur_line = range[0]
        self.full_format = args and args[0] == 'full'
        self.range = (self.full_format and [0, len(self.buffer)]) or None
        self._format()

    def _get_up(self):
        up_text = self.buffer[:self.cur_line + 1]
        for index, line in sorted(enumerate(up_text), reverse=True):
            if line and not line.startswith(' '):
                space = 0
                for line in self.buffer[index:self.cur_line]:
                    if not line:
                        space += 1
                    else:
                        break
                return index + space
        return 0

    def _get_down(self):
        down_text = self.buffer[self.cur_line:+1]
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

    def _has_diff(self):
        with open(self.buffer.name, 'r') as f:
            origi = f.read()
        result = difflib.SequenceMatcher(None, origi,
                                         '\n'.join(self.buffer[:]))
        if result.ratio() != 1.0:
            return True

    def _format(self):
        text, up, down = self._get_scope()
        if not self._has_diff():
            return
        formated_text, ok = self._try(text)
        if not ok:
            text = '\n'.join(self.buffer[:])
            up, down = 0, len(self.buffer[:])
            formated_text, ok = self._try(text, final=True)
        if not ok:
            return
        formated_range = formated_text.splitlines()

        self.pos = self.nvim.eval('getpos(".")')
        self.buffer[up:down] = formated_range
        if self.nvim.current.buffer == self.buffer:
            self.nvim.eval('setpos(".", {})'.format(self.pos))

    def _try(self, text, final=False):
        try:
            return FormatCode(text, filename='<stdin>', verify=False)
        except (SyntaxError, IndentationError) as err:
            if final:
                sys.stderr.write(str(err))
            return text, False
