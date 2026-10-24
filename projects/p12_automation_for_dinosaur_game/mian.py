from selenium import webdriver
import time
import pyautogui
import numpy as np
from PIL import ImageGrab
import cv2
import msvcrt

pyautogui.PAUSE = 0.005

def find_dino_automatically():
    time.sleep(1)

    screen = ImageGrab.grab()
    img = np.array(screen.convert('L'))

    _, thresh = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if 35 < w < 60 and 40 < h < 60:
            detection_box = (x + w + 15, y + 30, 140, 75)
            game_over_box = (x - 50, y - 120, 300, 80)
            return detection_box, game_over_box

    return None, None

def restart_game():
    pyautogui.press("space")
    time.sleep(0.3)
    pyautogui.press("space")

def check_game_over(go_box):
    try:
        screenshot = ImageGrab.grab(bbox=(go_box[0], go_box[1], go_box[0] + go_box[2], go_box[1] + go_box[3]))
        img = np.array(screenshot.convert('L'))
        dark_pixels = np.sum(img < 100)
        if 500 < dark_pixels < 3000:
            return True
        return False
    except:
        return False

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://elgoog.im/dinosaur-game/")

time.sleep(3)
driver.maximize_window()
time.sleep(1)

pyautogui.click(300, 300)
time.sleep(0.5)
pyautogui.press("space")
time.sleep(0.5)

DETECTION_BOX, GAME_OVER_BOX = find_dino_automatically()

if not DETECTION_BOX:
    DETECTION_BOX = (320, 580, 150, 80)
    GAME_OVER_BOX = (400, 450, 300, 100)

print(f"Detection Box: {DETECTION_BOX}")
print(f"Game Over Box: {GAME_OVER_BOX}")

def jump():
    pyautogui.press("space")

def duck():
    pyautogui.keyDown("down")
    time.sleep(0.08)
    pyautogui.keyUp("down")

def detect_obstacle():
    try:
        screenshot = ImageGrab.grab(bbox=(
            DETECTION_BOX[0],
            DETECTION_BOX[1],
            DETECTION_BOX[0] + DETECTION_BOX[2],
            DETECTION_BOX[1] + DETECTION_BOX[3]
        ))

        img = np.array(screenshot.convert('L'))

        blurred = cv2.GaussianBlur(img, (3, 3), 0)

        _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY_INV)

        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=1)

        dark_pixels = np.sum(thresh > 0)

        if dark_pixels < 50:
            return None

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 40:
                x, y, w, h = cv2.boundingRect(contour)

                if w > 80 and h < 25:
                    return "duck"
                elif h > 25 and area > 60:
                    return "jump"

        return None
    except Exception as e:
        return None

def start_bot():
    print("\n" + "="*50)
    print("DINOSAUR GAME BOT RUNNING")
    print("="*50)
    print("Press Ctrl+C or hold the 's' key for 1 second to stop")
    print("Close the browser to stop the bot automatically")
    print("="*50)

    jump_count = 0
    duck_count = 0
    restart_count = 0
    last_action = 0
    frame_count = 0
    stop_requested = False

    def should_stop():
        global driver
        try:
            driver.title
        except Exception:
            print("\nBrowser closed. Stopping bot.")
            return True

        try:
            if msvcrt.kbhit():
                key = msvcrt.getwch()
                if key.lower() == 's':
                    start = time.time()
                    while time.time() - start < 1.0:
                        if msvcrt.kbhit():
                            next_key = msvcrt.getwch()
                            if next_key.lower() == 's':
                                print("\nSTOP signal received via 's' key")
                                return True
                        time.sleep(0.02)
        except Exception:
            pass
        return False

    try:
        while not stop_requested:
            frame_count += 1

            if should_stop():
                stop_requested = True
                break

            if check_game_over(GAME_OVER_BOX):
                print(f"\nGame Over! Restart #{restart_count + 1}")
                restart_count += 1
                restart_game()
                time.sleep(0.8)
                pyautogui.press("space")
                time.sleep(0.5)
                jump_count = 0
                duck_count = 0
                continue

            if time.time() - last_action < 0.07:
                time.sleep(0.001)
                continue

            action = detect_obstacle()

            if action == "jump":
                jump()
                jump_count += 1
                last_action = time.time()
                print(f"Jumps: {jump_count} | Ducks: {duck_count} | Restarts: {restart_count}")

            elif action == "duck":
                duck()
                duck_count += 1
                last_action = time.time()
                print(f"Jumps: {jump_count} | Ducks: {duck_count} | Restarts: {restart_count}")

            time.sleep(0.002)

    except KeyboardInterrupt:
        print("\n" + "="*50)
        print("BOT STOPPED BY USER")
        print("="*50)
        print(f"Total Jumps: {jump_count}")
        print(f"Total Ducks: {duck_count}")
        print(f"Total Restarts: {restart_count}")
        print("="*50)
        return

    print("\n" + "="*50)
    print("BOT STOPPED BY USER")
    print("="*50)
    print(f"Total Jumps: {jump_count}")
    print(f"Total Ducks: {duck_count}")
    print(f"Total Restarts: {restart_count}")
    print("="*50)
    driver.quit()

if __name__ == "__main__":
    try:
        start_bot()
    except Exception as e:
        print(f"Error: {e}")
        try: driver.quit()
        except: pass