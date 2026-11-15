# Distributed Blockchain 

Aplikasi web simulasi blockchain interaktif berbasis **Python (Flask)** untuk memvisualisasikan cara kerja struktur blok, algoritma *hashing* **SHA-256**, *Proof of Work (Mining)*, serta efek berantai saat terjadi manipulasi data (*tampering*).

## Fitur Utama

- **Genesis Block Otomatis**: Aplikasi otomatis membuat `Block 0` yang sudah tervalidasi saat pertama kali dijalankan.
- **Input Transaksi per Blok**: Form transaksi (`Pengirim`, `Penerima`, `Jumlah`) berada langsung di dalam setiap kartu blok dan langsung ditampilkan ke kotak **Data** dalam format daftar bernomor.
- **Mining & Pembuatan Blok Otomatis**: Menekan tombol **Mine** akan mencari nilai `Nonce` yang menghasilkan `Hash` berawalan `00` (*difficulty* = 2). Jika yang di-*mine* adalah blok terakhir, blok baru akan otomatis dibuat di sebelahnya.
- **Deteksi Manipulasi Data Real-Time (*Tampering*)**: Kotak **Data** dapat diedit secara langsung. Setiap perubahan teks otomatis menghitung ulang `Hash` blok tersebut dan memperbarui `Prev` pada seluruh blok setelahnya—mengubah status blok terdampak menjadi **Tidak Valid** (merah) secara *real-time*.
- **Reset Blockchain**: Tombol **Reset** mengembalikan seluruh rantai kembali ke kondisi awal (`Block 0` dengan data kosong).

## Struktur Proyek

```text
blockchain-demo/
├── app.py              # Logika Blockchain, Proof of Work, dan routing Flask
├── README.md           # Dokumentasi proyek
└── templates/
    └── index.html      # Antarmuka web dan skrip real-time tamper detection