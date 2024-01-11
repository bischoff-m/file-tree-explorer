import hashlib


def get_hash(s):
    if type(s) != str:
        s = str(s)
    return hashlib.md5(s.encode("utf-8")).hexdigest()


column_types = {
    "Name": str,  # Required
    "ParentID": str,  # Required
    "Path": str,  # Required
    "Size": "Int64",  # Required, may be any number >= 0
    "Type": str,  # May be "File", "Directory" or None/NaN
    "LastAccessTime": "datetime64[ns]",  # Optional
    "LastWriteTime": "datetime64[ns]",  # Optional
}
