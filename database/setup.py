import sqlite3



def setup_database():
  conn = sqlite3.connect('novels_tracker.db')

  cursor = conn.cursor()


  cursor.execute('''
    CREATE TABLE IF NOT EXISTS novels (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      url TEXT,
      image_url TEXT,
      image_path TEXT
    );
  ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS chapters (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      novel_id INTEGER NOT NULL,
      title TEXT NOT NULL,
      url TEXT,
      chapter_order FLOAT NOT NULL, 
      upload_date datetime NOT NULL,                   
      FOREIGN KEY (novel_id) REFERENCES novels(id)
    );
  ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS updates (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      chapter_id INTEGER NOT NULL,
      update_date datetime NOT NULL,
      FOREIGN KEY (chapter_id) REFERENCES chapters(id)
    );                                                  
  ''')

  conn.commit()
  conn.close()