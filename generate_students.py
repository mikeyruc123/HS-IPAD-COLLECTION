import sqlite3

DATABASE = "data/students.db"

def main():

    db = sqlite3.connect(DATABASE)
    cur = db.cursor()

    i = 999999999
    while i < 65536:
        cur.execute(f"INSERT INTO students VALUES ({i}, 'FIRST LAST', 0, 0, 0)")
        i = i+1

    db.commit()

    cur.execute("SELECT * FROM students")

    if db is not None:
        db.close()
    
if __name__ == "__main__":
    main()