import sqlite3
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"data"/"pixelai.sqlite3"

def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    return con

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS images(
        id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, path TEXT NOT NULL,
        caption TEXT DEFAULT '', mime_type TEXT DEFAULT 'image/jpeg', created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS versions(
        id INTEGER PRIMARY KEY AUTOINCREMENT, image_id INTEGER NOT NULL, version_no INTEGER NOT NULL,
        path TEXT NOT NULL, prompt TEXT NOT NULL, created_at TEXT NOT NULL,
        FOREIGN KEY(image_id) REFERENCES images(id))""")

def add_image(filename,path,caption="",mime_type="image/jpeg"):
    with connect() as c:
        cur=c.execute("INSERT INTO images(filename,path,caption,mime_type,created_at) VALUES(?,?,?,?,?)",
          (filename,path,caption,mime_type,datetime.now().isoformat(timespec="seconds")))
        return cur.lastrowid

def update_caption(image_id,caption):
    with connect() as c: c.execute("UPDATE images SET caption=? WHERE id=?",(caption,image_id))

def list_images():
    with connect() as c: return [dict(r) for r in c.execute("SELECT * FROM images ORDER BY id DESC")]

def get_image(image_id):
    with connect() as c:
        row=c.execute("SELECT * FROM images WHERE id=?",(image_id,)).fetchone()
        return dict(row) if row else None

def add_version(image_id,path,prompt):
    with connect() as c:
        row=c.execute("SELECT COALESCE(MAX(version_no),0)+1 n FROM versions WHERE image_id=?",(image_id,)).fetchone()
        n=int(row["n"])
        c.execute("INSERT INTO versions(image_id,version_no,path,prompt,created_at) VALUES(?,?,?,?,?)",
          (image_id,n,path,prompt,datetime.now().isoformat(timespec="seconds")))
        return n

def list_versions(image_id):
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM versions WHERE image_id=? ORDER BY version_no DESC",(image_id,))]
