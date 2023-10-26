from pathlib import Path, PurePath
import pandas as pd
from IPython.display import display
from util import get_hash

# NodeID: Name, ParentID, Type, Size, Path, LastWriteTime, LastAccessTime
column_types = {
    "Name": str,
    "ParentID": str,
    "Type": str,
    "Size": "Int64",
    "Path": str,
    "LastAccessTime": "datetime64[ns]",
}

data_dir = Path(__file__).parent.parent / "datasets"


def accesstime_df() -> pd.DataFrame:
    df_input = pd.read_csv(
        data_dir / "lastaccesstime_test.csv",
        parse_dates=["LastAccessTime"],
        date_format=f"%d.%m.%Y %H:%M:%S",
    )
    full_path = df_input["FullName"].map(lambda p: PurePath(p))
    df = pd.DataFrame(
        {
            "NodeID": full_path.map(lambda p: get_hash(p)),
            "Name": full_path.map(lambda p: p.name),
            "ParentID": full_path.map(lambda p: get_hash(p.parent)),
            "Type": None,
            "Size": 0,
            "Path": df_input["FullName"],
            "LastAccessTime": df_input["LastAccessTime"],
        }
    )
    df = df.set_index("NodeID")
    display(df)
    df.to_csv(data_dir / "result_lastaccess.csv", index=True, index_label="NodeID")


if __name__ == "__main__":
    accesstime_df()
