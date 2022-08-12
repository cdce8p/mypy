import sys

from mypy.build import BuildSource, Options, build
from mypy.version import __version__

print(__version__)

options = Options()
options.show_traceback = True
options.raise_exceptions = True
# options.verbosity = 10
# result = build([BuildSource("/Users/James/PycharmProjects/mypy/rotki/rotkehlchen/constants/ethereum.py", "rotki.rotkehlchen.constants.ethereum")], options, stderr=sys.stderr, stdout=sys.stdout)
result = build([BuildSource("test.py", None)], options, stderr=sys.stderr, stdout=sys.stdout)
print(*result.errors, sep="\n")
