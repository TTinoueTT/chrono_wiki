#!/usr/bin/env python3
"""
SQLiteデータベースの内容を確認するスクリプト
"""

import sqlite3
from pathlib import Path


def check_database():
    """データベースの内容を確認"""
    db_path = Path("test.db")

    if not db_path.exists():
        print("データベースファイルが見つかりません")
        return

    print(f"データベースファイル: {db_path}")
    print(f"ファイルサイズ: {db_path.stat().st_size} bytes")
    print("-" * 50)

    # SQLiteに接続
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # テーブル一覧を取得
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("テーブル一覧:")
    for table in tables:
        table_name = table[0]
        print(f"  - {table_name}")

        # 各テーブルの構造を確認
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        print("    カラム:")
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            pk_mark = " (PK)" if pk else ""
            not_null_mark = " NOT NULL" if not_null else ""
            print(f"      {col_name}: {col_type}{not_null_mark}{pk_mark}")

        # 各テーブルのレコード数を確認
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"    レコード数: {count}")

        # 最初の数件のデータを表示
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            rows = cursor.fetchall()
            print("    サンプルデータ:")
            for row in rows:
                print(f"      {row}")

        print()

    conn.close()


if __name__ == "__main__":
    check_database()
 