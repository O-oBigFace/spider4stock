import os
import spider4stocks
import pymysql
from Logger import logger
import json
import time

_PATH_DIR_RESULT = os.path.join(os.getcwd(), "result")
_PATH_DIR_COMPANY = os.path.join(os.getcwd(), "result", "company")

db_config = {
            'host': "localhost",
            'port': 3306,
            'user': "root",
            'password': "0410",
            'db': "zhishi",
            'charset': 'utf8'
            }
_CONNECT = pymysql.connect(**db_config)
_SQL_QUERY = "select company from company where id = %s"
_CURSOR = _CONNECT.cursor()


def save_dict_to_file(filename, d):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(d))

d = dict()

for name in os.listdir(_PATH_DIR_COMPANY):
    _CURSOR.execute(_SQL_QUERY % name)
    company = _CURSOR.fetchone()[0]

    with open(os.path.join(_PATH_DIR_COMPANY, name), "r", encoding="utf-8") as f:
        c = json.loads(f.read().strip())
        d[company] = c.setdefault("Market_Cap", "N/A")

save_dict_to_file("MC.json", d)
