# 🎨 Virtual Hand-Drawing & Gesture UI Designer

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange.svg)

**Draw in mid-air using hand gestures! Control your canvas with intuitive hand movements tracked through your webcam.**

</div>

---

## ✨ Features

### 🖐️ Gesture Controls

| Gesture | Visual | Function |
|---------|--------|----------|
| Index Finger | ☝️ | Drawing mode |
| Closed Fist | ✊ | Eraser mode |
| Open Palm | 🤚 | Clear canvas |
| Two Fingers | ✌️ | Undo action |

### 🎨 Additional Features
- **Color Palette**: Quick color switching with G/B/R/Y/W/P keys
- **Smoothing**: Jitter-free drawing with 5-frame averaging
- **Export**: Save your masterpiece as PNG

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/palakchandak8/virtual-hand-drawing.git
cd virtual-hand-drawing

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python src/main.py
```

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| Q | Quit |
| S | Save drawing |
| H | Toggle help |
| G/B/R/Y/W/P | Change color |

---

## 📋 Requirements

- Python 3.8+
- Webcam
- See `requirements.txt` for packages

---

## 🏗️ Architecture

```
┌─────────────┐
│   Camera    │
│   Input     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MediaPipe  │
│ Hand Tracking│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Gesture    │
│  Detection  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Drawing    │
│   Layer     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Display   │
│   Output    │
└─────────────┘
```

### Core Components
- **Capture Module**: Handles webcam input and frame processing
- **Hand Detector**: MediaPipe-based landmark detection (21 points per hand)
- **Gesture Recognizer**: Classifies hand poses into drawing commands
- **Canvas Manager**: Maintains drawing state and rendering pipeline
- **UI Controller**: Processes keyboard input and display updates

---

## 📁 Project Structure

```
virtual-hand-drawing/
├── src/
│   ├── main.py              # Application entry point
│   ├── hand_detector.py     # Hand tracking logic
│   ├── gesture_recognizer.py# Gesture classification
│   └── canvas.py            # Drawing canvas manager
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── LICENSE                 # MIT License
└── examples/               # Sample drawings
```

---

## 🎯 Usage Tips

1. **Optimal Lighting**: Use well-lit environments for better hand detection
2. **Hand Position**: Keep hand 1-2 feet from camera for best tracking
3. **Steady Movements**: Draw slowly for smoother lines
4. **Calibration**: Allow 2-3 seconds for initial hand detection
5. **Background**: Plain backgrounds improve tracking accuracy

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking technology
- [OpenCV](https://opencv.org/) for computer vision tools
- Inspired by air canvas and gesture-based UI projects

---

<div align="center">

**Made with ❤️ by [Palak Chandak](https://github.com/palakchandak8)**

[![GitHub](https://img.shields.io/badge/GitHub-palakchandak8-181717?style=flat-square&logo=github)](https://github.com/palakchandak8)

⭐ **Star this repo if you found it useful!**

</div>