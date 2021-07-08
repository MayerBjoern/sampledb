# coding: utf-8
"""
Drop short_description_as_html column from instruments table.
"""

import os

MIGRATION_INDEX = 64
MIGRATION_NAME, _ = os.path.splitext(os.path.basename(__file__))


def run(db):
    # Skip migration by condition
    column_names = db.session.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'instruments'
        """).fetchall()
    if ('short_description_as_html',) not in column_names:
        return False

    # Perform migration
    db.session.execute("""
            ALTER TABLE instruments
            DROP COLUMN short_description_as_html
        """)

    return True