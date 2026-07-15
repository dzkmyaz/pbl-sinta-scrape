import requests
from bs4 import BeautifulSoup

id_sinta = "6858002"
url_profil = f"https://sinta.kemdiktisaintek.go.id/authors/profile/{id_sinta}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Lagi ngebuka profil ID: {id_sinta}...")
response = requests.get(url_profil, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Kita targetin persis sesuai nama class yang ada di screenshot lu
    kotak_skor = soup.find_all('div', class_='col-4 col-lg col-sm-4 col-md-4')
    
    # Cek minimal ada 2 kotak (biar dapet Overall sama 3Yr)
    if len(kotak_skor) >= 2:
        # Kotak pertama (index 0) itu SINTA Score Overall
        # Kita ambil div paling pertama di dalemnya (.find('div')) terus ambil teksnya
        score_overall = kotak_skor[0].find('div').text.strip()
        
        # Kotak kedua (index 1) itu SINTA Score 3Yr
        score_3yr = kotak_skor[1].find('div').text.strip()

        print("-" * 30)
        print("BERHASIL NARIK DATA:")
        print(f"SINTA Score Overall : {score_overall}")
        print(f"SINTA Score 3Yr     : {score_3yr}")
        print("-" * 30)
        
    else:
        print("Gagal bro, tag HTML-nya ga ketemu. Cek lagi ya.")

else:
    print(f"Gagal tembus profil. Status: {response.status_code}")