import streamlit as st
from google import genai
from PIL import Image
import requests
from bs4 import BeautifulSoup
import time

# Sayfa Yapılandırması
st.set_page_config(
    page_title="AutoCheck AI Pro - Dijital Ekspertiz Garajı",
    page_icon="🚘",
    layout="wide"
)

# Özel CSS: Animasyonlar, Lazer Tarama, Neon Parlamalar ve Reklam Alanları
st.markdown("""
<style>
    /* Gradient Arka Plan ve Genel Fontlar */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Ana Başlık Animasyonu */
    .main-title {
        font-size: 2.6rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        animation: pulse 3s infinite alternate;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Reklam / Sponsor Pop-up Banner */
    .ad-banner {
        background: linear-gradient(90deg, #1e1b4b 0%, #312e81 100%);
        border: 1px solid #6366f1;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
        animation: fadeIn 1.5s ease-in-out;
    }
    .ad-badge {
        background-color: #ef4444;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Lazer Tarama Kutusu */
    .scanner-container {
        position: relative;
        overflow: hidden;
        border-radius: 12px;
        border: 2px solid #38bdf8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    }
    .scan-line {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: #38bdf8;
        box-shadow: 0 0 15px #38bdf8, 0 0 30px #38bdf8;
        animation: scan 2s infinite linear;
    }

    @keyframes scan {
        0% { top: 0%; }
        50% { top: 100%; }
        100% { top: 0%; }
    }
    
    /* Buton Tasarımı ve Hover Animasyonu */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #4f46e5 100%);
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 16px;
        border-radius: 14px;
        border: none;
        box-shadow: 0 0 15px rgba(37, 99, 235, 0.4);
        transition: all 0.4s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 0 25px rgba(79, 70, 229, 0.8);
    }

    /* Rapor Kapsayıcı Kart */
    .report-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 📢 ÜST SPONSOR & REKLAM BANNER'I (SİTE AÇILIŞINDA GÖRÜNÜR)
st.markdown("""
<div class="ad-banner">
    <span class="ad-badge">SPONSORLU FIRSAT</span> 🚘 <b>Türkiye'nin En Büyük Oto Ekspertiz Ağı İle Anlaşmalı!</b> 
    <br><span style="font-size:0.9rem; color:#cbd5e1;">AutoCheck AI kullanıcılarına özel ekspertiz paketlerinde <b>%20 İndirim Kodu: AUTO2026</b></span>
</div>
""", unsafe_allow_html=True)

# Başlıklar
st.markdown('<div class="main-title">🚘 AutoCheck AI PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Yapay Zekâ Destekli 360° Akıllı Oto Ekspertiz & Karşılaştırma Garajı</div>', unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key (Yönetici Girişi):", type="password")

# Yan Panel (Sidebar) Reklam Kutus
with st.sidebar:
    st.markdown("### 📢 REKLAM ALANI")
    st.info("🎯 **Aracınızı Satıyor Musunuz?**\nAnında en iyi teklifi almak için kurumsal oto alım ortaklarımızı ziyaret edin.")
    st.markdown("---")
    st.caption("AutoCheck AI Engine v3.0 | Powered by Gemini 3.6")

# Ana Sekmeler
main_tab1, main_tab2 = st.tabs(["🔍 Tek Araç Detaylı Analiz", "⚔️ İki Aracı Karşılaştır (Kıyaslama)"])

# ---------------------------------------------------------
# SEKME 1: TEK ARAÇ ANALİZİ
# ---------------------------------------------------------
with main_tab1:
    col_input1, col_input2 = st.columns([1, 1])
    
    with col_input1:
        link_single = st.text_input("🔗 İlan Linki Yapıştırın (Sahibinden, Letgo vb.):", key="link_s")
        text_single = st.text_area("✍️ İlan Metni / Ek Araç Notları:", height=130, key="text_s", placeholder="Örn: 2012 VW Crafter 2.0 TDI 220 bin km, motor durumu iyi...")

    with col_input2:
        up_single = st.file_uploader("📷 Araç / İlan Fotoğrafı Yükleyin:", type=["jpg", "jpeg", "png"], key="up_s")
        img_single = None
        if up_single:
            img_single = Image.open(up_single)
            st.markdown('<div class="scanner-container"><div class="scan-line"></div>', unsafe_allow_html=True)
            st.image(img_single, caption="📸 Yapay Zekâ Görsel Taraması Aktif", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 360° DETAYLI TARAMAYI BAŞLAT", key="btn_single"):
        if not api_key:
            st.error("API Key bulunamadı. Lütfen Cloud Secrets alanını kontrol edin.")
        elif not link_single and img_single is None and not text_single.strip():
            st.warning("Lütfen analiz için en az bir link, metin veya fotoğraf ekleyin.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Yüklenme Simülasyonu
            for percent_complete in range(0, 101, 25):
                time.sleep(0.15)
                progress_bar.progress(percent_complete)
                if percent_complete == 25: status_text.text("⚡ Görseller ve Metinler Ayrıştırılıyor...")
                elif percent_complete == 50: status_text.text("⚙️ Kronik Arıza Veritabanı Taranıyor...")
                elif percent_complete == 75: status_text.text("📊 Piyasa Değeri ve Ekspertiz Riskleri Hesaplanıyor...")
                elif percent_complete == 100: status_text.text("✅ Analiz Tamamlandı!")
                
            try:
                client = genai.Client(api_key=api_key)
                prompt = """
                Sen kıdemli bir otomotiv ekspertiz ustasısın. 
                Sana verilen araç verilerini derinlemesine incele.
                
                Lütfen şu formatta yanıt ver:
                # 📊 AUTOCHECK AI PRO EKSPERTİZ RAPORU
                * **Genel Araç Puanı:** 🌟 (10 üzerinden)
                
                ### ⚙️ 1. MEKANİK & KRONİK ARIZA TEŞHİSİ
                * (Motor, Turbo, Şanzıman ve Elektronik kronik riskleri)
                
                ### 🟢 2. ÖNE ÇIKAN AVANTAJLAR
                * (Yakıt, piyasa likiditesi, sürüş)
                
                ### 🔴 3. DEZAVANTAJLAR & İŞLETME MALİYETİ
                * (Bakım masrafları, kronik yıpranmalar)
                
                ### 🛠️ 4. EKSPERTİZDE BAKILACAK KRİTİK 3 NOKTA
                1. ...
                2. ...
                3. ...
                """
                contents = [prompt]
                if link_single: contents.append(f"İlan Linki: {link_single}")
                if img_single: contents.append(img_single)
                if text_single.strip(): contents.append(f"Araç Bilgisi:\n{text_single}")

                res = client.models.generate_content(model='gemini-3.6-flash', contents=contents)
                
                st.balloons()
                st.markdown('<div class="report-card">', unsafe_allow_html=True)
                st.markdown(res.text)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Rapor Altı Reklam Bandı
                st.markdown("""
                <br>
                <div class="ad-banner" style="background:#0f172a; border-color:#38bdf8;">
                    🎯 <b>Bu Aracı Satın Almadan Önce Ekspertiz Yaptıracak Mısınız?</b><br>
                    <span style="font-size:0.85rem; color:#94a3b8;">En yakın yetkili ekspertiz noktasından %20 indirimli randevu almak için tıklayın.</span>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Analiz sırasında bir hata oluştu: {e}")

# ---------------------------------------------------------
# SEKME 2: İKİ ARAÇ KARŞILAŞTIRMA
# ---------------------------------------------------------
with main_tab2:
    st.subheader("⚔️ İki Araç İlanını Yan Yana Kıyaslayın")
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown("### 🚘 1. ARAÇ (Araç A)")
        link_A = st.text_input("🔗 1. Araç İlan Linki:", key="link_A")
        text_A = st.text_area("✍️ 1. Araç Bilgileri:", height=100, key="text_A")
        up_A = st.file_uploader("📷 1. Araç Fotoğrafı:", type=["jpg", "jpeg", "png"], key="up_A")
        img_A = Image.open(up_A) if up_A else None
        if img_A: st.image(img_A, height=160)

    with colB:
        st.markdown("### 🚘 2. ARAÇ (Araç B)")
        link_B = st.text_input("🔗 2. Araç İlan Linki:", key="link_B")
        text_B = st.text_area("✍️ 2. Araç Bilgileri:", height=100, key="text_B")
        up_B = st.file_uploader("📷 2. Araç Fotoğrafı:", type=["jpg", "jpeg", "png"], key="up_B")
        img_B = Image.open(up_B) if up_B else None
        if img_B: st.image(img_B, height=160)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚔️ İKİ ARACI KARŞILAŞTIR VE KAZANANI SEÇ", key="btn_compare"):
        if not api_key:
            st.error("API Key bulunamadı.")
        elif (not link_A and not text_A.strip() and img_A is None) or (not link_B and not text_B.strip() and img_B is None):
            st.warning("Lütfen her iki araç için de veri girin.")
        else:
            with st.spinner("⚡ İki araç kıyaslanıyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt_compare = """
                    Sen otomotiv danışmanısın. ARAÇ A ve ARAÇ B verilerini detaylıca kıyasla.
                    İkisine de 10 üzerinden puan ver, kronik sorunları karşılaştır ve kazanan aracı gerekçeleriyle açıkla.
                    """
                    contents_comp = [prompt_compare, "--- ARAÇ A ---"]
                    if link_A: contents_comp.append(f"Link A: {link_A}")
                    if text_A: contents_comp.append(text_A)
                    if img_A: contents_comp.append(img_A)
                    
                    contents_comp.append("--- ARAÇ B ---")
                    if link_B: contents_comp.append(f"Link B: {link_B}")
                    if text_B: contents_comp.append(text_B)
                    if img_B: contents_comp.append(img_B)
                    
                    res_comp = client.models.generate_content(model='gemini-3.6-flash', contents=contents_comp)
                    st.balloons()
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.markdown(res_comp.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")