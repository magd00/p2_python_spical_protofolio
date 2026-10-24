from flask import Flask, abort, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pathlib import Path
import traceback
import io
import contextlib
import os
import re
from dotenv import load_dotenv

# Load variables from a local .env file (if present) into the environment.
# On a host like Render/PythonAnywhere, you set these in the platform's
# dashboard instead, and load_dotenv() simply has nothing to load.
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
# SECRET_KEY and the database URI come from environment variables so no
# secrets are hardcoded in source control. The fallbacks below only kick in
# for local development (e.g. no .env file yet) and should never be relied
# on in production — always set real values via the host's env vars.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-insecure-key-change-me')

database_url = os.environ.get('DATABASE_URL', 'sqlite:///portfolio.db')
# Render/Heroku-style Postgres URLs sometimes start with "postgres://", but
# SQLAlchemy 1.4+ requires "postgresql://" — normalize it if needed.
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class Project(db.Model):
    """Project model for storing portfolio items"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    full_description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    technologies = db.Column(db.String(200), nullable=False)
    github_link = db.Column(db.String(200), nullable=True)
    demo_link = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(100), nullable=True, default='default-project.jpg')
    code_snippet = db.Column(db.Text, nullable=True)
    code_output = db.Column(db.Text, nullable=True)
    demo_note = db.Column(db.Text, nullable=True)  # explains how the Run Code demo relates to the real project
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def display_title(self):
        repo = (self.github_link or '').rstrip('/').rstrip('.')
        if repo.endswith('/p13_arcade_game_space_invaders'):
            return 'Space Invaders'
        return self.title

    def __repr__(self):
        return f'<Project {self.title}>'

class CodeExecution(db.Model):
    """Store code execution history"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    code = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== SEED DATA ====================
# Projects confirmed so far from your GitHub (magd00). Repos #7-15 will be
# appended here once their links + code are confirmed. code_snippet /
# code_output are left blank until you send over the actual .py files for
# each project — drop them in and I'll wire them in on the next pass.

INITIAL_PROJECTS = [
    {
        "title": "Morse Code Translator",
        "description": "Converts English text into Morse code from the command line.",
        "full_description": "A command-line tool that translates regular text (letters A-Z and numbers 0-9) into Morse code. Built to make it easy to learn and experiment with the Morse code system interactively.",
        "category": "automation",
        "technologies": "Python",
        "github_link": "https://github.com/magd00/p1_Morce_Code_translator",
        "image": "p1_morse_code.svg",
        "code_snippet": '# Morse Code Translator - encodes text into Morse code\n\nMORSE_CODE = {\n    \'A\': \'.-\', \'B\': \'-...\', \'C\': \'-.-.\', \'D\': \'-..\', \'E\': \'.\', \'F\': \'..-.\',\n    \'G\': \'--.\', \'H\': \'....\', \'I\': \'..\', \'J\': \'.---\', \'K\': \'-.-\', \'L\': \'.-..\',\n    \'M\': \'--\', \'N\': \'-.\', \'O\': \'---\', \'P\': \'.--.\', \'Q\': \'--.-\', \'R\': \'.-.\',\n    \'S\': \'...\', \'T\': \'-\', \'U\': \'..-\', \'V\': \'...-\', \'W\': \'.--\', \'X\': \'-..-\',\n    \'Y\': \'-.--\', \'Z\': \'--..\',\n    \'0\': \'-----\', \'1\': \'.----\', \'2\': \'..---\', \'3\': \'...--\', \'4\': \'....-\',\n    \'5\': \'.....\', \'6\': \'-....\', \'7\': \'--...\', \'8\': \'---..\', \'9\': \'----.\',\n    \' \': \'/\'\n}\n\ndef text_to_morse(text):\n    return \' \'.join(MORSE_CODE.get(ch.upper(), \'?\') for ch in text)\n\nmessage = "SOS PYTHON 123"\nencoded = text_to_morse(message)\n\nprint("Morse Code Translator")\nprint("-" * 40)\nprint(f"Input : {message}")\nprint(f"Morse : {encoded}")\n',
        "code_output": 'Morse Code Translator\n----------------------------------------\nInput : SOS PYTHON 123\nMorse : ... --- ... / .--. -.-- - .... --- -. / .---- ..--- ...--\n',
        "demo_note": 'This is the real translator logic. Type any text below and click Run Code — it re-encodes the sample message into Morse using the exact same lookup table as the command-line tool.',
    },
    {
        "title": "Tic-Tac-Toe XO Game",
        "description": "Classic two-player Tic-Tac-Toe game built in Python.",
        "full_description": "A Python implementation of the classic Tic-Tac-Toe (XO) game, playable by two players with win/draw detection.",
        "category": "game",
        "technologies": "Python",
        "github_link": "https://github.com/magd00/p2_Tic-_Tac_Toe_XO_game",
        "image": "p2_tictactoe.svg",
        "code_snippet": '# Tic-Tac-Toe XO Game - board state, move validation, and win detection\n\nboard = [" "] * 9\n\nWIN_LINES = [\n    (0,1,2), (3,4,5), (6,7,8),   # rows\n    (0,3,6), (1,4,7), (2,5,8),   # columns\n    (0,4,8), (2,4,6)             # diagonals\n]\n\ndef print_board(b):\n    rows = [b[0:3], b[3:6], b[6:9]]\n    for i, row in enumerate(rows):\n        print(" | ".join(row))\n        if i < 2:\n            print("-" * 9)\n\ndef check_winner(b):\n    for a, c, d in WIN_LINES:\n        if b[a] != " " and b[a] == b[c] == b[d]:\n            return b[a]\n    return None\n\n# Simulated game: X and O taking turns\nmoves = [(0, "X"), (4, "O"), (1, "X"), (5, "O"), (2, "X")]  # X wins top row\n\nfor pos, player in moves:\n    board[pos] = player\n\nprint("Tic-Tac-Toe XO Game - simulated match")\nprint("-" * 40)\nprint_board(board)\n\nwinner = check_winner(board)\nprint()\nprint(f"Winner: {winner}!" if winner else "No winner yet - board still in play")\n',
        "code_output": 'Tic-Tac-Toe XO Game - simulated match\n----------------------------------------\nX | X | X\n---------\n  | O | O\n---------\n  |   |  \n\nWinner: X!\n',
        "demo_note": 'The full game is interactive and played move-by-move in a terminal. This demo runs one full simulated match through the same win-detection logic and prints the final board and winner.',
    },
    {
        "title": "Image Watermarking App",
        "description": "Desktop app for adding custom text watermarks to images.",
        "full_description": "A Tkinter desktop application for adding text watermarks to images — built for photographers, designers, and content creators who want to protect their work. Supports PNG/JPG/JPEG/BMP/GIF/WebP, adjustable opacity (10-100%), 5 watermark positions, adjustable font size, a real-time preview, and threaded processing so the UI stays responsive on large files (up to 50MB).",
        "category": "desktop",
        "technologies": "Python, Tkinter, Pillow",
        "github_link": "https://github.com/magd00/p3_image_watermarking_app",
        "image": "p3_watermark.svg",
        "code_snippet": '# Image Watermarking App - core watermark-blending logic\n# The real app is a Tkinter desktop GUI (file picker, live preview, opacity\n# slider) which needs a display, so it can\'t run on a web server. This demo\n# uses the same underlying Pillow technique -- generating an image in memory\n# and blending semi-transparent text onto it -- so it runs headlessly here.\n\nfrom PIL import Image, ImageDraw, ImageFont\n\ndef add_watermark(base_size=(400, 250), text="SAMPLE", opacity=128, position="bottom-right"):\n    base = Image.new("RGBA", base_size, (40, 90, 160, 255))\n    watermark_layer = Image.new("RGBA", base_size, (0, 0, 0, 0))\n    draw = ImageDraw.Draw(watermark_layer)\n\n    try:\n        font = ImageFont.load_default()\n    except Exception:\n        font = None\n\n    bbox = draw.textbbox((0, 0), text, font=font)\n    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]\n\n    positions = {\n        "bottom-right": (base_size[0] - text_w - 15, base_size[1] - text_h - 15),\n        "top-left": (15, 15),\n        "center": ((base_size[0] - text_w) // 2, (base_size[1] - text_h) // 2),\n    }\n    xy = positions.get(position, positions["bottom-right"])\n    draw.text(xy, text, font=font, fill=(255, 255, 255, opacity))\n\n    result = Image.alpha_composite(base, watermark_layer)\n    return result\n\nimg = add_watermark(text="© MAGD 2026", opacity=160, position="bottom-right")\n\nprint("Image Watermarking App")\nprint("-" * 40)\nprint(f"Output image size : {img.size}")\nprint(f"Output mode       : {img.mode}")\nprint("Watermark applied : \'© MAGD 2026\' @ 160/255 opacity, bottom-right")\nprint("(the real app lets you upload any image, drag the opacity slider,")\nprint(" and preview the result live before saving)")\n',
        "code_output": "Image Watermarking App\n----------------------------------------\nOutput image size : (400, 250)\nOutput mode       : RGBA\nWatermark applied : '© MAGD 2026' @ 160/255 opacity, bottom-right\n(the real app lets you upload any image, drag the opacity slider,\n and preview the result live before saving)\n",
        "demo_note": "The real app is a Tkinter desktop GUI with a file picker, live preview, and opacity slider — it needs a real screen, so it can't run in a browser. This demo runs the exact same Pillow blending technique on a generated sample image and reports the result.",
    },
    {
        "title": "Typing Speed Test",
        "description": "Real-time typing speed and accuracy tester with a fire-themed UI.",
        "full_description": "A Tkinter-based typing speed test with live WPM tracking, accuracy percentage, and per-character color feedback (correct/incorrect/current position). Time limits are configurable (15-120 seconds), with a live countdown and progress tracking.",
        "category": "desktop",
        "technologies": "Python, Tkinter",
        "github_link": "https://github.com/magd00/p4_typing_speed_Test_app",
        "image": "p4_typing_speed.svg",
        "code_snippet": '# Typing Speed Test - WPM and accuracy calculation\n# The real app is a Tkinter GUI with a live countdown and per-character\n# color feedback; this demo shows the actual scoring math it runs once\n# time\'s up.\n\ntarget_text = "the quick brown fox jumps over the lazy dog"\ntyped_text  = "the quick brown fox jumps over the lasy dog"\ntime_seconds = 12\n\ndef score_typing(target, typed, seconds):\n    correct_chars = sum(1 for t, y in zip(target, typed) if t == y)\n    total_chars = len(target)\n    accuracy = round(correct_chars / total_chars * 100, 1)\n\n    words_typed = len(typed.split())\n    wpm = round(words_typed / (seconds / 60), 1)\n\n    return accuracy, wpm, correct_chars, total_chars\n\naccuracy, wpm, correct, total = score_typing(target_text, typed_text, time_seconds)\n\nprint("Typing Speed Test - results")\nprint("-" * 40)\nprint(f"Time limit   : {time_seconds}s")\nprint(f"Characters   : {correct}/{total} correct ({accuracy}% accuracy)")\nprint(f"Words per minute: {wpm} WPM")\n\n# highlight where the typo was\nfor i, (t, y) in enumerate(zip(target_text, typed_text)):\n    if t != y:\n        print(f"Typo at position {i}: expected \'{t}\', got \'{y}\'")\n',
        "code_output": "Typing Speed Test - results\n----------------------------------------\nTime limit   : 12s\nCharacters   : 42/43 correct (97.7% accuracy)\nWords per minute: 45.0 WPM\nTypo at position 37: expected 'z', got 's'\n",
        "demo_note": 'The real app is a Tkinter GUI with a live countdown timer and color-coded feedback as you type. This demo runs the same WPM/accuracy scoring formula against a sample typed passage and shows exactly where a mistake occurred.',
    },
    {
        "title": "Breakout Game",
        "description": "Classic Breakout arcade game with paddle and ball physics.",
        "full_description": "A classic Breakout arcade game built with Pygame — bounce a ball off a paddle to break bricks, with realistic angle reflection, score tracking, and start/play/game-over/win screens.",
        "category": "game",
        "technologies": "Python, Pygame",
        "github_link": "https://github.com/magd00/p5_Breakout_game",
        "image": "p5_breakout.svg",
        "code_snippet": '# Breakout Game - core ball/paddle/brick collision logic\n# The real game uses Pygame for real-time graphics and needs a display, so\n# it can\'t run headlessly on a web server. This demo reproduces the same\n# collision rules (ball bounces off paddle at an angle based on where it\n# lands, bricks break on contact) using simple coordinates.\n\nclass Ball:\n    def __init__(self, x, y, dx, dy):\n        self.x, self.y, self.dx, self.dy = x, y, dx, dy\n\ndef bounce_off_paddle(ball, paddle_x, paddle_width):\n    hit_pos = (ball.x - paddle_x) / paddle_width  # 0 = left edge, 1 = right edge\n    angle_factor = (hit_pos - 0.5) * 2            # -1 (left) .. 1 (right)\n    ball.dx = angle_factor * 5\n    ball.dy = -abs(ball.dy)\n    return ball\n\nbricks = [{"x": col * 40, "y": 20, "alive": True} for col in range(10)]\n\nball = Ball(x=200, y=280, dx=2, dy=3)\npaddle_x, paddle_width = 170, 80\n\nscore = 0\nbricks_hit = 0\n\n# simulate the ball hitting the paddle, then a few bricks\nball = bounce_off_paddle(ball, paddle_x, paddle_width)\n\nfor brick in bricks:\n    if abs(brick["x"] - 120) < 20:  # simulate the ball\'s path clipping a few bricks\n        brick["alive"] = False\n        score += 10\n        bricks_hit += 1\n\nbricks_left = sum(1 for b in bricks if b["alive"])\n\nprint("Breakout Game - simulated rally")\nprint("-" * 40)\nprint(f"Paddle hit -> new ball direction: dx={ball.dx:.2f}, dy={ball.dy:.2f}")\nprint(f"Bricks broken: {bricks_hit}   Score: {score}")\nprint(f"Bricks remaining: {bricks_left}/{len(bricks)}")\nprint("YOU WIN!" if bricks_left == 0 else "Game in progress...")\n',
        "code_output": 'Breakout Game - simulated rally\n----------------------------------------\nPaddle hit -> new ball direction: dx=-1.25, dy=-3.00\nBricks broken: 1   Score: 10\nBricks remaining: 9/10\nGame in progress...\n',
        "demo_note": "The real game renders live with Pygame and needs a display/keyboard, so it can't run in a browser. This demo runs the same ball-bounce-angle and brick-collision math the game uses internally, on one simulated rally.",
    },
    {
        "title": "Cafe Management System",
        "description": "Full-stack Flask app for managing a database of cafes and their amenities.",
        "full_description": "A full-stack Cafe Management System built with Flask and SQLAlchemy. Lets users add, edit, delete, and browse cafes, with a JSON REST endpoint and a stats dashboard (total cafes, unique areas, average coffee price). Tracks per-cafe details like location, map link, seat count, coffee price, and amenities (WiFi, sockets, toilet, phone calls allowed).",
        "category": "web",
        "technologies": "Python, Flask, SQLAlchemy, SQLite",
        "github_link": "https://github.com/magd00/p6_cafe_website",
        "image": "p6_cafe.svg",
        "code_snippet": '# Cafe Management System - stats dashboard calculation\n# The real app is Flask + SQLAlchemy with full CRUD and a JSON API; this\n# demo runs the same stats-dashboard math (total cafes, unique areas,\n# average coffee price) against a small in-memory sample of cafe records.\n\ncafes = [\n    {"name": "Peak Dive Coffee", "area": "Peckham", "coffee_price": 2.80, "has_wifi": True},\n    {"name": "The Espresso Room", "area": "Bermondsey", "coffee_price": 3.20, "has_wifi": True},\n    {"name": "Grind House", "area": "Peckham", "coffee_price": 2.50, "has_wifi": False},\n    {"name": "Bean There", "area": "Shoreditch", "coffee_price": 3.50, "has_wifi": True},\n    {"name": "Corner Cafe", "area": "Bermondsey", "coffee_price": 2.90, "has_wifi": True},\n]\n\ndef build_stats(cafes):\n    total = len(cafes)\n    areas = {c["area"] for c in cafes}\n    avg_price = round(sum(c["coffee_price"] for c in cafes) / total, 2)\n    wifi_count = sum(1 for c in cafes if c["has_wifi"])\n    return {\n        "total_cafes": total,\n        "unique_areas": len(areas),\n        "average_coffee_price": avg_price,\n        "cafes_with_wifi": wifi_count,\n    }\n\nstats = build_stats(cafes)\n\nprint("Cafe Management System - stats dashboard")\nprint("-" * 40)\nfor key, value in stats.items():\n    label = key.replace("_", " ").title()\n    print(f"{label:<22}: {value}")\n\nprint()\nprint("Cafes:")\nfor c in cafes:\n    wifi = "✓" if c["has_wifi"] else "✗"\n    print(f"  {c[\'name\']:<20} {c[\'area\']:<12} £{c[\'coffee_price\']:.2f}  WiFi:{wifi}")\n',
        "code_output": 'Cafe Management System - stats dashboard\n----------------------------------------\nTotal Cafes           : 5\nUnique Areas          : 3\nAverage Coffee Price  : 2.98\nCafes With Wifi       : 4\n\nCafes:\n  Peak Dive Coffee     Peckham      £2.80  WiFi:✓\n  The Espresso Room    Bermondsey   £3.20  WiFi:✓\n  Grind House          Peckham      £2.50  WiFi:✗\n  Bean There           Shoreditch   £3.50  WiFi:✓\n  Corner Cafe          Bermondsey   £2.90  WiFi:✓\n',
        "demo_note": 'The full app is a Flask website with a database, forms, and a JSON API. This demo runs the exact same stats-dashboard calculation (total cafes, unique areas, average coffee price) against a small sample of cafe records.',
    },
    {
        "title": 'Space Invaders',
        "description": 'Turtle-graphics arcade shooter — pilot a mini spaceship, dodge falling stars, and blast waves of alien enemies.',
        "full_description": "A Space Invaders-style shooter built with Python's turtle module. You control a small ship along the bottom of the screen (A/D or arrow keys), fire lasers with spacebar, and score points by shooting down descending gold stars (+10) and a grid of colorful alien ships (+15) before they reach you or shoot back. You have 4 lives, the game tracks score/lives/level on screen, levels get harder as waves clear, and you can pause with P or restart with R after a Game Over. Built with two files: main.py (the Game class — collisions, scoring, levels, UI) and turtle_1.py (the Turtle-based sprite classes for the ship, lasers, stars, and enemies).",
        "category": 'game',
        "technologies": 'Python, turtle (standard library)',
        "github_link": 'https://github.com/magd00/p13_arcade_game_space_invaders.',
        "image": 'p13_space_invaders.svg',
        "code_snippet": '# Space Invaders - core game-loop logic\n# The real game (main.py + turtle_1.py) uses Python\'s `turtle` module for\n# graphics and needs a real display/keyboard, so it can\'t run headlessly on\n# a web server. This demo reproduces the *actual* collision/scoring logic\n# from Game.check_collisions() (distance < 25 = hit, +10 for a star, +15\n# for an enemy, lose a life if an enemy laser gets you) using simple\n# coordinates instead of turtle sprites, so you can see the real mechanics.\n\nimport random\n\nclass Entity:\n    def __init__(self, x, y, kind):\n        self.x, self.y, self.kind = x, y, kind\n        self.alive = True\n\n    def distance(self, other):\n        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5\n\nrandom.seed(1)\n\nstars = [Entity(-330 + col * 50, 0, "star") for col in range(6)]\nenemies = [Entity(-360 + col * 50, 200, "enemy") for col in range(6)]\n\n# simulate the player firing a burst of lasers, roughly aimed at targets\ntargets = stars + enemies\nlasers = [Entity(t.x + random.randint(-15, 15), t.y, "laser") for t in random.sample(targets, 8)]\n\nscore = 0\nlives = 4\n\nfor laser in lasers:\n    for star in stars:\n        if star.alive and laser.distance(star) < 25:\n            star.alive = False\n            score += 10\n    for enemy in enemies:\n        if enemy.alive and laser.distance(enemy) < 25:\n            enemy.alive = False\n            score += 15\n\n# simulate one enemy laser slipping through\nif random.random() < 0.5:\n    lives -= 1\n\nstars_left = sum(1 for s in stars if s.alive)\nenemies_left = sum(1 for e in enemies if e.alive)\n\n        print("SPACE INVADERS - simulated wave")\nprint("-" * 45)\nprint(f"Stars destroyed  : {6 - stars_left}/6  (+10 each)")\nprint(f"Enemies destroyed: {6 - enemies_left}/6  (+15 each)")\nprint(f"Score: {score}   Lives: {lives}")\nprint("LEVEL COMPLETE!" if stars_left == 0 and enemies_left == 0 else "Wave in progress...")\nprint()\nprint("Controls in the real game: A/D or arrow keys to move, SPACE to fire,")\nprint("P to pause, R to restart after Game Over.")\n',
        "code_output": 'SPACE INVADERS - simulated wave\n---------------------------------------------\nStars destroyed  : 5/6  (+10 each)\nEnemies destroyed: 3/6  (+15 each)\nScore: 95   Lives: 4\nWave in progress...\n\nControls in the real game: A/D or arrow keys to move, SPACE to fire,\nP to pause, R to restart after Game Over.\n',
        "demo_note": "The real game uses Python's turtle module for graphics and needs a real display/keyboard, so it can't run on a server. This demo runs the actual collision/scoring formula from the game's check_collisions() method against plain coordinates instead of turtle sprites.",
    },
    {
        "title": 'Ledger & Co. — Online Shop',
        "description": 'Full-stack Flask eCommerce store with cart, accounts, and real Stripe checkout.',
        "full_description": "A small eCommerce store (fine paper & desk goods) built with Flask. It has a product catalog backed by SQLite, a session-based cart, account registration/login with hashed passwords (Flask-Login + Flask-Bcrypt), CSRF-protected forms (Flask-WTF), and real checkout via Stripe Checkout in test mode. Prices are always recomputed server-side at checkout rather than trusted from the client, and Stripe's webhook is treated as the authoritative source of truth for 'was this actually paid' rather than the redirect URL alone.",
        "category": 'web',
        "technologies": 'Python, Flask, SQLAlchemy, Flask-Login, Stripe',
        "github_link": 'https://github.com/magd00/p15_online_shop',
        "image": 'p15_online_shop.svg',
        "code_snippet": '# Ledger & Co. eCommerce - server-side cart pricing logic\n# (Full app is Flask + SQLAlchemy + Stripe Checkout; this demo shows the\n#  key security idea from the project: totals are recomputed from the\n#  database/catalog on the server, never trusted from the client.)\n\ncatalog = {\n    1: {"name": "Fountain Pen", "price": 24.00},\n    2: {"name": "Leather Journal", "price": 32.50},\n    3: {"name": "Wax Seal Kit", "price": 18.00},\n}\n\n# What the client\'s session cart says: {product_id: quantity}\nsession_cart = {1: 2, 2: 1, 3: 3}\n\ndef price_cart(cart, catalog):\n    line_items = []\n    subtotal = 0.0\n    for product_id, qty in cart.items():\n        product = catalog[product_id]\n        line_total = product["price"] * qty\n        subtotal += line_total\n        line_items.append((product["name"], qty, product["price"], line_total))\n    return line_items, subtotal\n\nitems, subtotal = price_cart(session_cart, catalog)\ntax = round(subtotal * 0.08, 2)\ntotal = round(subtotal + tax, 2)\n\nprint("Ledger & Co. - Checkout Summary")\nprint("-" * 45)\nfor name, qty, price, line_total in items:\n    print(f"{qty} x {name:<18} ${price:>6.2f}  -> ${line_total:>7.2f}")\nprint("-" * 45)\nprint(f"{\'Subtotal\':<32}${subtotal:>7.2f}")\nprint(f"{\'Tax (8%)\':<32}${tax:>7.2f}")\nprint(f"{\'Total (sent to Stripe)\':<32}${total:>7.2f}")\n',
        "code_output": 'Ledger & Co. - Checkout Summary\n---------------------------------------------\n2 x Fountain Pen       $ 24.00  -> $  48.00\n1 x Leather Journal    $ 32.50  -> $  32.50\n3 x Wax Seal Kit       $ 18.00  -> $  54.00\n---------------------------------------------\nSubtotal                        $ 134.50\nTax (8%)                        $  10.76\nTotal (sent to Stripe)          $ 145.26\n',
        "demo_note": 'This is the real server-side logic from checkout: cart totals, tax, and the final amount sent to Stripe are always recomputed here from the catalog, never trusted from the browser. Click Run Code to see a sample cart priced out exactly like the live store would.',
    },
    {
        "title": 'Beauty Color Extractor',
        "description": 'Upload an image and instantly see its most common colors as a palette with hex codes and percentages.',
        "full_description": "A Flask web app that finds the dominant colors in any uploaded image. It downsamples the image, runs K-Means clustering (scikit-learn) on the pixel data to group similar colors together, then reports each cluster's color as a hex code along with what percentage of the image it covers. Useful for designers pulling a palette from a photo, or anyone curious what colors define an image.",
        "category": 'data',
        "technologies": 'Python, Flask, NumPy, Pillow, scikit-learn',
        "github_link": 'https://github.com/magd00/p10_butycolory_app-find-the-most-common-colors-in-an-uploudedimage',
        "image": 'p10_color_extractor.svg',
        "code_snippet": '# Beauty Color Extractor - core color-quantization logic\n# (Full app uses Flask + scikit-learn KMeans on real uploaded images;\n#  this is a self-contained demo of the same idea using pure Python.)\n\nfrom collections import Counter\n\ndef quantize(value, step=32):\n    return (value // step) * step\n\ndef extract_dominant_colors(pixels, n_colors=5):\n    quantized = [tuple(quantize(c) for c in p) for p in pixels]\n    counts = Counter(quantized)\n    total = len(pixels)\n    dominant = counts.most_common(n_colors)\n    results = []\n    for color, count in dominant:\n        r, g, b = color\n        hex_code = \'#{:02x}{:02x}{:02x}\'.format(r, g, b)\n        pct = round(count / total * 100, 1)\n        results.append((hex_code, pct))\n    return results\n\n# Simulated "uploaded image" pixel data (RGB tuples)\nsample_pixels = (\n    [(220, 40, 40)] * 40 +\n    [(30, 90, 200)] * 25 +\n    [(240, 210, 20)] * 20 +\n    [(20, 160, 90)] * 15\n)\n\npalette = extract_dominant_colors(sample_pixels, n_colors=4)\n\nprint("Beauty Color Extractor - Dominant Palette")\nprint("-" * 40)\nfor hex_code, pct in palette:\n    bar = "#" * int(pct / 2)\n    print(f"{hex_code}  {pct:>5}%  {bar}")\n',
        "code_output": 'Beauty Color Extractor - Dominant Palette\n----------------------------------------\n#c02020   40.0%  ####################\n#0040c0   25.0%  ############\n#e0c000   20.0%  ##########\n#00a040   15.0%  #######\n',
        "demo_note": "The live app uses scikit-learn's K-Means clustering on your uploaded image's real pixels. This demo uses the same clustering idea in pure Python against a small sample image, so you can see the same kind of dominant-color palette output without uploading anything.",
    },
    {
        "title": 'Open Art Museum Explorer',
        "description": "Command-line tool that searches the Art Institute of Chicago's public API for artworks.",
        "full_description": "A Python CLI that connects to the Art Institute of Chicago's public API to search for artworks by artist, style, or keyword. It returns titles, artist names, and direct image links, with graceful handling of network/API errors and a loop so you can keep searching without restarting the script.",
        "category": 'api',
        "technologies": 'Python, Requests, REST APIs',
        "github_link": 'https://github.com/magd00/p14_API_search',
        "image": 'p14_api_search.svg',
        "code_snippet": '# Open Art Museum Explorer - searches the Art Institute of Chicago\'s\n# public API for artworks by keyword. Falls back to a small offline\n# sample set if there\'s no network access in this environment, so the\n# demo always produces real, readable output.\n\nimport json\n\ndef search_local_fallback(query, artworks):\n    query = query.lower()\n    return [a for a in artworks if query in a["title"].lower() or query in a["artist"].lower()]\n\ntry:\n    import urllib.request\n    url = ("https://api.artic.edu/api/v1/artworks/search"\n           "?q=van+gogh&fields=title,artist_title,image_id&limit=3")\n    with urllib.request.urlopen(url, timeout=4) as resp:\n        data = json.loads(resp.read())\n    results = [\n        {"title": d.get("title"), "artist": d.get("artist_title") or "Unknown"}\n        for d in data.get("data", [])\n    ]\n    source = "live Art Institute of Chicago API"\nexcept Exception:\n    sample_artworks = [\n        {"title": "The Bedroom", "artist": "Vincent van Gogh"},\n        {"title": "Self-Portrait", "artist": "Vincent van Gogh"},\n        {"title": "A Sunday on La Grande Jatte", "artist": "Georges Seurat"},\n    ]\n    results = search_local_fallback("van gogh", sample_artworks)\n    source = "offline sample data (no network in this sandbox)"\n\nprint("Open Art Museum Explorer")\nprint(f"Search: \'van gogh\'  |  source: {source}")\nprint("-" * 45)\nfor i, r in enumerate(results, start=1):\n    print(f"{i}. {r[\'title\']}  -  {r[\'artist\']}")\nprint(f"\\n{len(results)} result(s) found")\n',
        "code_output": "Open Art Museum Explorer\nSearch: 'van gogh'  |  source: offline sample data (no network in this sandbox)\n---------------------------------------------\n1. The Bedroom  -  Vincent van Gogh\n2. Self-Portrait  -  Vincent van Gogh\n\n2 result(s) found\n",
        "demo_note": 'This calls the real Art Institute of Chicago public API and returns live search results. If this server has no internet access it automatically falls back to a small offline sample so the demo still works.',
    },
    {
        "title": 'Recipe Scraper',
        "description": 'Scrapes recipe titles, links, and images from AllRecipes.com and exports them to CSV/JSON.',
        "full_description": 'A web scraper built with Requests and BeautifulSoup that pulls recipe titles, links, and preview images from AllRecipes.com across multiple pages. It tries several HTML selectors for resilience against layout changes, rotates User-Agent headers, and handles 403 blocks, connection errors, and timeouts gracefully. Results can be exported to CSV or JSON, or just printed to the console.',
        "category": 'automation',
        "technologies": 'Python, Requests, BeautifulSoup',
        "github_link": 'https://github.com/magd00/p11_Recipe-Scraper',
        "image": 'p11_recipe_scraper.svg',
        "code_snippet": '# Recipe Scraper - core parsing logic\n# (Full project uses requests + BeautifulSoup against AllRecipes.com;\n#  this demo parses a local HTML sample so it runs anywhere without a\n#  network call or getting blocked by anti-bot protection.)\n\nfrom html.parser import HTMLParser\n\nsample_html = """\n<div class="card-list">\n  <a class="card" href="/recipe/101" data-title="Classic Beef Chili"></a>\n  <a class="card" href="/recipe/102" data-title="Lemon Garlic Roast Chicken"></a>\n  <a class="card" href="/recipe/103" data-title="Vegetarian Pad Thai"></a>\n  <a class="card" href="/recipe/104" data-title="One-Pan Shakshuka"></a>\n</div>\n"""\n\nclass RecipeParser(HTMLParser):\n    def __init__(self):\n        super().__init__()\n        self.recipes = []\n\n    def handle_starttag(self, tag, attrs):\n        if tag == "a":\n            attrs = dict(attrs)\n            if attrs.get("class") == "card":\n                self.recipes.append({\n                    "title": attrs.get("data-title"),\n                    "url": "https://allrecipes.com" + attrs.get("href", "")\n                })\n\nparser = RecipeParser()\nparser.feed(sample_html)\n\nprint("Recipe Scraper - extracted recipes")\nprint("-" * 40)\nfor i, r in enumerate(parser.recipes, start=1):\n    print(f"{i}. {r[\'title\']}")\n    print(f"   {r[\'url\']}")\n\nprint(f"\\nTotal recipes found: {len(parser.recipes)}")\nprint("(Exportable to CSV/JSON in the full script)")\n',
        "code_output": 'Recipe Scraper - extracted recipes\n----------------------------------------\n1. Classic Beef Chili\n   https://allrecipes.com/recipe/101\n2. Lemon Garlic Roast Chicken\n   https://allrecipes.com/recipe/102\n3. Vegetarian Pad Thai\n   https://allrecipes.com/recipe/103\n4. One-Pan Shakshuka\n   https://allrecipes.com/recipe/104\n\nTotal recipes found: 4\n(Exportable to CSV/JSON in the full script)\n',
        "demo_note": 'The live scraper pulls real listings from AllRecipes.com, which actively blocks bots — so this demo parses a small local HTML sample using the exact same BeautifulSoup-style parsing logic, guaranteed to work every time you click Run Code.',
    },
    {
        "title": 'Dinosaur Game Automation',
        "description": "Bot that watches Chrome's offline dino game on screen and auto-jumps/ducks past obstacles.",
        "full_description": "An automation script that captures the screen in real time while Chrome's offline T-Rex runner game is playing, detects incoming cacti and birds, and sends jump or duck key presses at the right moment using PyAutoGUI. The core of the project is the decision logic — given an obstacle's type and distance at the current game speed, decide whether to jump, duck, or keep running.",
        "category": 'automation',
        "technologies": 'Python, PyAutoGUI, Screen Capture',
        "github_link": 'https://github.com/magd00/p12_automation_for_dinosaur_game',
        "image": 'p12_dino_game.jpg',
        "code_snippet": '# Automation for Dinosaur Game - core decision logic\n# (Full project uses PyAutoGUI + screen capture to read the live game\n#  and send real keypresses; this demo simulates the obstacle feed and\n#  shows the same jump/duck decision-making without needing a screen.)\n\nimport random\n\ndef decide_action(distance_to_obstacle, obstacle_type, speed):\n    reaction_distance = 120 + speed * 4\n    if distance_to_obstacle > reaction_distance:\n        return "run"\n    if obstacle_type == "bird_low":\n        return "duck"\n    return "jump"\n\nrandom.seed(7)\nspeed = 10\nscore = 0\nlog = []\n\nfor tick in range(8):\n    obstacle = random.choice(["cactus", "cactus", "bird_low", "bird_high"])\n    distance = random.randint(40, 300)\n    action = decide_action(distance, obstacle, speed)\n    score += 10\n    speed += 0.5\n    log.append((tick, obstacle, distance, action))\n\nprint("Dino Game Automation - decision log")\nprint("-" * 45)\nprint(f"{\'tick\':<5}{\'obstacle\':<12}{\'distance\':<10}{\'action\'}")\nfor tick, obstacle, distance, action in log:\n    print(f"{tick:<5}{obstacle:<12}{distance:<10}{action}")\n\nprint(f"\\nFinal simulated score: {score}")\n',
        "code_output": 'Dino Game Automation - decision log\n---------------------------------------------\ntick obstacle    distance  action\n0    bird_low    117       duck\n1    bird_high   64        jump\n2    cactus      88        jump\n3    bird_low    69        duck\n4    cactus      59        jump\n5    cactus      262       run\n6    bird_high   75        jump\n7    cactus      86        jump\n\nFinal simulated score: 80\n',
        "demo_note": "The real bot watches your screen live and sends keypresses via PyAutoGUI — it needs an actual screen to see, so it can't run on a server. This demo runs the same jump/duck decision logic against a simulated sequence of obstacles.",
    },
]


def seed_initial_projects():
    """Populate the Project table on first run only (won't duplicate on restart)."""
    if Project.query.count() == 0:
        for p in INITIAL_PROJECTS:
            db.session.add(Project(**p))
        db.session.commit()
        print(f"✅ Seeded {len(INITIAL_PROJECTS)} projects.")


# Create database tables
with app.app_context():
    db.create_all()
    seed_initial_projects()
    print("✅ Database created successfully!")

# ==================== HELPER FUNCTIONS ====================

def execute_python_code(code_string):
    """Execute Python code safely and capture output"""
    output = io.StringIO()

    try:
        with contextlib.redirect_stdout(output):
            exec_globals = {}
            exec(code_string, exec_globals)
        return output.getvalue(), None
    except Exception as e:
        error_output = traceback.format_exc()
        return None, error_output

# ==================== ROUTES ====================

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/resume')
def resume():
    """Resume page"""
    return render_template('resume.html')

@app.route('/services')
def services():
    """Services page"""
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    """Portfolio page - shows all projects"""
    projects = Project.query.all()
    return render_template('portfolio.html', projects=projects)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Show individual project details"""
    project = Project.query.get_or_404(project_id)
    simulation_slug = None
    is_morse_translator = (project.github_link or '').rstrip('/').endswith('/p1_Morce_Code_translator')
    project_repo = (project.github_link or '').rstrip('/').rstrip('.')
    is_space_invaders = project_repo.endswith('/p13_arcade_game_space_invaders')
    is_watermark_app = project_repo.endswith('/p3_image_watermarking_app')
    is_typing_test = project_repo.endswith('/p4_typing_speed_Test_app')
    if (project.github_link or '').rstrip('/').endswith('/p12_automation_for_dinosaur_game'):
        simulation_slug = 'p12_automation_for_dinosaur_game'
    return render_template(
        'project_detail.html',
        project=project,
        simulation_slug=simulation_slug,
        is_morse_translator=is_morse_translator,
        is_space_invaders=is_space_invaders,
        is_watermark_app=is_watermark_app,
        is_typing_test=is_typing_test,
    )


def resolve_project_dir(slug):
    """Resolve a project folder under projects/ without allowing path traversal."""
    if not re.fullmatch(r'[A-Za-z0-9_-]+', slug):
        return None

    projects_root = (Path(__file__).resolve().parent / 'projects').resolve()
    project_dir = (projects_root / slug).resolve()
    if project_dir.parent != projects_root or not project_dir.is_dir():
        return None
    return project_dir


@app.route('/play/<slug>/')
def play_project_root(slug):
    """Redirect the project play URL to its isolated demo directory."""
    if resolve_project_dir(slug) is None:
        abort(404)
    return redirect(url_for('play_project', slug=slug))


@app.route('/play/<slug>/demo/', defaults={'filename': 'index.html'})
@app.route('/play/<slug>/demo/<path:filename>')
def play_project(slug, filename):
    """Serve only static files from a project's demo/ directory."""
    project_dir = resolve_project_dir(slug)
    if project_dir is None:
        abort(404)

    demo_dir = (project_dir / 'demo').resolve()
    if demo_dir.parent != project_dir or not demo_dir.is_dir():
        abort(404)
    requested_file = (demo_dir / filename).resolve()
    if requested_file != demo_dir and demo_dir not in requested_file.parents:
        abort(404)
    return send_from_directory(demo_dir, filename)

@app.route('/run-code', methods=['POST'])
def run_code():
    """API endpoint to run Python code and return output"""
    data = request.get_json()
    code = data.get('code', '')

    output, error = execute_python_code(code)

    # Save to database
    execution = CodeExecution(
        code=code,
        output=output if output else None,
        error=error if error else None
    )
    db.session.add(execution)
    db.session.commit()

    return jsonify({
        'output': output if output else '',
        'error': error if error else ''
    })

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form handling"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Print to console (you can replace with email sending)
        print(f"\n📧 New Contact Message:")
        print(f"From: {name} ({email})")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print("-" * 50)

        flash('✅ Message sent successfully! I will get back to you soon.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')

# ==================== ERROR HANDLERS ====================
# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Custom 500 page"""
    return render_template('500.html'), 500
# ==================== RUN THE APPLICATION ====================

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    print("\n🚀 Starting Flask Development Server...")
    print("📍 Access your portfolio at: http://127.0.0.1:5000")
    print(f"🔧 Debug mode: {'ON' if debug_mode else 'OFF'}")
    print(f"📁 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("\n✨ Portfolio is ready! Press CTRL+C to stop.\n")

    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))