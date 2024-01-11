from pathlib import Path, PurePath

import pandas as pd
from IPython.display import display
from tqdm import tqdm
from util import column_types, get_hash


def join(df1: pd.DataFrame, df2: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    # df1: NodeID,Name,ParentID,Type,Size,Path,LastAccessTime
    # df2: NodeID,Name,ParentID,Type,Size,Path,LastWriteTime

    # Check that no values are missing for required columns
    for col in ["Name", "ParentID", "Size", "Path"]:
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            display(df1[df1[col].isna()])
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            display(df2[df2[col].isna()])
        assert not df1[col].isna().any(), f"Missing values in {col} in df1"
        assert not df2[col].isna().any(), f"Missing values in {col} in df2"

    # Add empty columns if optional columns are missing
    df1 = df1.reindex(columns=column_types.keys())
    df2 = df2.reindex(columns=column_types.keys())
    # Fill NaN values in Type column to avoid converting NaN (float) to "nan" (str)
    df1 = df1.fillna({"Type": ""})
    df2 = df2.fillna({"Type": ""})
    # Convert columns to correct types
    df1 = df1.astype(column_types)
    df2 = df2.astype(column_types)
    # Convert empty strings to NaN
    df1 = df1.replace({"Type": {"": None}})
    df2 = df2.replace({"Type": {"": None}})

    # Merge the two dataframes
    df = df1.merge(df2, on="NodeID", suffixes=("_1", "_2"), how="outer")

    # Replace 0 with NaN to merge Size columns
    df["Size_1"] = df["Size_1"].replace(0, pd.NA)
    df["Size_2"] = df["Size_2"].replace(0, pd.NA)

    if verbose:
        print(
            f"Number of elements in intersection: {len(df1.index.intersection(df2.index))}"
        )

    # Merge all columns
    for col in column_types.keys():
        col1 = df[f"{col}_1"]
        col2 = df[f"{col}_2"]

        # Check that the Name columns are not overlapping
        overlap = df[col1.notna() & col2.notna()]
        if verbose:
            print(f"Overlap for {col}: {len(overlap)}")
        if not overlap[col1.name].equals(overlap[col2.name]):
            raise ValueError(f"{col}_1 and {col}_2 columns are not the same")

        # Fill missing values in Name column
        df[col] = col1.fillna(col2)
        # Drop the {col}_1 and {col}_2 columns
        df.drop(columns=[f"{col}_1", f"{col}_2"], inplace=True)

    # Set type of Size column to int
    df["Size"] = df["Size"].fillna(0).astype(column_types["Size"])

    # Recursively add parent directories
    df_parents = pd.DataFrame(columns=["Name", "ParentID", "Path", "Size", "Type"])
    for row in tqdm(df.itertuples(), total=len(df), desc="Adding parent directories"):
        current_path = PurePath(row.Path)
        for parent in current_path.parents:
            parent_id = get_hash(parent)
            name = parent.name
            if name == "":
                name = current_path.anchor
            if parent_id not in df.index and parent_id not in df_parents.index:
                df_parents.loc[parent_id] = [
                    parent.name,
                    get_hash(parent.parent),
                    parent,
                    0,
                    "Directory",
                ]
            else:
                if parent_id in df.index and df.loc[parent_id, "Type"] is None:
                    df.loc[parent_id, "Type"] = "Directory"
                # Stop when the parent is already in the dataframe
                break

    # Join the parent directories to the dataframe
    df = pd.concat([df_parents, df])

    # Post conditions
    print("Testing post conditions")
    assert df["ParentID"].notna().all(), "ParentID is NaN"
    assert df["ParentID"].isin(df.index).all(), "ParentID not in index"

    # Calculate Size, LastAccessTime, LastWriteTime for directories
    levels = df["Path"].map(lambda p: len(PurePath(p).parts))
    for level in tqdm(
        range(levels.max(), 0, -1),
        desc="Calculating Size, LastAccessTime, LastWriteTime",
    ):
        if verbose:
            print(f"\n\n############ Level {level}")
        df_level = df[levels.eq(level)]
        for col, condition_child, condition_parent, new_values in [
            (
                "Size",
                lambda x: x["Size"] > 0,
                lambda x: x["Size"] == 0,
                lambda p, g: df.loc[p, "Size"] + g["Size"].sum(),
            ),
            (
                "LastAccessTime",
                lambda x: x["LastAccessTime"].notna(),
                lambda x: x["LastAccessTime"].isna(),
                lambda p, g: g["LastAccessTime"].max(),
            ),
            (
                "LastWriteTime",
                lambda x: x["LastWriteTime"].notna(),
                lambda x: x["LastWriteTime"].isna(),
                lambda p, g: g["LastWriteTime"].max(),
            ),
        ]:
            if verbose:
                print(f"\n###### {col}")

            # Get which parents have children with a value for the column
            groupby_parent = df_level[condition_child(df_level)].groupby("ParentID")
            parent_ids = pd.Index(groupby_parent.groups.keys())
            if len(parent_ids) == 0:
                if verbose:
                    print("No parents")
                continue

            # Drop parents that already have a size
            parents = df.loc[parent_ids]
            parents = parents[condition_parent(parents)]
            if verbose:
                print(f"Number of parents before filter: {len(parent_ids)}")
            parent_ids = parents.index
            if verbose:
                print(f"Number of parents after filter: {len(parent_ids)}")

            # Aggregate the values
            df.loc[parent_ids, col] = new_values(parent_ids, groupby_parent)

    df["Type"].fillna("Unknown", inplace=True)
    return df


if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "datasets"
    # Required in the sense that the columns must be in df.columns
    required_columns = ["Name", "ParentID", "Path", "Size", "Type"]
    optional_columns = ["LastAccessTime", "LastWriteTime"]
    options = {
        "index_col": "NodeID",
        "dtype": {col: column_types[col] for col in required_columns},
        "keep_default_na": False,
        "na_values": [""],
    }

    df1 = pd.read_csv(
        data_dir / "result_lastaccess.csv", parse_dates=["LastAccessTime"], **options
    )
    df2 = pd.read_csv(
        data_dir / "result_lastwrite.csv", parse_dates=["LastWriteTime"], **options
    )

    verbose = True
    df = join(df1, df2, verbose)

    if verbose:
        display(df.head())
        display(df.describe(include="all"))
        display(df.dtypes)

    df.to_csv(data_dir / "result_combine.csv", index=True, index_label="NodeID")
