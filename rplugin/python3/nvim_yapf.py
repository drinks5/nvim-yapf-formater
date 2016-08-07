# -*- coding: utf-8 -*-
import difflib
from itertools import takewhile

import neovim

try:
    from yapf import yapf_api
    FormatCode = yapf_api.FormatCode
    _has_yapf = True
except ImportError:
    _has_yapf = False


@neovim.plugin
class YapfPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim
        self.buffer = self.nvim.buffers[self.nvim.current.buffer.number]

    def echo(self, message):
        self.nvim.command('echom "{}"'.format(message))

    @neovim.command("YapfFormater", range='', nargs='*')
    def yapf_command(self, args, range):
        if not _has_yapf or not self.buffer.name.endswith('.py'):
            self.echo('please install yapf first\npip install yapf')
            return
        self.cur_line = range[0]
        self.full_format = args and args[0] == 'full'
        self.range = (self.full_format and [0, len(self.buffer)]) or None
        self._format()

    def _get_up(self):
        up_text = self.buffer[:self.cur_line]
        for line in reversed(up_text):
            index = get_index(self.buffer, line)
            if is_not_blank(line):
                lines = takewhile(is_blnak, self.buffer[index:self.cur_line])
                return index + min(2, len(list(lines)))
        return 0

    def _get_down(self):
        down_text = self.buffer[self.cur_line:]
        for line in down_text:
            index = get_index(self.buffer, line)
            if is_not_blank(line):
                lines = takewhile(is_blnak,
                                  reversed(self.buffer[self.cur_line:index]))
                return index - min(2, len(list(lines)))
        return len(self.buffer[:])

    def _get_scope(self):
        up, down = self.range or (self._get_up(), self._get_down())
        scope_text = self.buffer[up:down]
        text = '\n'.join(scope_text)
        return text, up, down

    def _format(self):
        text, up, down = self._get_scope()
        if not self.full_format and not _has_diff(self.buffer, up, down,
                                                  self.echo):
            return
        formated_text, ok = self._try(text)
        if not ok:
            text, up, down = '\n'.join(self.buffer[:]), 0, len(self.buffer[:])
            formated_text, ok = self._try(text)
        if not ok:
            return
        formated_range = formated_text.splitlines()

        self.pos = self.nvim.eval('getpos(".")')
        self.buffer[up:down] = formated_range
        if self.nvim.current.buffer == self.buffer:
            self.nvim.eval('setpos(".", {})'.format(self.pos))
        self.nvim.command('write')
        self.echo('format range from {} to {}'.format(up, down))

    def _try(self, text, final=False):
        try:
            return FormatCode(text, filename='<stdin>', verify=False)
        except (SyntaxError, IndentationError) as err:
            self.echo(str(err))
            return text, False


def _has_diff(buffer, up, down, echo=None):
    try:
        with open(buffer.name, 'r') as f:
            origin = '\n'.join(f.read().splitlines()[up:down])
        modified_text = '\n'.join(buffer[up:down])
        result = difflib.SequenceMatcher(None, origin, modified_text)
        if result.ratio() == 1.0:
            echo('has no diff, range from {} to {}'.format(up, down))
            return False
    except Exception as err:
        echo(str(err))
    return True


def is_blnak(line):
    return not line.strip('')


def is_not_blank(line):
    return line and not line.startswith(' ')


def get_index(buffer, line):
    return buffer[:].index(line)
