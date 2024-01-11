from pathlib import Path, PurePath

import pandas as pd
from IPython.display import display
from util import column_types, get_hash

lastaccess_types = column_types.copy()
del lastaccess_types["LastWriteTime"]

data_dir = Path(__file__).parent.parent / "datasets"


def accesstime_df(df_input: pd.DataFrame) -> pd.DataFrame:
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
    return df


if __name__ == "__main__":
    df_input = pd.read_csv(
        data_dir / "lastaccesstime.csv",
        parse_dates=["LastAccessTime"],
    )
    df = accesstime_df(df_input)
    display(df)
    df.to_csv(data_dir / "result_lastaccess.csv", index=True, index_label="NodeID")
