tableList = {
    "STACKEXCHANGE_USER": ["USERID","REPUTATION",""],
}

import sqlite3
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
print(base_dir)
db_path = os.path.join(base_dir,"hushhush.db")
print(db_path)
print(f'db path is {db_path}')
con = sqlite3.connect(db_path,check_same_thread=False) # here db connection horha hae 
