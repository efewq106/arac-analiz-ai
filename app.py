import streamlit as st
from google import genai
from PIL import Image
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Araç Analiz AI", page_icon="🚗", layout="centered")

st.title("🚗 Otomatik Araç & İlan Analiz Asistanı")
st.write("Sahibinden/Letgo ilan linkini yapıştırın, fotoğraf yükleyin veya araç bilgilerini yazın.")

# API Key'i arka planda gizli ayarlardan (Secrets) veya koddan alır
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Eğer Secrets ayarlanmadıysa test için geçici alan (Yayınlayınca gerek kalmaz)
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key (Yönetici Girişi):", type="password")

# Kullanıcı Girdileri
ilan_linki = st.text_input("🔗 İlan Linki Yapıştırın (Sahibinden, Letgo vb.):")
uploaded_file = st.file_uploader("📷 Veya İlan Ekran Görüntüsü Yükleyin", type=["jpg", "jpeg", "png"])
ilan_metni = st.text_area("✍️ Veya Araç Detaylarını Yazın / İlan Metnini Yapıştırın:", height=100)

def linkten_veri_cek(url):
    """Link verildiğinde sayfa başlığını ve içeriğini çekmeye çalışır"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Sayfa başlığı ve meta açıklamalarını al
            title = soup.title.string if soup.title else ""
            return f"İlan Sayfası Başlığı/İçeriği: {title}"
    except Exception:
        pass
    return f"Girilen İlan Linki: {url}"

SYSTEM_PROMPT = """
Sen uzman bir otomotiv mekanikeri ve ikinci el araç danışmanısın.
Sana verilen ilan linki, görsel veya araç bilgilerini analiz et:

1. ⚠️ **Kronik Sorunlar & Riskler:** Motor, şanzıman ve elektronik aksamda bilinen kronik arızalar.
2. 🟢 **Avantajlar:** Güçlü yönler (yakıt, piyasa canlılığı, parça bulunabilirliği).
3. 🔴 **Dezavantajlar:** İşletme maliyeti, konfor veya sürüş eksileri.
4. 🛠️ **Ekspertiz Tavsiyeleri:** Bu araçta özellikle bakılması gereken kritik noktalar.

Yanıtı anlaşılır, maddeler halinde ve Türkçe ver.
"""

if st.button("🚀 Aracı Analiz Et"):
    if not api_key:
        st.error("Sistem API Key bulunamadı. Lütfen yönetici panelinden ekleyin.")
    elif not ilan_linki and uploaded_file is None and not ilan_metni.strip():
        st.warning("Lütfen bir link yapıştırın, fotoğraf yükleyin veya metin yazın.")
    else:
        with st.spinner("İlan ve araç bilgileri analiz ediliyor..."):
            try:
                client = genai.Client(api_key=api_key)
                contents = [SYSTEM_PROMPT]
                
                # Link varsa içeriği çekip ekle
                if ilan_linki:
                    link_verisi = linkten_veri_cek(ilan_linki)
                    contents.append(link_verisi)
                
                # Fotoğraf varsa ekle
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    contents.append(image)
                    
                # Metin varsa ekle
                if ilan_metni.strip():
                    contents.append(f"Kullanıcı Notu: {ilan_metni}")
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=contents
                )
                
                st.success("Analiz Tamamlandı!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Hata oluştu: {e}")