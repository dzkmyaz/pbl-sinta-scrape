import requests
from bs4 import BeautifulSoup

# 1. Masukin URL Authors Polman yang udah lu dapet dari web Sinta
url = "https://sinta.kemdikbud.go.id/affiliations/authors/538"

# 2. Pura-pura jadi Browser asli (biar ga diblokir dikira robot)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

print("Lagi nembak web Sinta...")
response = requests.get(url, headers=headers)

# Kalau statusnya 200, berarti sukses tembus webnya!
if response.status_code == 200:
    print("Sukses tembus! Mari kita bongkar HTML-nya...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 3. Cari elemen HTML pembungkus nama-nama dosen
    # (NAMA CLASS DI BAWAH INI CUMA CONTOH, LU HARUS INSPECT ELEMENT DULU DI WEB SINTA)
    # Misal daftar dosen ada di dalam kotak <div class="profile-item">
    dosen_list = soup.find_all('div', class_='profile-item') 
    
    for dosen in dosen_list:
        # Ambil teks namanya
        nama = dosen.find('h5').text.strip()
        
        # Ambil link buat dapetin ID Sinta
        # Misal linknya: /authors/profile/6695576, kita belah ambil angka ujungnya
        link_profil = dosen.find('a')['href']
        id_sinta = link_profil.split('/')[-1] 
        
        print(f"Ketemu! Nama: {nama} | ID Sinta: {id_sinta}")
        
        # NANTI DI SINI KITA TAMBAHIN KODE BUAT INSERT KE MYSQL
        
else:
    print("Waduh, gagal konek ke Sinta bro. Status Error:", response.status_code)
