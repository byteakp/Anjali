import sqlite3
import json
from datetime import datetime
import chromadb
from chromadb.config import Settings
import uuid
from config import DB_PATH, CHROMA_PERSIST_DIR, RELATIONSHIP_LEVELS

class MemoryDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_sqlite()
        self.init_chromadb()

    def init_sqlite(self):
        """Initialize SQLite database for structured memory and relationship storage"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_info (
                key TEXT PRIMARY KEY, value TEXT
            )''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT, timestamp TIMESTAMP, mood TEXT
            )''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT, memory_type TEXT, content TEXT, importance INTEGER, created_at TIMESTAMP, context TEXT
            )''')
        # New table for relationship tracking
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationship_metrics (
                id INTEGER PRIMARY KEY, interaction_count INTEGER DEFAULT 0, positive_interactions INTEGER DEFAULT 0,
                negative_interactions INTEGER DEFAULT 0, relationship_points INTEGER DEFAULT 0
            )''')
        # Ensure a single row exists for metrics
        self.cursor.execute("INSERT OR IGNORE INTO relationship_metrics (id) VALUES (1)")
        self.conn.commit()

    def init_chromadb(self):
        """Initialize ChromaDB for semantic memory search"""
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR, settings=Settings(anonymized_telemetry=False))
        self.collection = self.chroma_client.get_or_create_collection(name="anjali_memories", metadata={"hnsw:space": "cosine"})

    def save_user_info(self, key, value):
        self.cursor.execute('INSERT OR REPLACE INTO user_info (key, value) VALUES (?, ?)', (key, value))
        self.conn.commit()

    def get_user_info(self, key):
        self.cursor.execute('SELECT value FROM user_info WHERE key = ?', (key,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def save_conversation(self, role, content, mood="friendly"):
        self.cursor.execute('INSERT INTO conversations (role, content, timestamp, mood) VALUES (?, ?, ?, ?)', (role, content, datetime.now(), mood))
        self.conn.commit()

    def get_recent_conversations(self, limit=10):
        self.cursor.execute('SELECT role, content FROM conversations ORDER BY timestamp DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def save_memory(self, content, memory_type="general", importance=5, context=""):
        memory_id = str(uuid.uuid4())
        self.cursor.execute('INSERT INTO memories (memory_type, content, importance, created_at, context) VALUES (?, ?, ?, ?, ?)',
                           (memory_type, content, importance, datetime.now(), context))
        self.conn.commit()
        self.collection.add(documents=[content], metadatas=[{"type": memory_type, "importance": importance, "context": context, "timestamp": str(datetime.now())}], ids=[memory_id])

    def search_memories(self, query, n_results=5):
        return self.collection.query(query_texts=[query], n_results=n_results)

    def get_all_memories(self):
        self.cursor.execute('SELECT id, memory_type, content, importance, created_at, context FROM memories ORDER BY created_at DESC')
        return self.cursor.fetchall()
        
    def get_relationship_status(self):
        self.cursor.execute("SELECT interaction_count, positive_interactions, relationship_points FROM relationship_metrics WHERE id = 1")
        res = self.cursor.fetchone()
        if not res: return {"level": "Acquaintance", "points": 0}
        
        points = res[2]
        level = "Acquaintance"
        for point_threshold, name in RELATIONSHIP_LEVELS.items():
            if points >= point_threshold:
                level = name
        return {"level": level, "points": points, "interactions": res[0], "positive": res[1]}

    def update_interaction_metrics(self, sentiment: str):
        points_change = 0
        pos_change = 0
        neg_change = 0

        if sentiment == "positive":
            points_change = 2
            pos_change = 1
        elif sentiment == "negative":
            points_change = -1
            neg_change = 1
        else: # neutral
            points_change = 1

        self.cursor.execute("""
            UPDATE relationship_metrics
            SET interaction_count = interaction_count + 1,
                positive_interactions = positive_interactions + ?,
                negative_interactions = negative_interactions + ?,
                relationship_points = relationship_points + ?
            WHERE id = 1
        """, (pos_change, neg_change, points_change))
        self.conn.commit()

    def delete_memory(self, memory_id):
        self.cursor.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
        self.conn.commit()

    def clear_all_memories(self):
        self.cursor.execute('DELETE FROM memories')
        self.cursor.execute('DELETE FROM conversations')
        self.cursor.execute('DELETE FROM user_info')
        # Reset relationship as well
        self.cursor.execute('UPDATE relationship_metrics SET interaction_count=0, positive_interactions=0, negative_interactions=0, relationship_points=0 WHERE id=1')
        self.conn.commit()
        self.chroma_client.delete_collection("anjali_memories")
        self.init_chromadb()