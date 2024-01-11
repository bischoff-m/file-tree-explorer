# pyright: reportUndefinedVariable=false

from pathlib import PurePath

import pandas as pd
from lastwrite_lexer import FileListLexer
from sly import Parser
from util import column_types, get_hash


class FileListParser(Parser):
    # Get the token list from the lexer (required)
    tokens = FileListLexer.tokens
    # Omit LastAccessTime column from column_types
    lastwrite_types = column_types.copy()
    del lastwrite_types["LastAccessTime"]

    @_("block")
    def blocks(self, p):
        return p.block

    @_("blocks block")
    def blocks(self, p):
        # Join the list of blocks
        return pd.concat([p.blocks, p.block])

    @_("skip_literal DIR_PATH skip_literals file_list")
    def block(self, p):
        df: pd.DataFrame = p.file_list

        # Set values for all files
        df["ParentID"] = get_hash(PurePath(p.DIR_PATH))
        df["Path"] = PurePath(p.DIR_PATH) / df["Name"]
        df["Type"] = "File"
        df["NodeID"] = df["Path"].apply(lambda x: get_hash(x))

        # Set NodeID as index
        df = df.set_index("NodeID")

        # Add directory row
        df_dir = pd.DataFrame(
            {
                "Name": PurePath(p.DIR_PATH).name,
                "ParentID": get_hash(PurePath(p.DIR_PATH).parent),
                "Type": "Directory",
                "Size": 0,
                "Path": PurePath(p.DIR_PATH),
            },
            index=[get_hash(PurePath(p.DIR_PATH))],
        )
        df = pd.concat([df_dir, df])

        df = df.reindex(columns=self.lastwrite_types.keys())
        df = df.astype(self.lastwrite_types)

        return df

    @_("file_row")
    def file_list(self, p):
        return pd.DataFrame([p.file_row], columns=self.lastwrite_types.keys())

    @_("file_list file_row")
    def file_list(self, p):
        return pd.concat(
            [
                p.file_list,
                pd.DataFrame([p.file_row], columns=self.lastwrite_types.keys()),
            ]
        )

    @_("skip_mode DATETIME NUMBER FILENAME")
    def file_row(self, p):
        return pd.Series(
            index=self.lastwrite_types.keys(),
            data={
                "LastWriteTime": p.DATETIME,
                "Size": p.NUMBER,
                "Name": p.FILENAME,
            },
        )

    @_("skip_literal")
    def skip_literals(self, p):
        pass

    @_("skip_literals skip_literal")
    def skip_literals(self, p):
        pass

    @_(
        "SEPARATOR_LINE",
        "LITERAL_VERZEICHNIS",
        "LITERAL_MODE",
        "LITERAL_NAME",
        "LITERAL_LENGTH",
        "LITERAL_LAST_WRITE_TIME",
    )
    def skip_literal(self, p):
        pass

    @_("MODE")
    def skip_mode(self, p):
        pass
