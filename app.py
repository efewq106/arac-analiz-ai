import streamlit as st
from google import genai
from PIL import Image
import requests
from bs4 import BeautifulSoup

# Sayfa Yapılandırması
st.set_page_config(
    page_title="AutoCheck AI - Akıllı Araç & İlan Analizi",
    page_icon="🚘",
    layout="centered"
)

# Özel CSS Tasarımı (Görsel İyileştirmeler)
st.markdown("""
<style>
    /* Ana Başlık Tasarımı */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 25px;
    }
    /* Bilgi Kartı */
    .info-card {
        background-color: #F3F4F6;
        border-left: 5px solid #2563EB;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    /* Analiz Kutusu Stili */
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-size: 1.1rem;
        font-weight: bold;
        padding: 12px;
        border-radius: 10px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        border-none;
    }
</style>
""", unsafe_allow_html=True)

# Başlık Bölümü
st.markdown('<div class="main-header">🚘 AutoCheck AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Yapay Zekâ Destekli İkinci El Araç & Ekspertiz Danışmanı</div>', unsafe_allow_html=True)

# Bilgi Kartı
st.markdown("""
<div class="info-card">
    <b>💡 Nasıl Kullanılır?</b><br>
    İlan linkini yapıştırın, araç ekran görüntüsünü yükleyin veya araç bilgilerini yazın. Yapay zeka kronik sorunları, avantajları ve ekspertiz tavsiyelerini anında çıkarsın.
</div>
""", unsafe_allow_html=True)

# API Key Alımı (Secrets veya Sidebar)
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key (Yönetici Girişi):", type="password")

# Giriş Alanları (Tab Yapısı)
tab1, tab2 = st.tabs(["🔗 İlan Linki / Metin Girişi", "📷 Fotoğraf / Ekran Görüntüsü"])

with tab1:
    ilan_linki = st.text_input("🔗 İlan Linki Yapıştırın (Sahibinden, Letgo vb.):")
    ilan_metni = st.text_area("✍️ Veya Araç Detaylarını / İlan Metnini Yazın:", height=100, placeholder="Örn: 2012 Volkswagen Crafter 2.0 TDI 220.000 km...")

with tab2:
    uploaded_file = st.file_uploader("📷 Araç Fotoğrafı veya İlan Ekran Görüntüsü Yükleyin", type=["jpg", "jpeg", "png"])
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="🚘 Yüklenen Araç / İlan Görseli", use_container_width=True)

def linkten_veri_cek(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else ""
            return f"İlan Bağlantı İçeriği: {title}"
    except Exception:
        pass
    return f"Girilen İlan Linki: {url}"

SYSTEM_PROMPT = """
Sen uzman bir otomotiv mekanikeri, araç ekspertiz uzmanı ve ikinci el piyasa danışmanısın.
Sana verilen araç verilerini analiz et ve aşağıdaki yapıda, bol emojili, profesyonel bir rapor sun:

### 📊 Araç Analiz Raporu

#### 1. ⚠️ Kronik Arızalar & Mekanik Riskler
* (Motor, şanzıman, turbo, enjektör veya elektronik aksam riskleri)

#### 2. 🟢 Öne Çıkan Avantajlar
* (Yakıt tüketimi, piyasa likiditesi, yedek parça bulunabilirliği, konfor)

#### 3. 🔴 Dezavantajlar & İşletme Maliyeti
* (Sürüş hissi, kronik yıpranmalar, vergi veya bakım giderleri)

#### 4. 🛠️ Ekspertiz Kontrol Listesi
* (Ustaya veya ekspertize gidildiğinde özellikle bakılması gereken 3-4 kritik nokta)

Yanıtı anlaşılır, net ve Türkçe ver.
"""

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 Aracı Detaylı Analiz Et"):
    if not api_key:
        st.error("Sistem API Key bulunamadı. Lütfen yönetici panelinden Secrets ayarını kontrol edin.")
    elif not ilan_linki and uploaded_file is None and not ilan_metni.strip():
        st.warning("Lütfen analiz için bir link yapıştırın, fotoğraf yükleyin veya araç bilgisi girin.")
    else:
        with st.spinner("🔍 Araç geçmişi, kronik sorunlar ve piyasa verileri taranıyor..."):
            try:
                client = genai.Client(api_key=api_key)
                contents = [SYSTEM_PROMPT]
                
                if ilan_linki:
                    contents.append(linkten_veri_cek(ilan_linki))
                
                if uploaded_file is not None and image is not None:
                    contents.append(image)
                    
                if ilan_metni.strip():
                    contents.append(f"Kullanıcı Araç Notu:\n{ilan_metni}")
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=contents
                )
                
                st.success("✅ Analiz Başarıyla Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Analiz sırasında bir hata oluştu: {e}")