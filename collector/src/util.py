import hashlib

def get_hash(s):
    if type(s) != str:
        s = str(s)
    return hashlib.md5(s.encode("utf-8")).hexdigest()