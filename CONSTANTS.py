import os
import sqlite3

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
GLOBAL_CONNECTION = sqlite3.connect(
    os.path.join(ROOT_DIR, "data", "Chinook.db"), check_same_thread=False
)
