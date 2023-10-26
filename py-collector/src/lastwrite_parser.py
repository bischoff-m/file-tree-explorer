# pyright: reportUndefinedVariable=false

from sly import Parser
from pathlib import PurePath
import pandas as pd
from lastwrite_lexer import FileListLexer
from util import get_hash


class FileListParser(Parser):
    # debugfile = "parser.out"
    # Get the token list from the lexer (required)
    tokens = FileListLexer.tokens

    # NodeID: Name, ParentID, Type, Size, Path, LastWriteTime, LastAccessTime
    column_types = {
        "Name": str,
        "ParentID": str,
        "Type": str,
        "Size": "Int64",
        "Path": str,
        "LastWriteTime": "datetime64[ns]",
    }

    @_("block")
    def blocks(self, p):
        # Check if blocks contains the special numbers -684402285 and 3610565011
        if p.block["Size"].isin([-684402285, 3610565011]).any():
            print(f"Found special number in blocks: {p.block['Size']}")
        return p.block

    @_("blocks block")
    def blocks(self, p):
        # Check if blocks contains the special numbers -684402285 and 3610565011
        if p.block["Size"].isin([-684402285, 3610565011]).any():
            print(f"Found special number in blocks: {p.block['Size']}")
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

        df = df.reindex(columns=self.column_types.keys())
        df = df.astype(self.column_types)

        return df

    @_("file_row")
    def file_list(self, p):
        return pd.DataFrame([p.file_row], columns=self.column_types.keys())

    @_("file_list file_row")
    def file_list(self, p):
        return pd.concat(
            [
                p.file_list,
                pd.DataFrame([p.file_row], columns=self.column_types.keys()),
            ]
        )

    @_("skip_mode DATETIME NUMBER FILENAME")
    def file_row(self, p):
        if int(p.NUMBER) == -684402285 or int(p.NUMBER) == 3610565011:
            print(f"Found special number in file_row: {p.NUMBER} {p.FILENAME}")
        return pd.Series(
            index=self.column_types.keys(),
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
