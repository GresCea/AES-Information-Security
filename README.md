# AES-Information-Security

Proyek ini adalah implementasi dari **Key Distribution Scenario (Needham-Schroeder Protocol Variant)** menggunakan *Socket Programming* di Python. Proyek ini mendemonstrasikan distribusi *Session Key* yang aman melalui *Key Distribution Center* (KDC) antara dua entitas (Alice dan Bob), dilanjutkan dengan komunikasi dua arah yang dienkripsi menggunakan algoritma AES.

## Fitur Utama
1. **Arsitektur 3 Entitas:** Terdiri dari KDC (Server Kunci), Alice (Inisiator/Client), dan Bob (Responder/Server).
2. **Implementasi AES-128 Manual:** Algoritma enkripsi dan dekripsi AES-128 dibuat murni secara matematis dari nol (S-Box, ShiftRows, MixColumns, dll) tanpa menggunakan *library* kriptografi eksternal.
3. **Komunikasi Socket & Threading:** Menggunakan TCP Sockets untuk transmisi jaringan dan *threading* untuk *chat* dua arah secara real-time.
4. **Keamanan Master Key:** Master Key diinput secara interaktif saat runtime (tidak di-*hardcode*).
5. **Format Data:** Plaintext dan Master Key menggunakan ASCII, sedangkan *ciphertext* ditransmisikan dan ditampilkan dalam format Hexadecimal.

## Struktur Direktori
```text
Tugas_Keamanan_Informasi/
├── README.md           # Dokumentasi proyek
├── config.py           # Konfigurasi IP address dan Port
├── aes_manual.py       # Implementasi algoritma AES-128 manual
├── utils.py            # Fungsi utilitas (padding, encrypt, decrypt)
├── kdc.py              # Skrip Key Distribution Center
├── alice.py            # Skrip Entitas Alice (Client)
└── bob.py              # Skrip Entitas Bob (Server)
```

## Skenario Lingkungan (2 Perangkat)
Untuk simulasi jaringan ini, arsitektur disebar ke dalam dua komputer berbeda (Device A dan Device B) yang berada dalam satu jaringan lokal (LAN/Wi-Fi yang sama):

* **Device A (Komputer 1):**
  * **KDC:** Dijalankan di dalam **WSL (Windows Subsystem for Linux)**.
  * **Alice:** Dijalankan langsung di **Windows (Host)**.
* **Device B (Komputer 2):**
  * **Bob:** Dijalankan di **Windows**.

## Persiapan dan Konfigurasi
1. Pastikan **Python 3.x** terinstal di Windows Device A, WSL Device A, dan Windows Device B.
2. Dapatkan IP Address yang dibutuhkan:
   * **IP WSL (KDC):** Buka terminal WSL di Device A, ketik `hostname -I`.
   * **IP Device B (Bob):** Buka CMD di Device B, ketik `ipconfig` (catat IPv4 Address pada Wireless/Ethernet adapter).
3. Buka file `config.py` (samakan isi file ini di semua tempat) dan sesuaikan:
   ```python
   KDC_IP = '172.x.x.x'      # Ganti dengan IP WSL di Device A
   KDC_PORT = 5000
   
   BOB_IP = '192.168.x.x'    # Ganti dengan IPv4 Windows Device B
   BOB_PORT = 5002
   ```
4. **Penting (Firewall Device B):** Karena Bob bertindak sebagai *Server* di Device B, pastikan Anda membuat *Inbound Rule* pada Windows Firewall Device B untuk mengizinkan (Allow) koneksi TCP pada port `5002`. Jika tidak, Alice dari Device A akan mengalami *Connection Refused/Timeout*.

## Cara Menjalankan Program

Jalankan skrip secara berurutan:

**1. Jalankan KDC (di WSL Device A)**
```bash
python3 kdc.py
```
* *Input:* Masukkan Master Key Alice dan Master Key Bob (harus **tepat 16 karakter** ASCII, contoh: `MasterKeyAlice12` dan `MasterKeyBob1234`).

**2. Jalankan Bob (di Windows Device B)**
```cmd
python bob.py
```
* *Input:* Masukkan Master Key Bob yang **sama persis** dengan yang dimasukkan di KDC.
* Bob akan masuk ke status *standby*.

**3. Jalankan Alice (di Windows Device A)**
```cmd
python alice.py
```
* *Input:* Masukkan Master Key Alice yang **sama persis** dengan yang dimasukkan di KDC.
* Proses autentikasi 5 langkah akan berjalan. Jika berhasil, layar akan menampilkan mode *chat*.menampilkan mode *chat*.

## Panduan Wireshark (Monitoring)
Untuk membuktikan bahwa komunikasi berjalan dan terenkripsi, gunakan Wireshark di **Windows Device A**:

1. Buka Wireshark.
2. Pilih 2 antarmuka jaringan secara bersamaan (tahan `Ctrl`):
   * `vEthernet (WSL)` (untuk menangkap *traffic* antara Alice Windows <-> KDC WSL).
   * `Wi-Fi` atau `Ethernet` (antarmuka utama Anda yang terhubung ke jaringan lokal, untuk menangkap *traffic* antara Alice Device A <-> Bob Device B).
3. Masukkan filter berikut di kolom *Display Filter*:
   ```text
   tcp.port == 5000 or tcp.port == 5002
   ```
4. Klik **Start Capture**. Anda akan melihat paket TCP yang berisi *payload* terenkripsi dalam bentuk Hexadecimal.

## Alur Skenario Kunci (5 Langkah)
1. **(Alice ➔ KDC):** Alice mengirim request `IDA || IDB || N1`.
2. **(KDC ➔ Alice):** KDC merespons pesan yang dienkripsi dengan Master Key Alice: `E(Ka, [Ks || IDB || N1 || E(Kb, [Ks || IDA])])`.
3. **(Alice ➔ Bob):** Alice mem-forward tiket ke Bob: `E(Kb, [Ks || IDA])`.
4. **(Bob ➔ Alice):** Bob mengirim tantangan Nonce 2: `E(Ks, N2)`.
5. **(Alice ➔ Bob):** Alice membalas tantangan: `E(Ks, N2 - 1)`.

Setelah langkah 5, Alice dan Bob menggunakan `Ks` (Session Key) untuk saling *chat* dua arah dengan AES-128.