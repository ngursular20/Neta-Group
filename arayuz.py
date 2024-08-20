import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import pyodbc
import pandas as pd
from tkinter import filedialog
from tkinter import simpledialog
import mysql.connector
from dotenv import load_dotenv
import os
# Global değişkenler
entry_isim = None
entry_ikili_kod = None
entry_uclu_kod = None
entry_ulke = None
tree = None
tree2 = None

# .env dosyasını yükleyin
load_dotenv()

def veritabani_baglan():
    try:
        conn = mysql.connector.connect(
            user= os.getenv('user'),
            password= os.getenv('password'),
            host= os.getenv('host'),
            database= os.getenv('database'),
            port= os.getenv('port')
        )
        return conn
    except mysql.connector.Error as e:
        print("Veritabanına bağlanırken hata oluştu:", e)
        return None

def sorgula():
    conn = veritabani_baglan()
    if conn:
        isim = entry_isim.get()
        ikili_kod = entry_ikili_kod.get()
        uclu_kod = entry_uclu_kod.get()
        ulke = entry_ulke.get()

        # SQL sorgusunu oluştur
        sql_sorgu = """
        SELECT DISTINCT
            HYS.ikili_kod AS havayolu_sirketi_kodu,
            H.isim AS kalkis_havalimani_isim,
            H.havalimani_kodu AS kalkis_havalimani_kodu,
            H.sehir AS kalkis_havalimani_sehir,
            HV.isim AS varis_havalimani_isim,
            HV.havalimani_kodu AS varis_havalimani_kodu,
            HV.sehir AS varis_havalimani_sehir
        FROM
            Ucuslar U
            INNER JOIN Havalimanlari H ON U.kalkis_havalimani_id = H.id
            INNER JOIN HavaYoluSirketiUcuslar HYSU ON U.id = HYSU.ucus_id
            INNER JOIN HavaYoluSirketleri HYS ON HYSU.hava_yolu_sirketi_id = HYS.id
            INNER JOIN Havalimanlari HV ON U.varis_havalimani_id = HV.id
        WHERE 1=1
        """
        parametreler = []

        if isim:
            sql_sorgu += " AND HYS.isim LIKE %s"
            parametreler.append(f'%{isim}%')

        if ikili_kod:
            sql_sorgu += " AND HYS.ikili_kod = %s"
            parametreler.append(ikili_kod)

        if uclu_kod:
            sql_sorgu += " AND HYS.uclu_kod = %s"
            parametreler.append(uclu_kod)

        if ulke:
            sql_sorgu += " AND HYS.ulke LIKE %s"
            parametreler.append(f'%{ulke}%')

        # SQL sorgusunu çalıştır
        cursor = conn.cursor()
        cursor.execute(sql_sorgu, parametreler)
        rows = cursor.fetchall()

        # Tabloyu temizle
        for i in tree.get_children():
            tree.delete(i)

        # Verileri tabloya ekle
        for row in rows:
            # Parantezleri ve tırnak işaretlerini kaldırarak verileri formatla
            clean_row = [data.replace("'", "").replace("(", "").replace(")", "") if isinstance(data, str) else data for data in row]

            tree.insert("", tk.END, values=clean_row)
        conn.close()

        
def sorgula_page2():
    conn = veritabani_baglan()
    if conn:
        kalkis_havalimani = entry_kalkis_havalimani.get()
        varis_havalimani = entry_varis_havalimani.get()
        kalkis_havalimani_kod = entry_kalkis_havalimani_kod.get()
        varis_havalimani_kod = entry_varis_havalimani_kod.get()

        # SQL sorgusunu oluştur
        sql_sorgu = """
        SELECT
            hys.isim AS HavaYoluSirketiIsim,
            hys.ulke AS HavaYoluSirketiUlke,
            hys.ikili_kod AS HavaYoluSirketiIkiliKod,
            hys.uclu_kod AS HavaYoluSirketiUcluKod,
            kalkisHavalimani.havalimani_kodu AS KalkisHavalimaniKodu,
            varisHavalimani.havalimani_kodu AS VarisHavalimaniKodu
        FROM
            Ucuslar u
            INNER JOIN HavaYoluSirketiUcuslar hyu ON u.id = hyu.ucus_id
            INNER JOIN HavaYoluSirketleri hys ON hyu.hava_yolu_sirketi_id = hys.id
            INNER JOIN Havalimanlari kalkisHavalimani ON u.kalkis_havalimani_id = kalkisHavalimani.id
            INNER JOIN Havalimanlari varisHavalimani ON u.varis_havalimani_id = varisHavalimani.id
            WHERE 1=1
        """
        parametreler = []

        if kalkis_havalimani:
            sql_sorgu += " AND kalkisHavalimani.sehir LIKE %s"
            parametreler.append(f'%{kalkis_havalimani}%')

        if varis_havalimani:
            sql_sorgu += " AND varisHavalimani.sehir LIKE %s"
            parametreler.append(f'%{varis_havalimani}%')

        if kalkis_havalimani_kod:
            sql_sorgu += " AND kalkisHavalimani.havalimani_kodu = %s"
            parametreler.append(kalkis_havalimani_kod)

        if varis_havalimani_kod:
            sql_sorgu += " AND varisHavalimani.havalimani_kodu = %s"
            parametreler.append(varis_havalimani_kod)

        # SQL sorgusunu çalıştır
        cursor = conn.cursor()
        cursor.execute(sql_sorgu, parametreler)
        rows = cursor.fetchall()

        # Tabloyu temizle
        for i in tree2.get_children():
            tree2.delete(i)

        # Verileri tabloya ekle
        for row in rows:
            # Parantezleri ve tırnak işaretlerini kaldırarak verileri formatla
            clean_row = [data.replace("'", "").replace("(", "").replace(")", "") if isinstance(data, str) else data for data in row]

            tree2.insert("", tk.END, values=clean_row)
        conn.close()


def havalimani_ekle():
    ad = entry_havalimani_ad.get()
    kita = entry_havalimani_kita.get()
    ulke_kodu = entry_havalimani_ulke_kodu.get()
    sehir = entry_havalimani_sehir.get()
    havalimani_kodu = entry_havalimani_kodu.get()

    if not ad or not kita or not ulke_kodu or not sehir or not havalimani_kodu:
        messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
        return

    conn = veritabani_baglan()
    if conn:
        cursor = conn.cursor()

        # Havalimanı varlık kontrolü SQL sorgusu
        kontrol_sorgu = "SELECT * FROM Havalimanlari WHERE havalimani_kodu = %s"
        kontrol_parametreler = (havalimani_kodu,)

        cursor.execute(kontrol_sorgu, kontrol_parametreler)
        varlik = cursor.fetchone()

        if varlik:
            messagebox.showinfo("Bilgi", "Bu havalimanı zaten var.")
        else:
            # Havalimanı ekleme SQL sorgusu
            sql_sorgu = """
            INSERT INTO Havalimanlari (isim, kita, ulke_kodu, sehir, havalimani_kodu)
            VALUES (%s, %s, %s, %s, %s)
            """
            parametreler = (ad, kita, ulke_kodu, sehir, havalimani_kodu)

            try:
                cursor.execute(sql_sorgu, parametreler)
                conn.commit()
                messagebox.showinfo("Başarılı", "Havalimanı başarıyla eklendi.")
            except pyodbc.Error as e:
                conn.rollback()
                messagebox.showerror("Hata", f"Havalimanı eklenirken bir hata oluştu:\n{e}")
            finally:
                conn.close()

def hava_yolu_sirketi_ekle():
    isim = entry_sirket_isim.get()
    ikili_kod = entry_sirket_ikili_kod.get()
    prefix = entry_sirket_prefix.get()
    uclu_kod = entry_sirket_uclu_kod.get()
    ulke = entry_sirket_ulke.get()

    if not isim or not ikili_kod or not prefix or not uclu_kod or not ulke:
        messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
        return

    conn = veritabani_baglan()
    if conn:
        cursor = conn.cursor()

        # Hava yolu şirketi varlık kontrolü SQL sorgusu
        kontrol_sorgu = "SELECT * FROM HavaYoluSirketleri WHERE ikili_kod = %s"
        kontrol_parametreler = (ikili_kod,)

        cursor.execute(kontrol_sorgu, kontrol_parametreler)
        varlik = cursor.fetchone()

        if varlik:
            messagebox.showinfo("Bilgi", "Bu hava yolu şirketi zaten var.")
        else:
            # Hava yolu şirketi ekleme SQL sorgusu
            sql_sorgu = """
            INSERT INTO HavaYoluSirketleri (isim, ikili_kod, prefix, uclu_kod, ulke)
            VALUES (%s, %s, %s, %s, %s)
            """
            parametreler = (isim, ikili_kod, prefix, uclu_kod, ulke)

            try:
                cursor.execute(sql_sorgu, parametreler)
                conn.commit()
                messagebox.showinfo("Başarılı", "Hava Yolu Şirketi başarıyla eklendi.")
            except pyodbc.Error as e:
                conn.rollback()
                messagebox.showerror("Hata", f"Hava Yolu Şirketi eklenirken bir hata oluştu:\n{e}")
            finally:
                conn.close()

def verileri_guncelle(ikili_kod, ucus_verileri):
    conn = veritabani_baglan()
    if conn:
        cursor = conn.cursor()

        # Güncelleme işlemi
        try:
            # Güncellenecek uçuşları sil
            cursor.execute("DELETE FROM HavaYoluSirketiUcuslar WHERE hava_yolu_sirketi_id = (SELECT id FROM HavaYoluSirketleri WHERE ikili_kod = %s)", (ikili_kod,))
            conn.commit()

            # Yeni uçuş verilerini ekleyin
            for _, row in ucus_verileri.iterrows():
                kalkis_havalimani_kodu = row['Kalkış Havalimanı Kodu']
                varis_havalimani_kodu = row['Varış Havalimanı Kodu']

                # Havalimanları veritabanında var mı kontrol et
                cursor.execute("SELECT id FROM Havalimanlari WHERE havalimani_kodu = %s", (kalkis_havalimani_kodu,))
                kalkis_havalimani_id = cursor.fetchone()

                cursor.execute("SELECT id FROM Havalimanlari WHERE havalimani_kodu = %s", (varis_havalimani_kodu,))
                varis_havalimani_id = cursor.fetchone()

                if kalkis_havalimani_id and varis_havalimani_id:
                    # Uçuşun var olup olmadığını kontrol et
                    cursor.execute("SELECT id FROM Ucuslar WHERE kalkis_havalimani_id = %s AND varis_havalimani_id = %s", (kalkis_havalimani_id[0], varis_havalimani_id[0]))
                    existing_flight_id = cursor.fetchone()

                    if existing_flight_id:
                        # Hava yolu şirketi - uçuş ilişkisini ekleyin
                        cursor.execute("""
                            INSERT INTO HavaYoluSirketiUcuslar (hava_yolu_sirketi_id, ucus_id)
                            VALUES ((SELECT id FROM HavaYoluSirketleri WHERE ikili_kod = %s), %s)
                        """, (ikili_kod, existing_flight_id[0]))
                    elif not existing_flight_id:
                        # Uçuş tablosuna ekle
                        cursor.execute("""
                            INSERT INTO Ucuslar (kalkis_havalimani_id, varis_havalimani_id)
                            VALUES (%s, %s)
                        """, (kalkis_havalimani_id[0], varis_havalimani_id[0]))
                        
                        # Eklenen uçuşun id'sini al
                        cursor.execute("SELECT last_insert_rowid()")
                        new_flight_id = cursor.fetchone()[0]

                        # Hava yolu şirketi - uçuş ilişkisini ekleyin
                        cursor.execute("""
                            INSERT INTO HavaYoluSirketiUcuslar (hava_yolu_sirketi_id, ucus_id)
                            VALUES ((SELECT id FROM HavaYoluSirketleri WHERE ikili_kod = %s), %s)
                        """, (ikili_kod, new_flight_id))

            conn.commit()

        except Exception as e:
            print("Verileri güncelleme hatası:", str(e))
            conn.rollback()

        finally:
            conn.close()

def exel_dosyasini_yukle(ikili_kod):

    if not ikili_kod:
        messagebox.showerror("Hata", "İkili Kodu boş bırakılamaz.")
        return
    
    file_path = filedialog.askopenfilename(filetypes=[("Excel dosyaları", "*.xlsx;*.xls")])

    if not file_path:
        messagebox.showerror("Hata", "Lütfen bir Excel dosyası seçin.")
        return

    try:
        # Excel dosyasını oku
        ucus_verileri = pd.read_excel(file_path)

        # Verileri güncelle
        verileri_guncelle(ikili_kod, ucus_verileri)
        messagebox.showinfo("Başarılı", "Excel dosyası başarıyla yüklendi ve veriler güncellendi.")
    
    except Exception as e:
        messagebox.showerror("Hata", f"Excel dosyası yüklenirken bir hata oluştu:\n{e}")

def create_page3():
    page3 = tk.Frame(notebook, bg='white')

    page3_title = tk.Label(page3, text="Veri Ekleme-Güncelleme İşlemleri", font=("Helvetica", 12), bg='white')
    page3_title.grid(row=0, column=0, columnspan=8, pady=10)


    # Şirket İsmi, İkili Kodu, Prefix, Üçlü Kodu, Ülke için label ve entry
    labels_sirket = ["Şirket İsmi", "İkili Kodu", "Prefix", "Üçlü Kodu", "Ülke"]
    entries_sirket = [tk.Entry(page3) for _ in range(len(labels_sirket))]

    global entry_sirket_isim, entry_sirket_ikili_kod, entry_sirket_prefix, entry_sirket_uclu_kod, entry_sirket_ulke
    entry_sirket_isim, entry_sirket_ikili_kod, entry_sirket_prefix, entry_sirket_uclu_kod, entry_sirket_ulke = entries_sirket

    for i, (label_text, entry) in enumerate(zip(labels_sirket, entries_sirket)):
        label = tk.Label(page3, text=label_text)
        label.grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
        entry.grid(row=i + 1, column=1, padx=5, pady=5, sticky="e")

    sirket_ekle_button = tk.Button(page3, text="Şirket Ekle", command=hava_yolu_sirketi_ekle)
    sirket_ekle_button.grid(row=len(labels_sirket) + 1, column=0, columnspan=2, pady=10)

    # Havalimanı Adı, Kıta, Ülke Kodu, Şehir, Havalimanı Kodu için label ve entry
    labels3 = ["Havalimanı Adı", "Kıta", "Ülke Kodu", "Şehir", "Havalimanı Kodu"]
    entries3 = [tk.Entry(page3) for _ in range(len(labels3))]

    global entry_havalimani_ad, entry_havalimani_kita, entry_havalimani_ulke_kodu, entry_havalimani_sehir, entry_havalimani_kodu
    entry_havalimani_ad, entry_havalimani_kita, entry_havalimani_ulke_kodu, entry_havalimani_sehir, entry_havalimani_kodu = entries3

    for i, (label_text, entry) in enumerate(zip(labels3, entries3)):
        label = tk.Label(page3, text=label_text)
        label.grid(row=i + 1, column=5, padx=5, pady=5, sticky="w")
        entry.grid(row=i + 1, column=6, padx=5, pady=5, sticky="e")

    havalimani_ekle_button = tk.Button(page3, text="Havalimanı Ekle", command=havalimani_ekle)
    havalimani_ekle_button.grid(row=len(labels3) + 1, column=6, columnspan=2, pady=10)

    # İkili Kod Girişi için label ve entry
    ikili_kod_label = tk.Label(page3, text="İkili Kod Girişi:")
    ikili_kod_label.grid(row=len(labels3) + 2, column=3, padx=5, pady=5, sticky="w")

    ikili_kod_entry = tk.Entry(page3)
    ikili_kod_entry.grid(row=len(labels3) + 2, column=4, padx=5, pady=5, sticky="e")

    # Excel Dosyasını Yükle ve Verileri Güncelle butonu
    excel_yukle_button = tk.Button(page3, text="Excel Dosyasını Yükle ve Verileri Güncelle", command=lambda: exel_dosyasini_yukle(ikili_kod_entry.get()))
    excel_yukle_button.grid(row=len(labels3) + 3, column=3, columnspan=2, pady=10)

    return page3


root = tk.Tk()
root.title("netagroup")
root.geometry("895x550")
root.configure(bg='navy')

# Yeniden boyutlanabilir düzen için konfigürasyon
for i in range(8):
    root.rowconfigure(i, weight=1)
    root.columnconfigure(i, weight=1)

logo_image = Image.open("logo2.png")
logo_photo = ImageTk.PhotoImage(logo_image)

logo_label = tk.Label(root, image=logo_photo, bg='navy')
logo_label.photo = logo_photo
logo_label.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

page1 = tk.Frame(notebook, bg='white')
page2 = tk.Frame(notebook, bg='white')

page1_title = tk.Label(page1, text="Havayolu Şirket Bilgileri Girerek Uçuş Sorgulama", font=("Helvetica", 12), bg='white')
page1_title.grid(row=0, column=0, columnspan=8, pady=10)

labels = ["Şirket İsmi", "İkili Kodu", "Üçlü Kodu", "Ülke"]
entries = [tk.Entry(page1) for _ in range(len(labels))]

# Giriş alanlarını global değişkenlere atama
entry_isim, entry_ikili_kod, entry_uclu_kod, entry_ulke = entries

for i, (label_text, entry) in enumerate(zip(labels, entries)):
    label = tk.Label(page1, text=label_text)
    label.grid(row=1, column=i*2, padx=5, pady=5, sticky="w")
    entry.grid(row=1, column=i*2 + 1, padx=5, pady=5, sticky="e")

# Sorgula butonu
sorgula_button = tk.Button(page1, text="Sorgula", command=sorgula)
sorgula_button.grid(row=5, column=0, columnspan=8, pady=10)

# Tablo oluştur
columns = ["Şirket Kodu","Kalkış Havalimanı", "Kalkış Kodu", "Kalkış Şehri", "Varış Havalimanı", "Varış Kodu", "Varış Şehri"]
tree = ttk.Treeview(page1, columns=columns, show="headings")

# Başlık ekle
for col in columns:
    tree.heading(col, text=col)
    
# Tabloyu çerçevenin en aşağısına yerleştir
tree.grid(row=6, column=0, pady=10, columnspan=8, sticky='nsew')

for col in columns:
    tree.column(col, anchor="center", width=125)

page2_title = tk.Label(page2, text="Uçuş Bilgileri Girerek Havayolu Şirket Sorgulama", font=("Helvetica", 12), bg='white')
page2_title.grid(row=0, column=0, columnspan=8, pady=10)

# Sayfa 2 için gerekli bileşenleri ekleyin
labels2 = ["Kalkış", "Varış", "Kalkış Havalimanı kod", "Varış Havalimanı kod"]
entries2 = [tk.Entry(page2) for _ in range(len(labels2))]

# Giriş alanlarını global değişkenlere atama
entry_kalkis_havalimani, entry_varis_havalimani, entry_kalkis_havalimani_kod, entry_varis_havalimani_kod  = entries2

for i, (label_text, entry) in enumerate(zip(labels2, entries2)):
    label = tk.Label(page2, text=label_text)
    label.grid(row=1, column=i*2, padx=5, pady=5, sticky="w")
    entry.grid(row=1, column=i*2 + 1, padx=5, pady=5, sticky="e")
    
    
sorgula_button2 = tk.Button(page2, text="Sorgula", command=sorgula_page2)
sorgula_button2.grid(row=5, column=0, columnspan=8, pady=10)


# Tablo oluştur
columns2 = ["Havayolu Şirketi Ad", "Ülke", "İkili Kodu", "Üçlü Kodu","Kakış Havalimanı Kodu", "Varış Havalimanı Kodu"]
tree2 = ttk.Treeview(page2, columns=columns2, show="headings")

# Başlık ekle
for col in columns2:
    if col in ["Havayolu Şirketi Ad", "Ülke"]:
        tree2.heading(col, text=col, anchor="w")
    else:
        tree2.heading(col, text=col)
    
# Tabloyu çerçevenin en aşağısına yerleştir
tree2.grid(row=6, column=0, pady=10, columnspan=8, sticky='nsew')

# Sadece "Havayolu Şirketi Ad" ve "Ülke" sütunlarını sola dayalı yap
for col in columns2:
    if col in ["Havayolu Şirketi Ad", "Ülke"]:
        tree2.column(col, anchor="w", width=100)
    else:
        tree2.column(col, width=100)
# Başlık ekle
for col in columns2:
    if col in ["İkili Kodu", "Üçlü Kodu", "Kalkış Havalimanı Kodu", "Varış Havalimanı Kodu"]:
        tree2.heading(col, text=col, anchor="center")
    else:
        tree2.heading(col, text=col)
    
# Tabloyu çerçevenin en aşağısına yerleştir
tree2.grid(row=6, column=0, pady=10, columnspan=8, sticky='nsew')

# Sadece "Havayolu Şirketi Ad" ve "Ülke" sütunlarını sola dayalı yap
for col in columns2:
    if col in ["İkili Kodu", "Üçlü Kodu"]:
        tree2.column(col, anchor="center", width=100)
    else:
        tree2.column(col, width=100)

for i in range(8):
    root.columnconfigure(i, weight=1)
    root.rowconfigure(i, weight=1)

notebook.add(page1, text="Uçuş Sorgu")
notebook.add(page2, text="Havalimanı Sorgu")
notebook.add(create_page3(), text="Veri Ekle")

root.mainloop()
