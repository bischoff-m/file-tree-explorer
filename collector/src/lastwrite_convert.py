from lastwrite_lexer import FileListLexer
from lastwrite_parser import FileListParser
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from IPython.display import display


if __name__ == "__main__":
    filename = "lastwritetime.txt"
    # filename = "lastwritetime_test.txt"
    data_dir = Path(__file__).parent.parent / "datasets"
    with open(data_dir / filename, "r", encoding="utf-16le") as f:
        lines = f.readlines()
    data = "".join(lines)

    lexer = FileListLexer()
    parser = FileListParser()

    # TODO: Post process data frame to calculate Size, LastWriteTime, LastAccessTime for
    # directories and add intermediate directories
    def tokenize(data):
        with tqdm(total=len(lines)) as pbar:
            for idx, token in enumerate(lexer.tokenize(data)):
                # if idx > 100 or not token:
                #     break
                # print(token.type, str(token.value).replace("\n", "\\n"))
                # print(lexer.lineno)
                pbar.update(lexer.lineno - pbar.n)
                yield token

    # TQDM: 228476it [00:52, 4312.01it/s]
    # TQDM: 228476it [00:45, 4990.66it/s]
    try:
        df: pd.DataFrame = parser.parse(tokenize(data))
        if df is not None:
            display(df)
            display(df.dtypes)
            df.to_csv(
                data_dir / "result_lastwrite.csv", index=True, index_label="NodeID"
            )
        else:
            print("No result")
    except EOFError:
        print("EOFError")
