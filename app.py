import streamlit as st
from google import genai
from PIL import Image
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(
    page_title="AutoCheck AI Pro - Araç & İlan Analizi",
    page_icon="🚘",
    layout="centered"
)

# Özel CSS Tasarımı
st.markdown("""
<style>
    .main-title { font-size: 2.3rem; font-weight: 900; color: #0F172A; text-align: center; }
    .sub-title { font-size: 1rem; color: #475569; text-align: center; margin-bottom: 20px; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 14px;
        border-radius: 12px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚘 AutoCheck AI PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">İlan Görsel Yakalamalı & Akıllı Oto Ekspertiz Danışmanı</div>', unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key (Yönetici Girişi):", type="password")

tab1, tab2 = st.tabs(["🔗 İlan Linki & Fotoğraf Çekici", "📷 Ekran Görüntüsü / Resim Yükle"])

def linkten_gorsel_ve_veri_cek(url):
    """Linkten hem başlık hem de ilan fotoğraflarını yakalamaya çalışır"""
    gorseller = []
    baslik = ""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Başlık Al
            if soup.title:
                baslik = soup.title.string
                
            # OpenGraph Ana Resmi Yakala
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                gorseller.append(og_image["content"])
                
            # Ekstra İlan Görsellerini Ara
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src and re.search(r'(jpeg|jpg|png|webp)', src, re.IGNORECASE):
                    if 'logo' not in src.lower() and 'icon' not in src.lower() and src not in gorseller:
                        gorseller.append(src)
                        if len(gorseller) >= 3: # En fazla 3 resim al
                            break
    except Exception:
        pass
    return baslik, gorseller

gorsel_linkleri = []
with tab1:
    ilan_linki = st.text_input("🔗 İlan Linkini Yapıştırın (Sahibinden, Letgo, Arabam vb.):")
    ilan_metni = st.text_area("✍️ Ek Açıklama veya İlan Metni (İsteğe Bağlı):", height=80)
    
    if ilan_linki:
        with st.spinner("🖼️ İlandaki görseller ve veriler taranıyor..."):
            baslik, gorsel_linkleri = linkten_gorsel_ve_veri_cek(ilan_linki)
            if gorsel_linkleri:
                st.write("### 📸 İlandan Yakalanan Araç Görselleri:")
                cols = st.columns(len(gorsel_linkleri))
                for idx, img_url in enumerate(gorsel_linkleri):
                    cols[idx].image(img_url, caption=f"Görsel {idx+1}", use_container_width=True)
            else:
                st.caption("ℹ️ İlan sitesi bot koruması nedeniyle görseller otomatik çekilemedi. Fotoğraf sekmesinden ekran görüntüsü ekleyebilirsiniz.")

uploaded_image = None
with tab2:
    uploaded_file = st.file_uploader("📷 İlan Ekran Görüntüsü veya Araç Fotoğrafı Yükleyin", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption="📸 Yüklenen İlan / Araç Görseli", use_container_width=True)

SYSTEM_PROMPT = """
Sen usta bir otomotiv mekanikeri ve ikinci el araç ekspertiz uzmanısın.
Sana verilen görselleri, ilan linkini ve metinleri analiz et. 
Kullanıcıya 10 üzerinden genel değerlendirme puanı ver, kronik motor/şanzıman arızalarını, avantaj ve dezavantajları ile ekspertizde bakılması gereken 3 kritik noktayı detaylıca Türkçe raporla.
"""

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 ARACI DETAYLI ANALİZ ET"):
    if not api_key:
        st.error("Sistem API Key bulunamadı. Lütfen Secrets alanından GEMINI_API_KEY ekleyin.")
    elif not ilan_linki and uploaded_file is None and not ilan_metni.strip():
        st.warning("Lütfen analiz için bir link yapıştırın, resim yükleyin veya bilgi girin.")
    else:
        with st.spinner("🔍 Araç verileri ve görseller taranıyor..."):
            try:
                client = genai.Client(api_key=api_key)
                contents = [SYSTEM_PROMPT]
                
                if ilan_linki:
                    contents.append(f"İlan Linki: {ilan_linki}")
                    if gorsel_linkleri:
                        contents.append(f"İlandan Yakalanan Görsel Adresleri: {gorsel_linkleri}")
                
                if uploaded_image:
                    contents.append(uploaded_image)
                    
                if ilan_metni.strip():
                    contents.append(f"Kullanıcı Notu:\n{ilan_metni}")
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=contents
                )
                
                st.balloons()
                st.success("✅ Analiz Raporu Oluşturuldu!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Hata oluştu: {e}")