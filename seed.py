"""
seed.py - re-initialize the live database on a new/fresh host.

Use this any time you point the site at a brand-new database (a fresh
Postgres instance, or a SQLite file that got wiped by a host restart) and
need the portfolio projects populated again.

USAGE:

    python seed.py            # create tables (if missing) + seed projects
    python seed.py --reset    # drop all tables first, then recreate + seed
                               # (WARNING: --reset deletes any projects you
                               # added by hand via manage.py)

This script reuses the exact same app config, models, and INITIAL_PROJECTS
data defined in main.py, so it always stays in sync with the live app -
there's nothing to duplicate or keep updated separately.
"""

import sys
from main import app, db, seed_initial_projects, Project


def run(reset: bool = False):
    with app.app_context():
        print(f"📁 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")

        if reset:
            confirm = input(
                "⚠️  --reset will DROP ALL TABLES and lose any manually-added "
                "projects. Type 'yes' to continue: "
            )
            if confirm.strip().lower() != "yes":
                print("Aborted.")
                return
            db.drop_all()
            print("🗑️  Dropped all tables.")

        db.create_all()
        print("✅ Tables ready.")

        before = Project.query.count()
        seed_initial_projects()
        after = Project.query.count()

        if after == before:
            print(f"ℹ️  Projects table already had {before} project(s) - nothing to seed.")
        else:
            print(f"✅ Seeded projects. Total projects now: {after}")


if __name__ == "__main__":
    run(reset="--reset" in sys.argv)
