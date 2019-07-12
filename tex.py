
from pathlib import Path
from enum import Enum
from tempfile import TemporaryDirectory
import subprocess
from subprocess import DEVNULL, TimeoutExpired
from dataclasses import dataclass
from typing import List
import util


@dataclass
class Primitives:
    commands: List[str]
    environments: List[str]


KERNEL_PRIMITIVES = util.load_json('kernel.json', Primitives)


class Format(Enum):
    LATEX = 'latex'
    LUALATEX = 'lualatex'
    XELATEX = 'xelatex'


class CompilationResult:
    def __init__(self, tmpdir):
        self.tmpdir = tmpdir

    def find(self, ext):
        return Path(self.tmpdir.name) / 'code.{}'.format(ext)

    def find_img(self, index):
        return Path(self.tmpdir.name) / 'code{}.png'.format(index)

    def read_log(self):
        return self.find('log').read_text(errors='replace')


def compile(code, fmt=Format.LATEX, timeout=10):
    tmpdir = TemporaryDirectory()
    (Path(tmpdir.name) / 'code.tex').write_text(code)
    cmd = [fmt.value, '-interaction=batchmode',
           '-shell-escape', 'code.tex']
    try:
        subprocess.run(cmd, cwd=tmpdir.name, timeout=timeout,
                       stdout=DEVNULL, stderr=DEVNULL)
        return CompilationResult(tmpdir)
    except TimeoutExpired as error:
        tmpdir.cleanup()
        raise error
