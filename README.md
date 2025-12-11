# 🎨 Virtual Hand-Drawing & Gesture UI Designer

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange.svg)

*Draw in mid-air using hand gestures! Control your canvas with intuitive hand movements tracked through your webcam.*


Pen/Pencil Mode • Virtual Keyboard • Multiple Brush Shapes • Smart Notifications • Enhanced UI Ribbon • Pinch Thickness Control • Pause Mode • Improved Smoothing • 8-Color Palette • Better Undo System

</div>


---
## ✨ Features

### 🖐 Gesture Controls

| Gesture | Visual | Function |
|---------|--------|----------|
| Index Finger | ☝ | Drawing mode |
| Closed Fist | ✊ | Erase entire canvas |
| Open Palm | 🤚 | Pause/Resume |
| Two Fingers | ✌ | Undo action |
| Three Fingers | 🤟 | Change brush shape |
| Pinch | 🤏 | Adjust brush thickness |

### 🎨 Additional Features
- *4 Brush Shapes*: Normal, Circle, Square, Spray paint
- *8 Color Palette*: G/B/R/Y/W/P/O/C keys
- *Thickness Control*: UP/DOWN arrows or pinch gesture (1-50px)
- *Smoothing*: 10-frame motion averaging
- *Pen/Pencil Mode*: Draw with physical colored pens (Red/Blue/Green)
- *Virtual Keyboard*: QWERTY keyboard for text annotations
- *Smart Notifications*: Real-time feedback system
- *Interactive UI*: Ribbon panel and side instructions (toggle with H/T keys)
- *Export*: Save as PNG with timestamp
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

### ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Q** | Quit |
| **S** | Save PNG |
| **H** | Toggle Help |
| **T** | Toggle Ribbon |
| **K** | Virtual Keyboard |
| **P** | Pen / Hand Mode |
| **↑ / ↓** | Brush Size + / - |
| **G B R Y W P O C** | Color Select |
| **1 2 3** | Track Red / Blue / Green Pen |


---

## 📋 Requirements

- Python 3.8+
- Working webcam (built-in or USB)
- See requirements.txt for packages
- 4GB RAM minimum

### Python Dependencies
```
opencv-python==4.8.1.78
mediapipe==0.10.8
numpy==1.24.3
```

## 🏗 Architecture
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
- *Capture Module*: Handles webcam input and frame processing
- *Hand Detector* (gesture_detector.py): MediaPipe-based landmark detection (21 points per hand)
- *Gesture Recognizer*: Classifies hand poses into drawing commands (6 unique gestures)
- *Canvas Manager* (drawing_canvas.py): Maintains drawing state, brush shapes, and rendering pipeline
- *Virtual Keyboard* (virtual_keyboard.py): QWERTY keyboard interface for text input
- *Notification System* (notification_system.py): Real-time feedback and status messages
- *Pen Tracking*: HSV color-based detection for physical pen/pencil drawing
- *UI Controller*: Processes keyboard input and display updates
---

## 📁 Project Structure
```

virtual-hand-drawing/
├── src/
│   ├── main.py                # Application entry point
│   ├── gesture_detector.py    # Hand tracking & pen detection logic
│   ├── drawing_canvas.py      # Drawing canvas manager with brush shapes
│   ├── virtual_keyboard.py    # QWERTY keyboard interface
│   └── notification_system.py # Notification display system
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE                    # MIT License
└── output/                    # Saved drawings folder (auto-created)

```
---

## 🎯 Usage Tips
```
### Hand Mode
- Good lighting • 1–2 ft distance • Slow movements • 2–3 sec detect • Plain background

### Pen Mode
- Red/Blue/Green tip • P to toggle • Point to draw • 1/2/3 to switch color

### Virtual Keyboard
- K to open • Point to type • SPACE / DEL / CLEAR / SAVE / HIDE • After SAVE: point to place text

### Brush Controls
- Shapes: Normal / Circle / Square / Spray
- Thickness: Pinch or UP/DOWN
- Colors: G B R Y W P O C
- Ribbon shows preview

## 🎨 Brush Shapes
Normal • Circle • Square • Spray

## 💡 Pro Tips
Pause (open palm) • Multiple undo (two-finger) • Save (S) • Toggle UI: T (ribbon), H (help)
```
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

Made with ❤ by   [![GitHub](https://img.shields.io/badge/GitHub-palakchandak8-181717?style=flat-square&logo=github)](https://github.com/palakchandak8) 

⭐ *Star this repo if you found it useful!*

</div>
