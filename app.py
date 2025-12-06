# TAPI MERAH # app.py
from flask import Flask, request, render_template, redirect, url_for, session, flash
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import pandas as pd
import numpy as np
import os, random, uuid, logging
from functools import wraps

# =====================
# Konfigurasi Flask
# =====================
app = Flask(__name__)
app.secret_key = "rahasia_super_aman"
app.config.update(
    UPLOAD_FOLDER="static/uploads",
    FLOWER_FOLDER="static/flowers",
    MAX_CONTENT_LENGTH=5 * 1024 * 1024
)
logging.basicConfig(level=logging.INFO)

# =====================
# Load Model & Dataset
# =====================
flowers_model = load_model("flowers_model.keras")

with open("labels.txt", "r", encoding="utf-8") as f:
    flower_labels = [line.strip() for line in f.readlines()]
logging.info(f"Daftar bunga: {flower_labels}")

iris_df = pd.read_csv("iris.csv")

USER = {"kelompok1": "123"}  # login simple

# =====================
# Helper
# =====================
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            flash("⚠️ Silakan login dulu", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"jpg", "jpeg", "png"}

# =====================
# LOGIN
# =====================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username in USER and USER[username] == password:
            session["user"] = username
            flash("✅ Login berhasil", "success")
            return redirect(url_for("home"))
        else:
            flash("❌ Username / password salah", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("✅ Logout berhasil", "info")
    return redirect(url_for("login"))

# =====================
# INDEX
# =====================
@app.route("/")
@login_required
def home():
    return render_template("index.html")

# =====================
# FOTO (CNN)
# =====================
@app.route("/foto", methods=["GET","POST"])
@login_required
def foto():
    hasil, foto_url, related_fotos = None, None, []
    if request.method == "POST":
        file = request.files.get("foto")
        if file and allowed_file(file.filename):
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            filename = f"{uuid.uuid4().hex}_{file.filename}"
            foto_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(foto_path)
            foto_url = url_for("static", filename=f"uploads/{filename}")

            try:
                img = image.load_img(foto_path, target_size=(224,224))
                img_array = image.img_to_array(img) / 255.0
                img_array = np.expand_dims(img_array, axis=0)

                pred = flowers_model.predict(img_array)
                idx = np.argmax(pred)
                confidence = float(pred[0][idx])

                THRESHOLD = 0.90  # minimal 90% confidence
                if confidence >= THRESHOLD and 0 <= idx < len(flower_labels):
                    hasil = f" {flower_labels[idx]} "
                    flower_folder_name = flower_labels[idx]
                    flower_folder_path = os.path.join(app.config["FLOWER_FOLDER"], flower_folder_name)
                    if os.path.exists(flower_folder_path):
                        files = [f for f in os.listdir(flower_folder_path) if f.lower().endswith((".png",".jpg",".jpeg"))]
                        sample = random.sample(files, min(15, len(files)))
                        related_fotos = [url_for("static", filename=f"flowers/{flower_folder_name}/{f}") for f in sample]
                else:
                    hasil = "⚠️ Gambar tidak dikenali sebagai bunga"

            except Exception as e:
                logging.error(f"Error prediksi CNN: {e}")
                hasil = "⚠️ Gagal memproses gambar"
        else:
            flash("⚠️ File tidak valid (hanya .jpg, .jpeg, .png)", "danger")
    return render_template("foto.html", hasil=hasil, foto_url=foto_url, related_fotos=related_fotos)

# =====================
# NUMERIK (IRIS)
# =====================
@app.route("/numerik", methods=["GET","POST"])
@login_required
def numerik():
    prediction, related_fotos, method_info = None, [], ""
    if request.method == "POST":
        try:
            # Ambil input pengguna
            sl = float(request.form.get("sepal_length", "0"))
            sw = float(request.form.get("sepal_width", "0"))
            pl = float(request.form.get("petal_length", "0"))
            pw = float(request.form.get("petal_width", "0"))
            input_array = np.array([sl, sw, pl, pw])

            # Ambil data fitur dari iris.csv
            features = iris_df[['sepal_length','sepal_width','petal_length','petal_width']].values

            # Hitung jarak ke semua data
            distances = np.linalg.norm(features - input_array, axis=1)
            idx_min = np.argmin(distances)
            min_distance = distances[idx_min]

            # Hitung threshold adaptif berdasarkan rata-rata + 2×std
            from itertools import combinations
            all_dists = [
                np.linalg.norm(features[i] - features[j])
                for i, j in combinations(range(len(features)), 2)
            ]
            mean_dist = np.mean(all_dists)
            std_dist = np.std(all_dists)
            THRESHOLD = mean_dist + 2 * std_dist

            # Hitung tingkat kemiripan (0–100%)
            similarity = max(0, 100 - (min_distance / THRESHOLD) * 100)
            similarity = round(similarity, 2)

            # Tentukan level keyakinan
            if similarity >= 85:
                confidence = "Tinggi"
            elif similarity >= 60:
                confidence = "Sedang"
            else:
                confidence = "Rendah"

            # Jika jarak melebihi threshold → data tidak cocok
            if min_distance > THRESHOLD:
                prediction = f"⚠️ Data tidak cocok dengan dataset.<br>Tingkat kemiripan: {similarity}% (Akurasi: {confidence})"
                method_info = f"Metode: KNN + Validasi Jarak (Threshold adaptif = {THRESHOLD:.2f})"
            else:
                # Ambil spesies terdekat
                species = iris_df.iloc[idx_min]['species']
                iris_info = {
                    "Iris-setosa": "Sepal pendek & lebar, Petal sangat kecil.",
                    "Iris-versicolor": "Sepal & Petal berukuran sedang.",
                    "Iris-virginica": "Sepal & Petal panjang dan lebar."
                }

                # Kalimat naratif
                desc = iris_info.get(species, "")
                prediction = (
                    f"🌸 Jenis bunga paling mirip: <b>{species}</b><br>"
                    f"Tingkat kemiripan: <b>{similarity}%</b> (Akurasi: {confidence})<br>"
                    f"Ciri khas: {desc}"
                )

                method_info = f"Metode: KNN (Jarak Euclidean, Threshold adaptif = {THRESHOLD:.2f})"

                # Gambar contoh
                species_folder = species.lower().replace("iris-", "")
                flower_folder = os.path.join(app.config["FLOWER_FOLDER"], species_folder)
                if os.path.exists(flower_folder):
                    files = [f for f in os.listdir(flower_folder) if f.lower().endswith((".png",".jpg",".jpeg"))]
                    sample = random.sample(files, min(15, len(files)))
                    related_fotos = [url_for("static", filename=f"flowers/{species_folder}/{f}") for f in sample]

        except Exception as e:
            logging.error(f"Error numerik: {e}")
            prediction = "⚠️ Data numerik tidak valid"

    return render_template("numerik.html", prediction=prediction, related_fotos=related_fotos, method_info=method_info)

# =====================
# CARI NAMA BUNGA
# =====================
@app.route("/cari", methods=["GET","POST"])
@login_required
def cari():
    prediction, related_fotos, method_info = None, [], ""
    if request.method == "POST":
        search = request.form.get("search", "").lower()
        found = [f for f in flower_labels if search in f.lower()]
        if found:
            prediction = "Hasil Pencarian: " + ", ".join(found)
            method_info = "Metode: String Matching"
            for flower in found:
                flower_folder = os.path.join(app.config["FLOWER_FOLDER"], flower)
                if os.path.exists(flower_folder):
                    files = [f for f in os.listdir(flower_folder) if f.lower().endswith((".png",".jpg",".jpeg"))]
                    sample = random.sample(files, min(15,len(files)))
                    related_fotos += [url_for("static", filename=f"flowers/{flower}/{f}") for f in sample]
        else:
            prediction = "Tidak ditemukan"
    return render_template("cari.html", prediction=prediction, related_fotos=related_fotos, method_info=method_info)

@app.after_request
def skip_ngrok_warning(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# =====================
# RUN
# =====================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    app.run(host="0.0.0.0", port=5000)