import os
import spider4stocks
import pymysql
from Logger import logger
import json

_PATH_DIR_RESULT = os.path.join(os.getcwd(), "result")
_PATH_DIR_RECORD = os.path.join(os.getcwd(), "result", "record")

db_config = {
            'host': "localhost",
            'port': 3306,
            'user': "root",
            'password': "0410",
            'db': "zhishi",
            'charset': 'utf8'
            }
_CONNECT = pymysql.connect(**db_config)
_SQL_QUERY = "select id, company from company where id >= %d and id < %d"
cursor = _CONNECT.cursor()


def spider(_lock, _begin, _end):
    logger.info("Begin: %d| End: %d" % (_begin, _end))
    # 查询
    _lock.acquire()
    try:
        cursor.execute(_SQL_QUERY % (_begin, _end))
        company_list = cursor.fetchall()
    except Exception as e:
        logger.error("ERROR: %s | Begin: %d | End: %d" % (str(e), _begin, _end))
        return
    finally:
        _lock.release()

    for id, company in company_list:
        with open(os.path.join(_PATH_DIR_RECORD, "%d" % id), "w", encoding="utf-8") as f:
            pass

        # 查找
        stock = None
        MC = "N/A"
        _generator = spider4stocks.search_stock(company)
        while MC == "N/A":
            try:
                stock = next(_generator).fill()
                MC = stock.Market_Cap
            except StopIteration as e:
                break
            except Exception as e:
                continue

        # 存储
        if stock:
            with open(os.path.join(_PATH_DIR_RESULT, "%d" % id), "w", encoding="utf-8") as f:
                logger.info("Company: %s | Info: %s | Market Cap: %s" % (company, stock.Stock_Name, stock.Market_Cap))
                f.write(json.dumps(stock.get_attr_dict()))


if __name__ == '__main__':
    from multiprocessing import Lock
    lock = Lock()
    spider(lock, 1, 10)
