import requests
from bs4 import BeautifulSoup
import time # Ini library bawaan Python buat bikin jeda waktu

# URL dasar tanpa embel-embel page
base_url = "https://sinta.kemdiktisaintek.go.id/affiliations/authors/538"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

page = 1
total_semua_dosen = 0

print("Mulai ngeruk semua halaman Sinta Polman. Siapin kopi bro...\n")
print("=" * 50)

# Kita pakai while True biar dia jalan terus sampai halamannya mentok/habis
while True:
    print(f"--> Lagi nembak Halaman {page}...")
    
    # Ngerakit URL dengan tambahan parameter page (contoh: .../005001?page=1)
    url_page = f"{base_url}?page={page}"
    response = requests.get(url_page, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        semua_link = soup.find_all('a', href=True)
        
        jumlah_dosen_per_page = 0
        
        for link in semua_link:
            href = link['href']
            if "/authors/profile/" in href:
                id_sinta = href.split('/')[-1]
                nama_dosen = link.text.strip()
                
                if nama_dosen:
                    print(f"[{total_semua_dosen + 1}] {nama_dosen} | ID: {id_sinta}")
                    jumlah_dosen_per_page += 1
                    total_semua_dosen += 1
        
        # LOGIKA STOP: Kalau di halaman ini udah ga nemu dosen satupun, berarti datanya udah habis
        if jumlah_dosen_per_page == 0:
            print("\nUdah mentok bro! Ga ada data lagi di halaman ini.")
            break # Hentikan perulangan
            
        page += 1 # Lanjut ke halaman berikutnya
        
        # INI PALING PENTING: Kasih jeda 3 detik sebelum nembak halaman berikutnya biar ga kena blokir
        print("Tunggu 3 detik biar ga dikira bot...")
        time.sleep(3) 
        
    else:
        print(f"Gagal tembus halaman {page}. Kena blokir atau error server. Status: {response.status_code}")
        break

print("=" * 50)
print(f"Selesai bro! Total jenderal dapet {total_semua_dosen} dosen.")