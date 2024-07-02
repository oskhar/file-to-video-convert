## file2video

## Langkah-langkah

Pertama, instal dependencies:

```bash
pip install -r requirements.txt
```

Kita memerlukan OpenGL, GLib, dan FFmpeg. Instal mereka di Ubuntu/Debian dengan:

```bash
sudo apt-get install libgl1 libglib2.0-0 ffmpeg
```

Kemudian, Anda bisa menjalankan perintah berikut untuk mengonversi file ke video:

```bash
python file2video.py --encode test/test100k.txt out.mp4
```

Dan Anda bisa menjalankan perintah berikut untuk mengonversi video kembali ke file:

```bash
python file2video.py --decode out.mp4 ./
```
