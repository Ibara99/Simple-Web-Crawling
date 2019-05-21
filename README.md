# Simple Web Crawler

​	*Program ini digunakan untuk mengekstrak data dari sebuah website. Penjelasan lebih lengkap (termasuk analisis), klik [di sini](https://ibara99.github.io/Simple%20Web%20Crawler/).*

# Pengantar

> Ucapan terima kasih kepada Bapak [Mulaab, S.Si., M.Kom.](https://forlap.ristekdikti.go.id/dosen/detail/RTA5QTg4RjctMjBEQy00QThELUI4REYtREQ5ODAzMzU0MjUz) selaku Dosen Pembimbing kami

> Nama 			: Ibnu Asro Putra
>
> NRP			: 160411100023
>
> Mata kuliah 		: Penambangan dan Pencarian Web - 2019
>
> Jurusan			: Teknik Informatika
>
> Perguruan Tinggi	: Universitas Trunojoyo Madura

# Environment 

*Program ini dijalankan menggunakan:*

- Bahasa Python, dengan library:
  - BeautifulSoup4 (install menggunakan pip)
  - requests (install menggunakan pip)
  - SQLite3 (library bawaan python)
  - csv  (library bawaan python)
  - numpy (install menggunakan pip)
  - scipy (install menggunakan pip)
  - scikit-learn (install menggunakan pip, perlu untuk install numpy dan scipy terlebih dulu)
  - Scikit-fuzzy (install menggunakan pip, perlu untuk install numpy dan scipy terlebih dulu)
  - networkx
  - matplotlib
- Website target : [Jurnal Online](https://garuda.ristekdikti.go.id))

> Jika anda memutuskan untuk meng-update data, maka Program **hanya** bisa dijalankan menggunakan Internet, atau program akan error

> Setiap kali program dijalankan, akan muncul file baru bernama `test.db`, dan beberapa file `csv`. File tersebut merupakan file database serta output program.

# Daftar isi

Berikut deskripsi dari setiap file di repositori ini. Untuk Dokumentasinya silakan klik [di sini](https://ibara99.github.io/simple-web-crawling)

* web_crawl.py

  Merupakan file source code untuk Web Content Mining

* test.db

  Merupakan file database sqlite untuk menyimpan hasil crawling pada Web Content Mining

* File CSV merupakan output dari web_crawl.py, dengan detail:

  * bow_manual_1.csv : merupakan hasil Bag of Words
  * tfidf1.csv : merupakan hasil tfidf
  * seleksiFitur1.csv : merupakan hasil seleksi fitur menggunakan pearson
  * Cluster1.csv : merupakan hasil dari clustering **tanpa** seleksi fitur
  * Cluster1FS.csv : merupakan hasil dari clustering **dengan** seleksi fitur

* Web Structure Mining.py

  Merupakan file source code untuk Web Structure Mining

