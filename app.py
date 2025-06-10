from flask import Flask, redirect, url_for, render_template, request, session
from flask_dance.contrib.google import make_google_blueprint, google
from werkzeug.utils import secure_filename
import os
import torch
from torchvision import models, transforms
from PIL import Image

# OAuth-Konfiguration (lokal, ohne HTTPS)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Google OAuth Blueprint
google_bp = make_google_blueprint(
    client_id = os.getenv("519412196727-442r2nmsiv6juv697hs6mk1ni448cgmm.apps.googleusercontent.com"),
    
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")

# Bildklassifikation vorbereiten
with open("imagenet_classes.txt") as f:
    klasse_namen = [line.strip() for line in f.readlines()]

modell = models.mobilenet_v2(pretrained=True)
modell.eval()

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def klassifiziere_bild(pfad):
    bild = Image.open(pfad).convert('RGB')
    bild = transform(bild).unsqueeze(0)
    with torch.no_grad():
        ausgabe = modell(bild)
    wahrsch = torch.nn.functional.softmax(ausgabe[0], dim=0)
    top5 = torch.topk(wahrsch, 5)
    erklaerung = [
        f"{klasse_namen[idx]} ({wert.item()*100:.2f}%)"
        for idx, wert in zip(top5.indices, top5.values)
    ]
    return klasse_namen[top5.indices[0]], erklaerung

# Temporäre Bilddatenbank
bild_datenbank = []

@app.route("/google-login")
def google_login():
    try:
        if not google.authorized:
            return redirect(url_for("google.login"))
        resp = google.get("/oauth2/v2/userinfo")
        assert resp.ok, resp.text
        email = resp.json()["email"]
        return f"✅ Eingeloggt als: {email} <br><a href='/'>Zur App</a>"
    except Exception as e:
        return f"⚠️ Fehler beim Login: {str(e)}"

@app.route("/logout")
def logout():
    if "google_oauth_token" in session:
        del session["google_oauth_token"]
    return redirect(url_for("google_login"))

@app.route('/')
def home():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template("upload.html")

@app.route('/upload', methods=['POST'])
def upload():
    if not google.authorized:
        return redirect(url_for("google.login"))
    bild = request.files['bild']
    beschreibung = request.form.get('beschreibung', '')
    if bild:
        dateiname = secure_filename(bild.filename)
        pfad = os.path.join(app.config['UPLOAD_FOLDER'], dateiname)
        bild.save(pfad)
        klasse, erklaerung = klassifiziere_bild(pfad)
        bild_datenbank.append({
            "dateiname": dateiname,
            "beschreibung": beschreibung,
            "klasse": klasse,
            "erklaerung": erklaerung,
            "kommentare": []
        })
        return redirect(url_for('bilder'))
    return "Fehler beim Upload"

@app.route('/bilder')
def bilder():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template("bilder.html", bilder=bild_datenbank)

@app.route('/kommentar/<dateiname>', methods=['POST'])
def kommentar(dateiname):
    if not google.authorized:
        return redirect(url_for("google.login"))
    kommentar_text = request.form.get('kommentar', '')
    for eintrag in bild_datenbank:
        if eintrag["dateiname"] == dateiname:
            eintrag["kommentare"].append(kommentar_text)
            break
    return redirect(url_for('bilder'))

@app.route('/loeschen/<dateiname>')
def loeschen(dateiname):
    if not google.authorized:
        return redirect(url_for("google.login"))
    pfad = os.path.join(app.config['UPLOAD_FOLDER'], dateiname)
    if os.path.exists(pfad):
        os.remove(pfad)
    global bild_datenbank
    bild_datenbank = [b for b in bild_datenbank if b["dateiname"] != dateiname]
    return redirect(url_for('bilder'))

if __name__ == '__main__':
    app.run(debug=True)