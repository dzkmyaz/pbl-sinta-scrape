import requests
from bs4 import BeautifulSoup
import mysql.connector
import time

# 1. KONEKSI KE DATABASE XAMPP
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pbl_dummy"
)
cursor = db.cursor()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 2. FUNGSI MESIN PENGERUK (Udah dipasang pelindung error)
def scrape_dosen(id_sinta, nama_dosen):
    print(f"[*] Menarik data: {nama_dosen} (ID: {id_sinta})")
    
    try:
        # A. Masukin ke tabel Induk (Pakai IGNORE biar kalau double ga error)
        cursor.execute("INSERT IGNORE INTO tb_dosen (id_sinta, nama_dosen) VALUES (%s, %s)", (id_sinta, nama_dosen))
        db.commit()

        # B. Tarik Skor Utama (4 Lingkaran Kuning)
        url_profil = f"https://sinta.kemdiktisaintek.go.id/authors/profile/{id_sinta}"
        res_profil = requests.get(url_profil, headers=headers, timeout=10)
        
        if res_profil.status_code == 200:
            soup = BeautifulSoup(res_profil.text, 'html.parser')
            kotak_skor = soup.find_all('div', class_='col-4 col-lg col-sm-4 col-md-4')
            
            if len(kotak_skor) >= 4:
                score_overall = kotak_skor[0].find('div').text.strip().replace('.', '') or '0'
                score_3yr = kotak_skor[1].find('div').text.strip().replace('.', '') or '0'
                affil_overall = kotak_skor[2].find('div').text.strip().replace('.', '') or '0'
                affil_3yr = kotak_skor[3].find('div').text.strip().replace('.', '') or '0'
                
                sql_skor = "INSERT INTO tb_skor_utama (id_sinta, score_overall, score_3yr, affil_score, affil_score_3yr) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql_skor, (id_sinta, score_overall, score_3yr, affil_overall, affil_3yr))
                db.commit()
                print("    -> [OK] Skor Sinta masuk!")

        # C. Tarik Metrik Summary (Trik Pencarian Pintar)
        url_metrics = f"https://sinta.kemdiktisaintek.go.id/authors/profile/{id_sinta}/?view=metrics"
        res_metrics = requests.get(url_metrics, headers=headers, timeout=10)
        
        if res_metrics.status_code == 200:
            soup_metrik = BeautifulSoup(res_metrics.text, 'html.parser')
            semua_tabel = soup_metrik.find_all('table')
            tabel_target = None
            
            for tbl in semua_tabel:
                isi_teks = tbl.text.lower()
                if 'gscholar' in isi_teks and 'h-index' in isi_teks:
                    tabel_target = tbl
                    break
                    
            if tabel_target:
                scopus_data = {}
                gscholar_data = {}
                key_map = {
                    'article': 'article', 'citation': 'citation', 'cited document': 'cited_document',
                    'h-index': 'h_index', 'i10-index': 'i10_index', 'g-index': 'g_index'
                }
                
                for row in tabel_target.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        nama_baris = cols[0].text.strip().lower()
                        for key, db_col in key_map.items():
                            if key in nama_baris:
                                scopus_data[db_col] = cols[1].text.strip().replace('.', '') or '0'
                                gscholar_data[db_col] = cols[2].text.strip().replace('.', '') or '0'
                
                sql_metrik = """INSERT INTO tb_metrik_summary (id_sinta, sumber, article, citation, cited_document, h_index, i10_index, g_index) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                # Insert Scopus
                cursor.execute(sql_metrik, (id_sinta, 'Scopus', scopus_data.get('article', 0), scopus_data.get('citation', 0), scopus_data.get('cited_document', 0), scopus_data.get('h_index', 0), scopus_data.get('i10_index', 0), scopus_data.get('g_index', 0)))
                # Insert GScholar
                cursor.execute(sql_metrik, (id_sinta, 'GScholar', gscholar_data.get('article', 0), gscholar_data.get('citation', 0), gscholar_data.get('cited_document', 0), gscholar_data.get('h_index', 0), gscholar_data.get('i10_index', 0), gscholar_data.get('g_index', 0)))
                
                db.commit()
                print("    -> [OK] Metrik Scopus & GScholar masuk!")
            else:
                print("    -> [GAGAL] Tabel Summary tidak ketemu.")

    except Exception as e:
        # Kalau ada dosen yang error profilnya, program tetep jalan dan nge-skip ke dosen selanjutnya
        print(f"    -> [ERROR BRAY] Ada masalah pas narik data: {e}")

# 3. MASUKIN DATA 150 DOSEN LU DI SINI
    
daftar_dosen = [
    {"id": "6668333", "nama": "PIPIT ANGGRAENI"},
    {"id": "6777793", "nama": "HILDA KHOIRUNNISA"},
    {"id": "6084229", "nama": "YULIADI ERDANI"},
    {"id": "6717179", "nama": "SETYAWAN AJIE SUKARNO"},
    {"id": "6686671", "nama": "GITA NOVIAN HERMANA"},
    {"id": "6643838", "nama": "HERMAN BUDI HARJA"},
    {"id": "6789563", "nama": "WAHYU ADHIE CANDRA"},
    {"id": "6677041", "nama": "HERI SETIAWAN"},
    {"id": "6723637", "nama": "SAROSA CASTRENA ABADI"},
    {"id": "6695576", "nama": "SUSETYO BAGAS BHASKORO"},
    {"id": "6858002", "nama": "MUHAMAD ADITYA ROYANDI"},
    {"id": "6717379", "nama": "ABDUR ROHMAN HARITS MARTAWIREJA"},
    {"id": "6778574", "nama": "FITRIA SURYATINI"},
    {"id": "6092914", "nama": "GUNGUN MAULANA"},
    {"id": "6789561", "nama": "RIZQI AJI PRATAMA"},
    {"id": "6092647", "nama": "ADHITYA SUMARDI SUNARYA"},
    {"id": "6777141", "nama": "NUR JAMILUDIN RAMADHAN"},
    {"id": "6071601", "nama": "IWAN HARIANTON"},
    {"id": "6717294", "nama": "SANDY BHAWANA MULIA"},
    {"id": "6706159", "nama": "MUHAMMAD RIZKI GORBYANDI NADI"},
    {"id": "6069519", "nama": "ASEP INDRA KOMARA"},
    {"id": "6199625", "nama": "CECEP RUSKANDI"},
    {"id": "6698997", "nama": "HADI SUPRIYANTO"},
    {"id": "6652811", "nama": "ARIS BUDIYARTO"},
    {"id": "6788864", "nama": "HANIF AZIS BUDIARTO"},
    {"id": "6199552", "nama": "ARI SISWANTO"},
    {"id": "6187238", "nama": "RIONA IHSAN MEDIA"},
    {"id": "6082022", "nama": "EMMA DWI ARIYANI"},
    {"id": "6801988", "nama": "ANGGRAENI MULYADEWI"},
    {"id": "6646191", "nama": "YOGI MULDANI HENDRAWAN"},
    {"id": "6085850", "nama": "SITI AMINAH"},
    {"id": "6941627", "nama": "BOLO DWIARTOMO"},
    {"id": "6084257", "nama": "ISMAIL ROKHIM"},
    {"id": "6105469", "nama": "NURYANTI"},
    {"id": "6128063", "nama": "WIWIK PURWADI"},
    {"id": "6133841", "nama": "MERI RAHMI"},
    {"id": "6139238", "nama": "RONI KUSNOWO"},
    {"id": "6777158", "nama": "SUHARYADI PANCONO"},
    {"id": "6139265", "nama": "RIKY ADHIHARTO"},
    {"id": "6055091", "nama": "SUPRIYADI SADIKIN"},
    {"id": "6717298", "nama": "ABYANUDDIN SALAM"},
    {"id": "6717654", "nama": "HENDY RUDIANSYAH"},
    {"id": "6644011", "nama": "MOHAMMAD HARRY KHOMAS SAPUTRA"},
    {"id": "6802014", "nama": "MUHAMMAD NURSYAM RIZAL"},
    {"id": "6666678", "nama": "AIDA MAHMUDAH"},
    {"id": "6718392", "nama": "DEDE SUJANA"},
    {"id": "6789765", "nama": "RANI NOPRIYANTI"},
    {"id": "6789767", "nama": "DHION KHAIRUL NUGRAHA"},
    {"id": "6777298", "nama": "MUHAMMAD NAHROWI"},
    {"id": "6681200", "nama": "NIA NURYANTI PERMATA"},
    {"id": "6936822", "nama": "AAN EKO SETIAWAN"},
    {"id": "6092786", "nama": "DEWI IDAMAYANTI"},
    {"id": "6802036", "nama": "GANIS SANHAJI"},
    {"id": "6766197", "nama": "MOHAMMAD YAZID DIRATAMA"},
    {"id": "6789759", "nama": "METHA ISLAMEKA"},
    {"id": "6717283", "nama": "DINNY INDRIAN"},
    {"id": "6657355", "nama": "ANDRI PRATAMA"},
    {"id": "6802235", "nama": "REKA ARDI PRAYOGA"},
    {"id": "6669433", "nama": "SOPHIADI GUNARA"},
    {"id": "6121727", "nama": "NOVAL LILANSA"},
    {"id": "6775523", "nama": "YULIAR YASIN ERLANGGA"},
    {"id": "6139256", "nama": "IMAN APRIANA EFFENDI"},
    {"id": "6108457", "nama": "NUR WISMA NUGRAHA"},
    {"id": "6092879", "nama": "OYOK YUDIYANTO"},
    {"id": "6789772", "nama": "ADI SURYA PRADIPTA"},
    {"id": "6811990", "nama": "AYUNISA FITRIANI JILAN"},
    {"id": "6717681", "nama": "DINI HADIANI"},
    {"id": "6652699", "nama": "MOCHAMAD ACHYARSYAH"},
    {"id": "6893928", "nama": "SITI HADIATY YUNINGSIH"},
    {"id": "6777500", "nama": "RIDWAN"},
    {"id": "6789762", "nama": "RISKY AYU FEBRIANI"},
    {"id": "6110966", "nama": "WAHYUDI PURNOMO"},
    {"id": "6139619", "nama": "BUSTAMI IBRAHIM"},
    {"id": "6776727", "nama": "AGUS SURJANA SAEFUDIN"},
    {"id": "6789758", "nama": "WIDYA PRAPTI PRATIWI"},
    {"id": "6043669", "nama": "KURNIAWAN"},
    {"id": "6669534", "nama": "ERY HIDAYAT"},
    {"id": "6723418", "nama": "HARIS SETIAWAN"},
    {"id": "6685025", "nama": "JATA BUDIMAN"},
    {"id": "6085781", "nama": "ACHMAD MUHAMMAD"},
    {"id": "6092779", "nama": "AFAF FADHIL RIFAI"},
    {"id": "6131453", "nama": "RUMINTO SUBEKTI"},
    {"id": "6777295", "nama": "REZA YADI HIDAYAT"},
    {"id": "6874124", "nama": "SIDIK PERMANA"},
    {"id": "6701034", "nama": "CEPI RAMDANI"},
    {"id": "6675927", "nama": "NARWIKANT INDROASYOKO"},
    {"id": "6807696", "nama": "MUHAMMAD FADHLAN AFIF"},
    {"id": "6043724", "nama": "GAMAWAN ANANTO SUBEKTI"},
    {"id": "6661174", "nama": "MOHAMMAD FAUZI"},
    {"id": "6774513", "nama": "DADAN HERYADA WIGENAPUTRA"},
    {"id": "6811014", "nama": "AKIL PRIYAMANGGALA DANADIBRATA"},
    {"id": "6717417", "nama": "NOVI SAKSONO BRODJO MUHADI"},
    {"id": "6700405", "nama": "IWAN GUNAWAN"},
    {"id": "6838916", "nama": "DEDY ARIEFIJANTO"},
    {"id": "6777328", "nama": "MOHAMAD AGUS SOLIHIN"},
    {"id": "6026163", "nama": "DARMA FIRMANSYAH UNDAYAT"},
    {"id": "6778503", "nama": "ANTONIUS ADI SOETOPO"},
    {"id": "6779236", "nama": "DEDE BUCHORI MUSLIM"},
    {"id": "6909058", "nama": "YENI LATIPAH"},
    {"id": "6904584", "nama": "PRADIKA NOVIANDANI"},
    {"id": "6778113", "nama": "NANDANG RUSMANA"},
    {"id": "6857622", "nama": "PANDOE"},
    {"id": "6768322", "nama": "MARTA HAYU RARAS SITA RUKMIKA SARI"},
    {"id": "6850953", "nama": "ADDONIS CANDRA"},
    {"id": "6139418", "nama": "DARMAN"},
    {"id": "6936865", "nama": "ALFISENA JUWANDANA"},
    {"id": "6909088", "nama": "FITRI HIDAYAH SUNDAWATI"},
    {"id": "6970154", "nama": "NOER FAJRIN"},
    {"id": "6690481", "nama": "ADE RAMDAN"},
    {"id": "6936911", "nama": "ILHAM ALI ARRIDHO"},
    {"id": "6808383", "nama": "CASIMAN"},
    {"id": "6966489", "nama": "MUHAMMAD RIZKI AFLAHUL MUZHIDIN"},
    {"id": "6669383", "nama": "DUDDY ARISANDI"},
    {"id": "6969763", "nama": "IHSAN TANAMA SITIO"},
    {"id": "6908852", "nama": "FEBBY FAUZIAH"},
    {"id": "6930277", "nama": "KEVIN PUTRANDA"},
    {"id": "6139445", "nama": "KUS HANALDI"},
    {"id": "6810787", "nama": "SUSENO"},
    {"id": "6835830", "nama": "OTTO PURNAWARMAN"},
    {"id": "6684446", "nama": "MOHAMMAD NUR HIDAYATULLAH"},
    {"id": "6893355", "nama": "DANU JAYA SAPUTRO"},
    {"id": "6993423", "nama": "BALQIS MENTARI EFENDI"},
    {"id": "6876170", "nama": "MUHAMMAD RIZAL ARDIANSYAH"},
    {"id": "6200131", "nama": "ACHMAD SAMBAS"},
    {"id": "6988747", "nama": "RIZKY HERDYAN SUHERMAN"},
    {"id": "6929671", "nama": "RESSA MUHRIPAH NOVIANTI"},
    {"id": "6805977", "nama": "HARTONO WIDJAJA"},
    {"id": "6807683", "nama": "BAYU PRATAMA ADIKARA"},
    {"id": "6043651", "nama": "MOHAMMAD NURDIN"},
    {"id": "6993265", "nama": "FADHILAH DIAN UTAMI"},
    {"id": "6993575", "nama": "NUR FITRIA NINGSIH"},
    {"id": "6807683", "nama": "BAYU PRATAMA ADIKARA"},
    {"id": "6043651", "nama": "MOHAMMAD NURDIN"},
    {"id": "84071", "nama": "BENY BANDANADJAJA"},
    {"id": "6935773", "nama": "FAISAL ABDULRAHMAN BUDIKASIH"},
    {"id": "6937119", "nama": "AHSHONAT KHOERUNNISA"},
    {"id": "6959690", "nama": "RULI AYU SETYOWATI"},
    {"id": "6982792", "nama": "M. GIRIARDA ABRARI"},
    {"id": "6990935", "nama": "RIZKA MULIA ANGGRAENI"},
    {"id": "6934043", "nama": "KHANSA SARAH PUSPITA"},
    {"id": "6937935", "nama": "ADI AKBAR"},
    {"id": "6984580", "nama": "CYNDI ODILIA SUMANTRI"},
    {"id": "6992214", "nama": "OKTA PIANTI RAHAYU"},
    {"id": "6937119", "nama": "AHSHONAT KHOERUNNISA"},
    {"id": "6959690", "nama": "RULI AYU SETYOWATI"},
    {"id": "6982792", "nama": "M. GIRIARDA ABRARI"},
    {"id": "6990935", "nama": "RIZKA MULIA ANGGRAENI"},
    {"id": "6935773", "nama": "FAISAL ABDULRAHMAN BUDIKASIH"},
    {"id": "6993439", "nama": "KHARIFUL SYUKRI"},
    {"id": "6999188", "nama": "KHUZAIVI WAFI JAUHARI"}
]

# 4. SISTEM OTOMATIS BERJALAN (LOOPING)
print("\n=== [ MESIN SCRAPING JATI DIMULAI ] ===\n")

total_dosen = len(daftar_dosen)
for index, dosen in enumerate(daftar_dosen):
    print(f"--- Proses {index + 1} dari {total_dosen} ---")
    
    # Panggil fungsi narik data
    scrape_dosen(dosen["id"], dosen["nama"])
    
    # INI PALING PENTING: Rem Anti-Blokir
    # Kasih jeda 3 detik tiap beres 1 dosen biar server Sinta ga panas
    if (index + 1) < total_dosen:
        waktu_istirahat = 3
        print(f"💤 Istirahat {waktu_istirahat} detik biar ga diblokir...\n")
        time.sleep(waktu_istirahat)

# Tutup pintu database kalau udah kelar semua
cursor.close()
db.close()
print("\n=== [ MISI SELESAI, SEMUA DATA SUDAH DI DATABASE! ] ===")