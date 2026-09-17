"""MySQL Connector/Python 9.2+ multi-statement execution for trusted SQL files."""
from pathlib import Path


def execute_script(connection, path: Path) -> None:
    with connection.cursor() as cursor:
        cursor.execute(path.read_text(encoding="utf-8"))
        while True:
            if cursor.with_rows:
                cursor.fetchall()
            if not cursor.nextset():
                break
    connection.commit()
