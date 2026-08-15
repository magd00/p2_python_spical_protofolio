"""
manage.py - the ONLY way to add a project to this portfolio now.

There is no public "Add Project" page or button on the website anymore -
visitors can only browse and view projects, they can't create, edit, or
delete anything. To add a new project, you (the site owner) run this
script yourself, either from the command line or by importing the
add_project() function in your own Python shell/script.

--------------------------------------------------------------------------
USAGE 1 - interactive command line:

    python manage.py

    It will ask you for each field one at a time.

OTHER COMMANDS:

    python manage.py --list          # show every project with its ID
    python manage.py --delete 7      # delete project #7

USAGE 2 - one-line command with arguments:

    python manage.py \
      --title "My New Project" \
      --description "Short one-line summary shown on the portfolio grid." \
      --full-description "Longer paragraph explaining how it works." \
      --category web \
      --technologies "Python, Flask" \
      --github-link "https://github.com/magd00/my_new_project" \
      --image /path/to/local/cover-image.png \
      --code-file /path/to/local/demo_snippet.py

USAGE 3 - import it and call it from your own script:

    from manage import add_project

    add_project(
        title="My New Project",
        description="Short one-line summary.",
        full_description="Longer paragraph.",
        category="web",           # one of: web, data, automation, api, game, desktop
        technologies="Python, Flask",
        github_link="https://github.com/magd00/my_new_project",
        image_path="/path/to/local/cover-image.png",   # optional
        code_snippet_path="/path/to/local/demo.py",    # optional - runs it to get output
    )
--------------------------------------------------------------------------
"""

import argparse
import os
import shutil
from datetime import datetime

from main import app, db, Project, execute_python_code

VALID_CATEGORIES = {"web", "data", "automation", "api", "game", "desktop"}


def add_project(
    title,
    description,
    full_description,
    category,
    technologies,
    github_link,
    demo_link=None,
    image_path=None,
    code_snippet=None,
    code_snippet_path=None,
):
    """
    Add a new project to the portfolio database.

    - image_path: path to a local image/SVG file on your computer. It gets
      copied into static/assets/img/portfolio/ so it shows up in the
      portfolio grid and project page, same as every other project.
      If omitted, a default placeholder image is used.
    - code_snippet / code_snippet_path: the Python code shown in the
      "Run Code" browser on the project's page. Pass the code as a string
      (code_snippet) OR a path to a .py file (code_snippet_path) - not
      both. It's run once here to capture real output, so the demo works
      immediately without anyone needing to click "Run" first (though they
      still can, to re-run it live).
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(f"category must be one of {sorted(VALID_CATEGORIES)}, got {category!r}")

    if code_snippet_path and code_snippet:
        raise ValueError("Pass either code_snippet or code_snippet_path, not both.")
    if code_snippet_path:
        with open(code_snippet_path) as f:
            code_snippet = f.read()

    image_filename = "default-project.jpg"
    if image_path:
        os.makedirs("static/assets/img/portfolio", exist_ok=True)
        ext = os.path.splitext(image_path)[1]
        image_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        shutil.copy(image_path, os.path.join("static/assets/img/portfolio", image_filename))

    code_output = None
    if code_snippet and code_snippet.strip():
        output, error = execute_python_code(code_snippet)
        code_output = output if output else (f"Error:\n{error}" if error else None)

    with app.app_context():
        project = Project(
            title=title,
            description=description,
            full_description=full_description,
            category=category,
            technologies=technologies,
            github_link=github_link,
            demo_link=demo_link,
            image=image_filename,
            code_snippet=code_snippet,
            code_output=code_output,
        )
        db.session.add(project)
        db.session.commit()
        print(f"✅ Added project #{project.id}: {title}")
        return project.id


def delete_project(project_id):
    """
    Delete a project by its ID (also removes its uploaded cover image from
    disk, unless it's the shared default placeholder). There's no button
    for this on the website anymore either - run it yourself, e.g.:

        python manage.py --delete 7

    or from your own script:

        from manage import delete_project
        delete_project(7)
    """
    with app.app_context():
        project = Project.query.get(project_id)
        if project is None:
            print(f"No project with id {project_id}.")
            return
        title = project.title
        if project.image and project.image != "default-project.jpg":
            image_path = os.path.join("static/assets/img/portfolio", project.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(project)
        db.session.commit()
        print(f"🗑️  Deleted project #{project_id}: {title}")


def list_projects():
    """Print every project currently in the database, with its id."""
    with app.app_context():
        projects = Project.query.order_by(Project.id).all()
        if not projects:
            print("No projects in the database.")
            return
        for p in projects:
            print(f"#{p.id:<3} [{p.category:<10}] {p.title}")


def _interactive():
    print("Add a new project to the portfolio (leave optional fields blank to skip)\n")
    title = input("Title: ").strip()
    description = input("Short description (1 line): ").strip()
    full_description = input("Full description (longer paragraph): ").strip()
    print(f"Category - one of {sorted(VALID_CATEGORIES)}")
    category = input("Category: ").strip()
    technologies = input("Technologies (e.g. 'Python, Flask'): ").strip()
    github_link = input("GitHub link: ").strip()
    demo_link = input("Live demo link (optional): ").strip() or None
    image_path = input("Path to a local cover image file (optional): ").strip() or None
    code_snippet_path = input("Path to a local .py file for the Run Code demo (optional): ").strip() or None

    add_project(
        title=title,
        description=description,
        full_description=full_description,
        category=category,
        technologies=technologies,
        github_link=github_link,
        demo_link=demo_link,
        image_path=image_path,
        code_snippet_path=code_snippet_path,
    )


def _cli():
    parser = argparse.ArgumentParser(description="Add a new project to the portfolio.")
    parser.add_argument("--title")
    parser.add_argument("--description")
    parser.add_argument("--full-description")
    parser.add_argument("--category", choices=sorted(VALID_CATEGORIES))
    parser.add_argument("--technologies")
    parser.add_argument("--github-link")
    parser.add_argument("--demo-link", default=None)
    parser.add_argument("--image", default=None, help="Path to a local cover image file")
    parser.add_argument("--code-file", default=None, help="Path to a local .py file for the Run Code demo")
    parser.add_argument("--delete", type=int, default=None, metavar="ID", help="Delete the project with this ID")
    parser.add_argument("--list", action="store_true", help="List all projects with their IDs")
    args = parser.parse_args()

    if args.list:
        list_projects()
        return

    if args.delete is not None:
        delete_project(args.delete)
        return

    if not any(v for k, v in vars(args).items() if k not in ("delete", "list")):
        _interactive()
        return

    required = [args.title, args.description, args.full_description, args.category,
                args.technologies, args.github_link]
    if not all(required):
        parser.error("When using flags, --title, --description, --full-description, "
                     "--category, --technologies, and --github-link are all required.")

    add_project(
        title=args.title,
        description=args.description,
        full_description=args.full_description,
        category=args.category,
        technologies=args.technologies,
        github_link=args.github_link,
        demo_link=args.demo_link,
        image_path=args.image,
        code_snippet_path=args.code_file,
    )


if __name__ == "__main__":
    _cli()
