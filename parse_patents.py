import os
import json
import pprint
import pymysql
import warnings
import numpy as np
warnings.filterwarnings("ignore")

path_dir = os.path.join(os.getcwd(), "data")

db_config = {
            'host': "localhost",
            'port': 3306,
            'user': "root",
            'password': "0410",
            'db': "zhishi",
            'charset': 'utf8'
            }
_CONNECT = pymysql.connect(**db_config)
_SQL = "insert ignore into `company` (`company`) VALUES (%s)"

def db_executemany(cursor, sql, values):
    try:
        cursor.executemany(sql, values)
    except pymysql.err.IntegrityError:
        pass
    except pymysql.err.DataError:
        pass
    except pymysql.err.InternalError:
        pass

# 处理json.dumps的问题
def default_json(o):
    if isinstance(o, np.int64):
        return int(o)
    raise TypeError


# 存储list形式的文件
def save_list_to_file(filename, list):
    with open(filename, "w", encoding="utf-8") as f:
        for l in list:
            f.write(json.dumps(l, default=default_json) + "\n")


if __name__ == "__main__":
    with open(os.path.join(path_dir, "noCo")) as f:
        noCoPatterns = set()
        for line in f.readlines():
            line = line.strip()
            noCoPatterns.add(line) if len(line) > 0 else False

    cursor = _CONNECT.cursor()
    for file_name in os.listdir(os.path.join(path_dir, "raw")):
        print(file_name)
        result_set = set()
        path = os.path.join(path_dir, "raw", file_name)
        with open(path, "r", encoding="iso-8859-1") as f:
            for line in  f.readlines():
                items = line.split("|")
                if len(items) < 4:
                    continue
                try:
                    js = json.loads(items[3].strip())
                    for author_info in js["aa"]:
                        dAfN = author_info.setdefault("dAfN", None)
                        result_set.add(dAfN.lower()) if dAfN is not None else False
                except Exception as e:
                    # print(e)
                    continue
        result_list = list(filter(lambda x:  len(set(x.split(" ")).intersection(noCoPatterns)) < 1, list(result_set)))
        # print(result_list)
        db_executemany(cursor=cursor, sql=_SQL, values=result_list)
        _CONNECT.commit()
    else:
        _CONNECT.commit()
