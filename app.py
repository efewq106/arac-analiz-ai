import streamlit as st
from google import genai
from PIL import Image
import requests
from bs4 import BeautifulSoup

# Sayfa Yapılandırması
st.set_page_config(
    page_title="AutoCheck AI Pro - Araç Ekspertiz & İlan Analiz",
    page_icon="🚗",
    layout="centered"
)

# Özel CSS Tasarımı (Profesyonel Garaj / Ekspertiz Teması)
st.markdown("""
<style>
    /* Ana Başlık */
    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        color: #0F172A;
        text-align: center;
        letter-spacing: -1px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #475569;
        text-align: center;
        margin-bottom: 20px;
    }
    /* Kart Yapıları */
    .feature-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .badge {
        background-color: #3B82F6;
        color: white;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    /* Buton Tasarımı */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 14px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 20px -3px rgba(37, 99, 235, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Üst Başlık & Banner
st.markdown('<div class="main-title">🚘 AutoCheck AI <span class="badge">PRO</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Yapay Zekâ Destekli 360° Oto Ekspertiz & İlan Analiz Platformu</div>', unsafe_allow_html=True)

# Hoş Geldin / Bilgi Kartı
st.markdown("""
<div class="feature-card">
    <h3 style="margin-top:0; color:#60A5FA;">🔍 Akıllı Teşhis Nasıl Çalışır?</h3>
    <p style="margin-bottom:5px;">İlan linkini yapıştırın veya araç/ilan fotoğrafını yükleyin. Sistemimiz aracı mekanik, kronik arıza, piyasa likiditesi ve ekspertiz riskleri açısından derinlemesine tarar.</p>
</div>
""", unsafe_allow_html=True)

# API Key Alımı (Secrets veya Sidebar)
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key (Yönetici Girişi):", type="password")

# Sekmeli Giriş Alanı
tab1, tab2 = st.tabs(["🔗 İlan Linki / Detaylı Metin", "📷 Araç Fotoğrafı / İlan Ekran Görüntüsü"])

with tab1:
    ilan_linki = st.text_input("🔗 İlan Linki Yapıştırın (Sahibinden, Letgo, Arabam vb.):")
    ilan_metni = st.text_area("✍️ Veya Araç Detaylarını / İlan Açıklamasını Yazın:", height=120, placeholder="Örn: 2012 Volkswagen Crafter 2.0 TDI 220.000 km, motor durumu %85, ekspertizde duman atma yok...")

with tab2:
    uploaded_file = st.file_uploader("📷 Araç Görseli veya İlan Ekran Görüntüsü Yükleyin", type=["jpg", "jpeg", "png"])
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="📸 Analiz Edilecek Araç / İlan Görseli", use_container_width=True)
        st.info("💡 Görsel algılandı: Motor, araç kasası, kadran veya ilan metni taranacak.")

def linkten_veri_cek(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else ""
            return f"İlan Bağlantı Verisi: {title}"
    except Exception:
        pass
    return f"Girilen İlan Linki: {url}"

SYSTEM_PROMPT = """
Sen usta bir otomotiv mekanikeri, kıdemli ekspertiz uzmanı ve ikinci el araç piyasa danışmanısın.
Sana verilen verileri (görsel, link, metin) en ince detayına kadar incele ve kullanıcıyı hayran bırakacak profesyonellikte bir rapor sun.

Lütfen yanıtını aynen şu şablonda ve zengin Markdown formatında hazırla:

---
## 📋 ARAÇ VE İLAN ÖZETİ
* **Tespit Edilen Model:** (Marka / Model / Motor / Yıl)
* **Genel Değerlendirme Puanı:** 🌟 (10 üzerinden puan ver)

---
## ⚙️ 1. MEKANİK & KRONİK ARIZA ANALİZİ
* **Motor & Turbo Riskleri:** (Enjektör, turbo, DPF, Duman atma, yağ yakma durumları)
* **Şanzıman & Aktarma:** (Manuel/Otomatik kronik arızalar, kavrama/mechatronic riskleri)
* **Elektronik & Süspansiyon:** (CAN-Bus, kronik sensör ve alt takım arızaları)

---
## 🟢 2. ÖNE ÇIKAN AVANTAJLAR (Neden Alınır?)
* **Piyasa & Likidite:** (İkinci el satılabilirlik hızı)
* **Maliyet:** (Yakıt tüketimi ve yedek parça erişim kolaylığı)

---
## 🔴 3. DEZAVANTAJLAR & İŞLETME GİDERLERİ
* (Sürüş konforu eksileri, yüksek km riskleri, ağır bakım maliyetleri)

---
## 🛠️ 4. EKSPERTİZDE ÖZELLİKLE BAKILMASI GEREKENLER (Kritik Noktalar)
1. 🔍 **Nokta 1:** (Örn: Soğutma suyu haznesinde yağ/kopuk var mı?)
2. 🔍 **Nokta 2:** (Örn: Şanzıman geçişlerinde vuruntu ve soğukta kararsızlık)
3. 🔍 **Nokta 3:** (Örn: Şase, podye ve direklerde düzeltme/kaynak izi)

---
💡 **Usta Tavsiyesi:** (Son karar cümlesi)
"""

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 360° DETAYLI ANALİZİ BAŞLAT"):
    if not api_key:
        st.error("Sistem API Key bulunamadı. Lütfen Streamlit Cloud Secrets ayarından GEMINI_API_KEY ekleyin.")
    elif not ilan_linki and uploaded_file is None and not ilan_metni.strip():
        st.warning("Lütfen analiz için bir link yapıştırın, fotoğraf yükleyin veya araç bilgisi yazın.")
    else:
        with st.spinner("⚡ Yapay Zekâ Araç Verilerini, Kronik Arıza Veritabanını ve Piyasa Koşullarını Tarıyor..."):
            try:
                client = genai.Client(api_key=api_key)
                contents = [SYSTEM_PROMPT]
                
                if ilan_linki:
                    contents.append(linkten_veri_cek(ilan_linki))
                
                if uploaded_file is not None and image is not None:
                    contents.append(image)
                    
                if ilan_metni.strip():
                    contents.append(f"Kullanıcı Araç Notu / Bilgisi:\n{ilan_metni}")
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=contents
                )
                
                st.balloons()
                st.success("✅ 360° Araç Ekspertiz Raporu Başarıyla Oluşturuldu!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Analiz sırasında bir hata oluştu: {e}")