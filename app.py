import streamlit as st
from google import genai
from PIL import Image
import requests
from bs4 import BeautifulSoup
import re

# Sayfa Yapılandırması
st.set_page_config(
    page_title="AutoCheck AI Pro - Araç Analiz & Karşılaştırma",
    page_icon="🚘",
    layout="wide"
)

# Özel CSS Tasarımı
st.markdown("""
<style>
    .main-title { font-size: 2.3rem; font-weight: 900; color: #0F172A; text-align: center; }
    .sub-title { font-size: 1rem; color: #475569; text-align: center; margin-bottom: 20px; }
    .badge { background-color: #2563EB; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; }
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

st.markdown('<div class="main-title">🚘 AutoCheck AI <span class="badge">PRO</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Yapay Zekâ Destekli Tekli Araç Analizi & Çift Araç Karşılaştırma Platformu</div>', unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key (Yönetici Girişi):", type="password")

# Ana Sekmeler: Tek Araç Analizi vs. Çift Araç Karşılaştırma
main_tab1, main_tab2 = st.tabs(["🔍 Tek Araç Detaylı Analiz", "⚔️ İki Aracı Karşılaştır (Kıyaslama)"])

def linkten_veri_cek(url):
    gorseller = []
    baslik = ""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            if soup.title:
                baslik = soup.title.string
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                gorseller.append(og_image["content"])
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src and re.search(r'(jpeg|jpg|png|webp)', src, re.IGNORECASE):
                    if 'logo' not in src.lower() and 'icon' not in src.lower() and src not in gorseller:
                        gorseller.append(src)
                        if len(gorseller) >= 2:
                            break
    except Exception:
        pass
    return baslik, gorseller

# ---------------------------------------------------------
# SEKME 1: TEK ARAÇ ANALİZİ
# ---------------------------------------------------------
with main_tab1:
    tab_single_link, tab_single_img = st.tabs(["🔗 İlan Linki / Metin", "📷 Görsel Yükle"])
    
    gorseller_single = []
    with tab_single_link:
        link_single = st.text_input("🔗 İlan Linki Yapıştırın:")
        text_single = st.text_area("✍️ İlan Metni / Notlar:", height=100)
        if link_single:
            _, gorseller_single = linkten_veri_cek(link_single)
            if gorseller_single:
                st.write("📸 İlandan Yakalanan Görseller:")
                cols = st.columns(len(gorseller_single))
                for idx, img_url in enumerate(gorseller_single):
                    cols[idx].image(img_url, use_container_width=True)

    img_single = None
    with tab_single_img:
        up_single = st.file_uploader("📷 Araç Fotoğrafı / Ekran Görüntüsü Yükleyin", type=["jpg", "jpeg", "png"], key="single_up")
        if up_single:
            img_single = Image.open(up_single)
            st.image(img_single, caption="Yüklenen Görsel", use_container_width=True)

    if st.button("🚀 Aracı Detaylı Analiz Et", key="btn_single"):
        if not api_key:
            st.error("API Key bulunamadı.")
        elif not link_single and img_single is None and not text_single.strip():
            st.warning("Lütfen analiz için bir veri girin.")
        else:
            with st.spinner("Araç taranıyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = "Sen uzman bir mekanikersin. Araç için 10 üzerinden genel puan ver, kronik arızalarını, avantajlarını, dezavantajlarını ve ekspertizde bakılması gereken 3 kritik noktayı Türkçe raporla."
                    contents = [prompt]
                    if link_single: contents.append(f"İlan Linki: {link_single}")
                    if gorseller_single: contents.append(f"İlan Resimleri: {gorseller_single}")
                    if img_single: contents.append(img_single)
                    if text_single.strip(): contents.append(text_single)

                    res = client.models.generate_content(model='gemini-3.6-flash', contents=contents)
                    st.balloons()
                    st.success("Analiz Tamamlandı!")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Hata: {e}")

# ---------------------------------------------------------
# SEKME 2: İKİ ARAÇ KARŞILAŞTIRMA (KIYASLAMA)
# ---------------------------------------------------------
with main_tab2:
    st.subheader("⚔️ İki Araç İlanını Yan Yana Kıyaslayın")
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown("### 🚘 1. ARAÇ (Araç A)")
        link_A = st.text_input("🔗 1. Araç İlan Linki:", key="link_A")
        text_A = st.text_area("✍️ 1. Araç Bilgileri / Metni:", height=100, key="text_A", placeholder="Örn: 2012 VW Crafter 2.0 TDI 220 bin km...")
        up_A = st.file_uploader("📷 1. Araç Görseli:", type=["jpg", "jpeg", "png"], key="up_A")
        img_A = Image.open(up_A) if up_A else None
        if img_A: st.image(img_A, height=150)

    with colB:
        st.markdown("### 🚘 2. ARAÇ (Araç B)")
        link_B = st.text_input("🔗 2. Araç İlan Linki:", key="link_B")
        text_B = st.text_area("✍️ 2. Araç Bilgileri / Metni:", height=100, key="text_B", placeholder="Örn: 2014 Renault Master 2.3 dCi 250 bin km...")
        up_B = st.file_uploader("📷 2. Araç Görseli:", type=["jpg", "jpeg", "png"], key="up_B")
        img_B = Image.open(up_B) if up_B else None
        if img_B: st.image(img_B, height=150)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚔️ İKİ ARACI KARŞILAŞTIR VE KAZANANI SEÇ", key="btn_compare"):
        if not api_key:
            st.error("API Key bulunamadı.")
        elif (not link_A and not text_A.strip() and img_A is None) or (not link_B and not text_B.strip() and img_B is None):
            st.warning("Lütfen karşılaştırma yapabilmek için her iki araç için de bilgi/link/fotoğraf girin.")
        else:
            with st.spinner("⚡ İki aracın kronik arızaları, piyasa değerleri ve işletme maliyetleri kıyaslanıyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt_compare = """
                    Sen uzman bir otomotiv mekanikeri ve ikinci el araç danışmanısın.
                    Sana verilen ARAÇ A ve ARAÇ B bilgilerini detaylıca karşılaştır.
                    
                    Lütfen yanıtı şu şablonda Türkçe sun:
                    
                    # ⚔️ ARAÇ KARŞILAŞTIRMA VE KIYASLAMA RAPORU
                    
                    ### 📊 1. GENEL PUANLAMA & ÖZET
                    * **Araç A Puanı:** 🌟 (10 üzerinden)
                    * **Araç B Puanı:** 🌟 (10 üzerinden)
                    
                    ---
                    ### ⚙️ 2. KRONİK ARIZA VE MEKANİK KIYASLAMA
                    * **Araç A Kronik Riskleri:** ...
                    * **Araç B Kronik Riskleri:** ...
                    * **Mekanik Dayanıklılık Kazananı:** ...
                    
                    ---
                    ### 💰 3. PİYASA, YAKIT VE İŞLETME MALİYETİ
                    * **İkinci El Satış Hızı (Likidite):** ...
                    * **Yedek Parça ve Bakım Maliyetleri:** ...
                    
                    ---
                    ### 🏆 4. SONUÇ VE BÜYÜK KAZANAN
                    * 🥇 **Tavsiye Edilen Araç:** (Araç A mı yoksa Araç B mi?)
                    * 💡 **Neden Bu Araç Seçilmeli?:** (Net gerekçelerle açıkla)
                    """
                    
                    contents_comp = [prompt_compare, "--- ARAÇ A VERİLERİ ---"]
                    if link_A: contents_comp.append(f"Araç A Linki: {link_A}")
                    if text_A: contents_comp.append(f"Araç A Metni: {text_A}")
                    if img_A: contents_comp.append(img_A)
                    
                    contents_comp.append("--- ARAÇ B VERİLERİ ---")
                    if link_B: contents_comp.append(f"Araç B Linki: {link_B}")
                    if text_B: contents_comp.append(f"Araç B Metni: {text_B}")
                    if img_B: contents_comp.append(img_B)
                    
                    res_comp = client.models.generate_content(model='gemini-3.6-flash', contents=contents_comp)
                    st.balloons()
                    st.success("Karşılaştırma Raporu Hazır!")
                    st.markdown(res_comp.text)
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")