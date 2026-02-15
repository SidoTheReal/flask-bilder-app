# Flask Bilder App

A Flask-based web application that allows users to upload images, classify them using a pre-trained MobileNetV2 model, and manage images with Google OAuth authentication.

---

## 🚀 Features

- Google OAuth Login (Flask-Dance)
- Image upload functionality
- Image classification using MobileNetV2 (ImageNet)
- Top-1 and Top-5 prediction display
- Image gallery view
- Comment system per image
- Image deletion
- Basic file upload validation

---

## 🛠 Tech Stack

- Python 3
- Flask
- Flask-Dance (Google OAuth)
- PyTorch & Torchvision
- Pillow (PIL)
- HTML (Jinja Templates)

---

## 📂 Project Structure

```text
flask-bilder-app/
├── app.py
├── imagenet_classes.txt
├── templates/
├── static/
│   └── uploads/
├── screenshots/
└── README.md
```
---

## 🔐 Environment Variables

Before running the app, set the following environment variables:

```bash
export GOOGLE_OAUTH_CLIENT_ID="your_client_id"
export GOOGLE_OAUTH_CLIENT_SECRET="your_client_secret"
export FLASK_SECRET_KEY="your_secret_key"

