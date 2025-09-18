# Database.py
import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = pyodbc.connect(
                f"DRIVER={{SQL Server}};"
                f"SERVER={os.getenv('DB_SERVER')};"
                f"DATABASE={os.getenv('DB_DATABASE')};"
                f"UID={os.getenv('DB_USERNAME')};"
                f"PWD={os.getenv('DB_PASSWORD')}"
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise Exception(f"Chyba připojení k databázi: {str(e)}")

    def create_ignored_table(self):
        self.cursor.execute("""
            IF OBJECT_ID('tempdb..#IgnoredCodes') IS NOT NULL
                DROP TABLE #IgnoredCodes
            CREATE TABLE #IgnoredCodes (
                SivCode NVARCHAR(255) PRIMARY KEY
            )
        """)

    def insert_ignored_codes(self, codes):
        self.cursor.executemany(
            "INSERT INTO #IgnoredCodes VALUES (?)",
            [(code,) for code in codes]
        )

    def get_products(self, limit=100):
        query = f"""
            SELECT TOP {limit} SivCode
            FROM {os.getenv('DB_TABLE')}
            WHERE SivNoteSca = ''
            AND SivComId = 32611
            AND SivOrdVen = 1
            AND (SivStiId IS NOT NULL OR SivStiId != '')
            AND NOT EXISTS (
                SELECT 1 FROM #IgnoredCodes 
                WHERE SivCode = {os.getenv('DB_TABLE')}.SivCode COLLATE DATABASE_DEFAULT
            )
            ORDER BY NEWID()
        """
        self.cursor.execute(query)
        return [{'SivCode': row[0]} for row in self.cursor.fetchall()]

    def update_products(self, updates):
        query = f"""
            UPDATE {os.getenv('DB_TABLE')}
            SET SivNoteSca = ?
            WHERE SivCode = ?
            AND SivComId = 32611
        """
        self.cursor.executemany(query, updates)
        self.connection.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
