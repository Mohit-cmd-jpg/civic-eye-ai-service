# 👁️ Civic-Eye AI Service

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-5C3EE8?style=flat&logo=opencv&logoColor=white)](https://opencv.org/)

An AI-powered service for image authenticity verification and severity analysis, used by the Civic-Eye platform to validate citizen reports.

## ✨ Features

- **🔍 Image Authenticity (ELA):** Detects digital manipulations using Error Level Analysis.
- **📄 Metadata Analysis:** Inspects EXIF data for editing software signatures.
- **🌓 Shadow Consistency:** Analyzes lighting and shadow patterns for anomalies.
- **📈 Trust Score:** Calculates a unified trust percentage (0-100%) for every report.
- **🚨 Severity Analysis:** Automatically determines report priority based on issue type and AI trust score.

## 🛠️ Tech Stack

- **Framework:** Flask (Python)
- **Image Processing:** OpenCV, Pillow (PIL)
- **Deployment:** Cloud-ready with `opencv-python-headless`

## 📦 Project Structure

```text
ai-service/
├── app.py              # Main Flask application & AI logic
├── requirements.txt    # Project dependencies
└── .gitignore          # Git ignore rules
```

## 🚀 Running Locally

1. **Clone & Navigate:**
   ```bash
   git clone https://github.com/Mohit-cmd-jpg/civic-eye-ai-service.git
   cd civic-eye-ai-service
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Service:**
   ```bash
   python app.py
   ```
   Server runs at `http://localhost:5000`

## 📄 License
This project is open-source under the MIT License.

Made with ❤️ by Mohit Bindal
