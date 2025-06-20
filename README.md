# Aplikasi Steganografi Gambar dengan Streamlit

Aplikasi ini memungkinkan pengguna untuk **menyisipkan (encode)** dan **mengambil kembali (decode)** pesan teks rahasia di dalam gambar menggunakan teknik *steganografi*. Dibuat dengan antarmuka interaktif menggunakan **Streamlit**.

---

## Fitur

- Upload gambar untuk disisipkan pesan rahasia.
- Menyisipkan pesan teks ke dalam gambar.
- Menyimpan gambar hasil encode dengan pesan tersembunyi.
- Menampilkan gambar hasil encode.
- Mengambil kembali pesan yang disisipkan dari gambar.
- Tampilan antarmuka sederhana dan interaktif dengan Streamlit.

---

## Teknologi yang Digunakan

- Python 3.12
- [Streamlit](https://streamlit.io/)
- numpy==1.26.4
- matplotlib==3.8.4
- Pillow==10.3.0
- PyWavelets==1.5.0
- seaborn==0.13.2
- scikit-image==0.22.0

---

## Cara Menjalankan Aplikasi

1. **Clone repository ini** (atau pindah ke folder proyek):
   ```bash
   git clone https://github.com/Faizmunif/Steganografi_with_LSB_and_DWT.git
   cd Steganografi_with_LSB_and_DWT

2. **Siapkan env**
   ```bash
   python -m venv steganografi-env
   steganografi-env\Scripts\activate  # Windows

4. **Install requirements.txt**
   ```bash
   pip install -r requirements.txt

6. **Run streamlit**
   ```bash
   streamlit run (nama file.py)


