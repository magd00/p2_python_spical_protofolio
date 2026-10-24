# 🦕 Dinosaur Game Auto Bot

An automated bot that plays the Chrome Dinosaur Game using computer vision and automation techniques.

## 📋 Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Controls](#controls)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Automatic Dinosaur Detection**: Finds the dinosaur position automatically on screen
- **Obstacle Detection**: Detects cacti and pterodactyls using computer vision
- **Smart Actions**: 
  - Jumps over cacti
  - Ducks under pterodactyls
- **Game Over Detection**: Automatically detects when the game ends
- **Auto-Restart**: Restarts the game automatically when you lose
- **Adaptive Thresholding**: Works in both day and night modes
- **Real-time Feedback**: Shows jump count, duck count, and restart count
- **Performance Optimized**: Fast detection with minimal delay

## 📦 Requirements

### Hardware
- Computer with web browser support
- Screen resolution: Any (auto-calibrates)

### Software
- Python 3.7 or higher
- Chrome Browser
- ChromeDriver

### Python Packages

1. Captures screen region in front of dinosaur
2. Converts to grayscale
3. Applies threshold to isolate dark objects
4. Uses contour detection to find obstacles
5. Analyzes object dimensions to determine action