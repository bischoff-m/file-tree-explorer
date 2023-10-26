# pyright: reportUndefinedVariable=false

from sly import Lexer
import pandas as pd


class FileListLexer(Lexer):
    # Set of token names.   This is always required
    tokens = {
        # WHITESPACE,
        LITERAL_LAST_WRITE_TIME,
        LITERAL_VERZEICHNIS,
        LITERAL_LENGTH,
        LITERAL_MODE,
        LITERAL_NAME,
        SEPARATOR_LINE,
        DATETIME,
        NUMBER,
        MODE,
        DIR_PATH,
        FILENAME,
    }

    ignore_whitespace = r" +"

    # WHITESPACE = r" +"
    LITERAL_LAST_WRITE_TIME = r"LastWriteTime"
    LITERAL_VERZEICHNIS = r"Verzeichnis: "
    LITERAL_LENGTH = r"Length"
    LITERAL_MODE = r"Mode"
    LITERAL_NAME = r"Name"
    SEPARATOR_LINE = r"(?:-+ +){4,}"

    # DD.MM.YYYY \s+ HH:MM
    @_(r"\d{2}\.\d{2}\.\d{4} +\d{2}:\d{2}")
    def DATETIME(self, t):
        t.value = pd.to_datetime(t.value, format="%d.%m.%Y %H:%M")
        return t

    @_(r"\d+ ")
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r"[als-]{6}")
    def MODE(self, t):
        return t

    FILENAME = r"[^\\\n ][^\\\n]*[\w}]"
    DIR_PATH = r"[a-zA-Z]:.+[^\\\n]*[\w}]"

    ignore_zero_width_space = r"\ufeff"

    # Line number tracking
    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        print("Line %d: Bad character %r" % (self.lineno, t.value[0]))
        self.index += 1


if __name__ == "__main__":
    data = """
    Verzeichnis: C:\Program Files\AMD
"""
    lexer = FileListLexer()
    for tok in lexer.tokenize(data):
        print(tok.type)
