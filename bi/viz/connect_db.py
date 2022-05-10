from dotenv import load_dotenv
import os
import mysql.connector as mc
import pandas as pd

load_dotenv()
######### TIDB
def runQuery_tidb(query):
    conn = mc.connect(host=os.getenv('TIDB_HOST'),
                      port=os.getenv('TIDB_PORT'),
                      user=os.getenv('TIDB_USER'),
                      password=os.getenv('TIDB_PW'),
                      database=os.getenv('TIDB_DEFAULT_DATABASE'))
    cur = conn.cursor()
    cur.execute(query)
    ### modify results
    columns = []
    for i in range(len(cur.description)):
        desc = cur.description[i]
        columns.append(str(desc[0]))
    data = pd.DataFrame(cur.fetchall(), columns=columns)
    ### disconnect and return
    # conn.disconnect
    return data