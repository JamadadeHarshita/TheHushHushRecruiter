from contextlib import contextmanager
import sqlite3

@contextmanager
def cursor_handler(con):
    cur = con.cursor()
    yield cur
    cur.close()
    cur.commit()
    
def db_select(cur,query):
    try:
        cur.execute(query)
        rows = cur.fetchall()
    except Exception as error:
        print(str(error))
        
    return rows

def insert_query(cur,query):
    cur.execute(query)
    

def db_setup(cur):
    for eachtable, allcolumns in tableList.items():
        try:
            result = cur.execute(f"SELECT * FROM {eachtable}")
            print(f"table {eachtable} exists")
        except:
            if "no such table" in str(error):
                columnQuery = "(" + (",").join(allColumns)+ ")"
                cur.execute(f"CREATE TABLE {eachtable} {columnQuery}")
                print("table crated")
                
if __name__ == "__main__":
    from table_metadata import tableList,con
    with cursor_handler(con) as cur:
        db_setup(cur)
    
                
            