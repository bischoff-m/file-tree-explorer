###########################################################
# Export from DBeaver: DDL
###########################################################
# -- FileTree definition
# CREATE TABLE "FileTree" (
#     "nodeID" TEXT NOT NULL PRIMARY KEY,
#     "name" TEXT NOT NULL,
#     "parentID" TEXT NOT NULL,
#     "path" TEXT NOT NULL,
#     "size" BIGINT NOT NULL,
#     "type" TEXT NOT NULL,
#     "lastAccessTime" DATETIME,
#     "lastWriteTime" DATETIME
# );
# CREATE UNIQUE INDEX "FileTree_path_key" ON "FileTree"("path");


# %%
import sqlite3
from pathlib import Path

import pandas as pd
from IPython.display import display
from tqdm import tqdm
from util import column_types

data_dir = Path(__file__).parent.parent / "datasets"
db_path = Path(__file__).parent.parent.parent / "prisma" / "sqldata.db"

# %%

# Connect to database
con = sqlite3.connect(db_path)
cur = con.cursor()

# Drop table
cur.execute("DROP TABLE IF EXISTS FileTree")
con.commit()

# Create table
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS FileTree (
        "nodeID" TEXT NOT NULL PRIMARY KEY,
        "name" TEXT NOT NULL,
        "parentID" TEXT NOT NULL,
        "path" TEXT NOT NULL,
        "size" BIGINT NOT NULL,
        "type" TEXT NOT NULL,
        "lastAccessTime" DATETIME,
        "lastWriteTime" DATETIME
    );
    """
)
cur.execute(
    """
    CREATE UNIQUE INDEX IF NOT EXISTS "FileTree_path_key" ON "FileTree"("path");
    """
)
con.commit()

# %%
###########################################################
# Load data from csv
###########################################################

date_columns = ["LastAccessTime", "LastWriteTime"]
non_date_columns = {
    col: column_types[col] for col in column_types if col not in date_columns
}

df_input = pd.read_csv(
    data_dir / "result_combine.csv",
    index_col="NodeID",
    dtype=non_date_columns,
    parse_dates=date_columns,
    keep_default_na=False,
    na_values=[""],
)
# Rename columns to fit schema.prisma
df_target = df_input.rename(
    columns={
        "Name": "name",
        "ParentID": "parentID",
        "Type": "type",
        "Size": "size",
        "Path": "path",
        "LastWriteTime": "lastWriteTime",
        "LastAccessTime": "lastAccessTime",
    }
)
df_target.index.name = "nodeID"

# Get rows where name is of type float
name_float = df_target[df_target["name"].map(type) == float]
assert (
    len(name_float) == 1
), "There should be exactly one row with name of \
    type float that is the root directory (e.g. C:\\)"

# Get rows where type is of type float
type_float = df_target[df_target["type"].map(type) == float]
assert type_float["type"].isna().all(), "All rows with type of type float should be NaN"

# Fill NaN values
df_target["name"].fillna("", inplace=True)  # "" corresponds to root directory
df_target["type"].fillna("Unknown", inplace=True)

verbose = False
if verbose:
    print(f"\n###### Dtypes")
    display({col: f"{df_target[col].dtype}" for col in df_target.columns})

    print(f"\n###### Unique types")
    display({col: list(df_target[col].map(type).unique()) for col in df_target.columns})

    print(f"\n###### Unique values for column 'type'")
    print(f"type: {list(df_target['type'].unique())}")

    display(df_target["size"].describe())


# Assign index to nodeID column
df_target.reset_index(inplace=True)

# Replace lastAccessTime and lastWriteTime with time in milliseconds
df_target["lastAccessTime"] = df_target["lastAccessTime"].apply(
    lambda x: x.timestamp() * 1000 if pd.notna(x) else None
)
df_target["lastWriteTime"] = df_target["lastWriteTime"].apply(
    lambda x: x.timestamp() * 1000 if pd.notna(x) else None
)
display(df_target.head())


# %%
###########################################################
# Insert data into database
###########################################################

# Split into chunks
chunksize = 100000
chunks = [df_target[i : i + chunksize] for i in range(0, len(df_target), chunksize)]

# Insert chunks
# for chunk in tqdm(chunks, total=len(chunks)):
for chunk in tqdm(chunks, total=len(chunks)):
    try:
        cur.executemany(
            """
            INSERT INTO FileTree
            VALUES (
                :nodeID,
                :name,
                :parentID,
                :path,
                :size,
                :type,
                :lastAccessTime,
                :lastWriteTime
            );
            """,
            chunk.to_dict("records"),
        )
        con.commit()
    except Exception as e:
        print(e)
        break

# %%

print("Done")
con.close()

# %%
