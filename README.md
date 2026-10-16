# YOLO-CAM

Program Python berbasis terminal untuk mendeteksi **orang**, **tas tangan**, dan
**ponsel** pada foto serta video. Program membaca file dari folder input,
menjalankan deteksi objek, lalu menyimpan salinan yang sudah diberi kotak dan
label deteksi ke folder hasil.

> **Catatan:** Walaupun nama proyeknya YOLO-CAM, versi ini tidak menggunakan
> webcam secara langsung. Input yang diproses adalah foto dan video yang sudah
> tersimpan di folder proyek.

## Fitur

- Memilih pemrosesan foto atau video melalui menu terminal.
- Memproses file satu per satu dan menampilkan kotak, label, serta skor deteksi.
- Menggunakan satu model yang dimuat saat pertama kali memilih file, lalu
  menggunakannya kembali selama program berjalan.
- Membuat folder input dan hasil jika belum tersedia.
- Tidak menimpa file hasil yang sudah ada.

## Model dan pengaturan deteksi

Proyek menggunakan **Ultralytics YOLO11 Nano**, dengan bobot
[`yolo11n.pt`](./yolo11n.pt). Ini adalah model deteksi objek pralatih pada
dataset COCO, bukan model yang dilatih khusus untuk proyek ini.

Program hanya menampilkan tiga kelas dari kelas-kelas yang dikenali model:

| Nama kelas model | Yang dideteksi |
| --- | --- |
| `person` | Orang |
| `handbag` | Tas tangan |
| `cell phone` | Ponsel |

Ambang keyakinan deteksi diatur ke `0.25` (25%). Deteksi dengan skor di bawah
ambang tersebut tidak ditampilkan. Pengaturan ini terdapat pada konstanta
`CONFIDENCE` di `app.py`. Model hanya menghasilkan prediksi; program tidak
mengenali identitas seseorang atau isi/nomor ponsel.

Jika file `yolo11n.pt` tidak ditemukan di direktori kerja saat program
dijalankan, Ultralytics dapat mencoba mengunduh bobot tersebut. Jalankan
perintah dari direktori utama proyek agar file model lokal ditemukan.

## Kebutuhan

- Python 3.10–3.12 disarankan.
- Paket Python yang tercantum dalam [`requirements.txt`](./requirements.txt):
  - `ultralytics` — pemuatan model dan inferensi YOLO.
  - `opencv-python` — membaca foto/video serta menyimpan hasil.
- Ruang disk dan memori yang cukup untuk PyTorch, dependensinya, dan bobot
  model.

Inferensi dapat berjalan di CPU; pemrosesan video pada CPU mungkin lebih lambat.
Ultralytics/PyTorch dapat memakai GPU jika instalasi dan perangkat keras yang
sesuai tersedia, tetapi proyek ini tidak mengonfigurasi GPU secara eksplisit.

## Struktur folder

```text
YOLO-CAM/
├── app.py
├── requirements.txt
├── yolo11n.pt
├── assets/
│   ├── photo/       # Letakkan foto di sini
│   └── video/       # Letakkan video di sini
└── result/
    ├── photo/       # Foto hasil deteksi
    └── video/       # Video hasil deteksi
```

Folder `assets/photo`, `assets/video`, dan folder hasil terkait dibuat otomatis
jika belum ada.

### Format input yang didukung

- **Foto:** `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`
- **Video:** `.mp4`, `.avi`, `.mov`, `.mkv`, `.m4v`, `.webm`

Ekstensi diperiksa tanpa membedakan huruf besar-kecil. Letakkan file di folder
yang sesuai sebelum menjalankan program.

## Instalasi dan menjalankan di Windows

Buka PowerShell di direktori proyek:

```powershell
cd D:\Project-Coding\YOLO-CAM
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

Jika PowerShell menolak aktivasi skrip, Anda dapat menjalankan interpreter
virtualenv secara langsung:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Jika ini pertama kalinya dependensi dan bobot model digunakan, instalasi paket
atau pengunduhan bobot memerlukan koneksi internet.

## Menjalankan di WSL2 Arch Linux

Jika kebijakan Windows memblokir DLL PyTorch di Windows, WSL2 dapat menjadi
alternatif untuk menjalankan versi Linux tanpa menonaktifkan fitur keamanan
Windows. Contoh berikut menggunakan `uv` untuk menyediakan Python 3.12 dan
lingkungan terpisah di direktori home Linux:

```bash
sudo pacman -Syu uv
uv python install 3.12
uv venv --python 3.12 ~/.venvs/yolo-cam
uv pip install --python ~/.venvs/yolo-cam/bin/python \
  torch --index-url https://download.pytorch.org/whl/cpu
uv pip install --python ~/.venvs/yolo-cam/bin/python \
  -r /mnt/d/Project-Coding/YOLO-CAM/requirements.txt
cd /mnt/d/Project-Coding/YOLO-CAM
~/.venvs/yolo-cam/bin/python app.py
```

Perintah tersebut memasang PyTorch CPU. Jalankan program dari direktori proyek
agar input dan output tetap menggunakan folder proyek di drive Windows. Akses
file melalui `/mnt/d` dapat lebih lambat daripada menyimpan proyek di filesystem
Linux WSL. Jika `uv` sudah tersedia, langkah pemasangannya dapat dilewati.

## Cara menggunakan

Setelah `python app.py` berjalan:

1. Pilih `1` untuk foto, `2` untuk video, atau `q` untuk keluar.
2. Pilih nomor file dari daftar yang ditampilkan. Pilih `0` untuk kembali.
3. Tunggu hingga pemrosesan selesai. Untuk video panjang, kemajuan dicetak
   setiap 100 frame.
4. Buka file hasil pada folder `result/photo` atau `result/video`.

Nama hasil mengikuti pola `FX_C0{nomor}{tanggal}.{ekstensi}`. Tanggal
menggunakan format `DDMMYYYY`; foto disimpan sebagai PNG dan video sebagai MP4.
Contoh: `FX_C0116102026.png`. Nomor mengikuti urutan nama file dalam daftar
input untuk sesi pemilihan tersebut. Jika nama hasil yang sama sudah ada,
program melewati file itu dan tidak menimpa hasil sebelumnya. Pindahkan atau
ubah nama hasil lama jika ingin memproses ulang file dengan nama hasil yang sama.

## Pemrosesan video

Video diproses frame demi frame. Kecepatan frame (FPS) sumber digunakan; jika
FPS tidak terbaca, program memakai 30 FPS. Video keluaran menggunakan codec
`mp4v`. Apabila OpenCV di sistem tidak mendukung codec tersebut, pembuatan video
hasil akan gagal.

## Pemecahan masalah

### `WinError 4551` saat memuat `torch_python.dll` di Windows

Error ini berarti Windows memblokir pemuatan DLL melalui kebijakan Application
Control; bukan berarti file input foto/video yang dipilih rusak. Pada sebagian
konfigurasi, mematikan perlindungan antivirus biasa tidak mengubah kebijakan
Application Control. Log **CodeIntegrity/Operational** pada Event Viewer dapat
menunjukkan kebijakan dan DLL yang diblokir.

Jangan menghapus atau mengganti DLL secara manual. Gunakan WSL2 sebagai alternatif
seperti dijelaskan di atas, atau periksa pengaturan Windows Security dan
kebijakan Application Control yang berlaku sebelum mengubah perlindungan sistem.

### Tidak ada file pada daftar

Pastikan file berada di `assets/photo` atau `assets/video` yang sesuai dan
ekstensinya termasuk format yang didukung.

### File hasil sudah ada

Program sengaja tidak menimpa hasil yang ada. Ubah nama atau pindahkan hasil
lama di dalam folder `result` sebelum menjalankan pemrosesan yang akan memakai
nama hasil yang sama.

## Lisensi

Lihat file [`LICENSE`](./LICENSE) untuk ketentuan lisensi proyek.