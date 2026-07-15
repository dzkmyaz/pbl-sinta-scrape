import requests
from bs4 import BeautifulSoup
import mysql.connector

# 1. KONEKSI KE DATABASE XAMPP
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pbl_dummy"
)
cursor = db.cursor()

# Data tester
id_sinta = "6858002"
nama_dosen = "MUHAMAD ADITYA ROYANDI"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

print(f"Mulai nge-scrape profil {nama_dosen}...")

# 2. MASUKIN DATA KE TABEL INDUK (tb_dosen)
# Pakai INSERT IGNORE biar kalau dosennya udah ada, nggak error
cursor.execute("INSERT IGNORE INTO tb_dosen (id_sinta, nama_dosen) VALUES (%s, %s)", (id_sinta, nama_dosen))
db.commit()

# 3. SCRAPE SKOR UTAMA (Halaman Depan)
url_profil = f"https://sinta.kemdiktisaintek.go.id/authors/profile/{id_sinta}"
res_profil = requests.get(url_profil, headers=headers)

if res_profil.status_code == 200:
    soup = BeautifulSoup(res_profil.text, 'html.parser')
    kotak_skor = soup.find_all('div', class_='col-4 col-lg col-sm-4 col-md-4')
    
    if len(kotak_skor) >= 4:
        # Kita hilangkan titik (misal 1.373 jadi 1373) biar bisa masuk ke kolom INT MySQL
        score_overall = kotak_skor[0].find('div').text.strip().replace('.', '')
        score_3yr = kotak_skor[1].find('div').text.strip().replace('.', '')
        affil_overall = kotak_skor[2].find('div').text.strip().replace('.', '')
        affil_3yr = kotak_skor[3].find('div').text.strip().replace('.', '')
        
        sql_skor = """INSERT INTO tb_skor_utama (id_sinta, score_overall, score_3yr, affil_score, affil_score_3yr) 
                      VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql_skor, (id_sinta, score_overall, score_3yr, affil_overall, affil_3yr))
        db.commit()
        print("[OK] Skor Utama berhasil masuk tb_skor_utama!")

# 4. SCRAPE METRIK SUMMARY (Tab Metrics)
# 4. SCRAPE METRIK SUMMARY (Tab Metrics)
url_metrics = f"https://sinta.kemdiktisaintek.go.id/authors/profile/{id_sinta}/?view=metrics"
res_metrics = requests.get(url_metrics, headers=headers)

if res_metrics.status_code == 200:
    soup_metrik = BeautifulSoup(res_metrics.text, 'html.parser')
    
    # 1. Trik Pintar: Cari semua tabel di halaman
    semua_tabel = soup_metrik.find_all('table')
    tabel_target = None
    
    # 2. Seleksi tabel yang beneran tabel Summary
    for tbl in semua_tabel:
        isi_teks = tbl.text.lower()
        # Kalau di dalam tabel itu ada kata kunci ini, berarti itu target kita!
        if 'gscholar' in isi_teks and 'h-index' in isi_teks:
            tabel_target = tbl
            break
            
    if tabel_target:
        scopus_data = {}
        gscholar_data = {}
        
        # Peta kunci kita bikin huruf kecil semua biar nggak sensitif huruf besar/kecil
        key_map = {
            'article': 'article', 
            'citation': 'citation', 
            'cited document': 'cited_document',
            'h-index': 'h_index', 
            'i10-index': 'i10_index', 
            'g-index': 'g_index'
        }
        
        for row in tabel_target.find_all('tr'):
            cols = row.find_all('td')
            # Pastiin barisnya punya 3 kolom (Nama Metrik, Scopus, GScholar)
            if len(cols) >= 3:
                nama_baris = cols[0].text.strip().lower()
                
                # Cocokin nama baris sama key_map kita
                for key, db_col in key_map.items():
                    if key in nama_baris:
                        # Ambil angkanya (kalau kosong, otomatis jadi '0')
                        val_scopus = cols[1].text.strip().replace('.', '') or '0'
                        val_gscholar = cols[2].text.strip().replace('.', '') or '0'
                        
                        scopus_data[db_col] = val_scopus
                        gscholar_data[db_col] = val_gscholar
        
        # Masukin sebaris buat Scopus
        sql_metrik = """INSERT INTO tb_metrik_summary (id_sinta, sumber, article, citation, cited_document, h_index, i10_index, g_index) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_metrik, (id_sinta, 'Scopus', scopus_data.get('article', 0), scopus_data.get('citation', 0), scopus_data.get('cited_document', 0), scopus_data.get('h_index', 0), scopus_data.get('i10_index', 0), scopus_data.get('g_index', 0)))
        
        # Masukin sebaris lagi buat GScholar
        cursor.execute(sql_metrik, (id_sinta, 'GScholar', gscholar_data.get('article', 0), gscholar_data.get('citation', 0), gscholar_data.get('cited_document', 0), gscholar_data.get('h_index', 0), gscholar_data.get('i10_index', 0), gscholar_data.get('g_index', 0)))
        
        db.commit()
        print("[OK] Metrik Scopus & GScholar berhasil masuk tb_metrik_summary!")
    else:
        print("[GAGAL] Tabel Summary yang dicari nggak ketemu di HTML-nya.")

cursor.close()
db.close()
print("Selesai bro! Cek phpMyAdmin lu sekarang.")