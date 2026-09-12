import streamlit as st
from google import genai
from PIL import Image
from datetime import date

# ---------------------------------------------------------
# SAYFA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="AutoCheck AI PRO - Tüm İlanlar Tek Yerde",
    page_icon="🏎️",
    layout="wide"
)

# ---------------------------------------------------------
# OTURUM HAFIZASI & İLAN VERİTABANI (LINK YÖNLENDİRMELİ)
# ---------------------------------------------------------
if 'garaj' not in st.session_state:
    st.session_state.garaj = []
if 'oylar' not in st.session_state:
    st.session_state.oylar = {"alinir": 42, "uzak_dur": 12}
if 'puan' not in st.session_state:
    st.session_state.puan = 250
if 'son_odul_tarihi' not in st.session_state:
    st.session_state.son_odul_tarihi = None
if 'analiz_metni_aktar' not in st.session_state:
    st.session_state.analiz_metni_aktar = ""

# Dış sitelerden çekilen / eklenen ilanlar (Orijinal linkleriyle)
if 'pazar_ilanlari' not in st.session_state:
    st.session_state.pazar_ilanlari = [
        {
            "baslik": "2018 Renault Megane 1.5 dCi Touch",
            "fiyat": "850.000 TL",
            "km": "110.000 KM",
            "sehir": "İstanbul",
            "kaynak": "Sahibinden",
            "link": "https://www.sahibinden.com",
            "detay": "Hatasız boyasız, bakımları yetkili serviste yapılmıştır."
        },
        {
            "baslik": "2021 Honda PCX 125 Scooter",
            "fiyat": "125.000 TL",
            "km": "12.500 KM",
            "sehir": "Hatay",
            "kaynak": "Letgo",
            "link": "https://www.letgo.com",
            "detay": "Düşmesi kalkması yok. Çanta ve konfor sele eklentili."
        },
        {
            "baslik": "2015 BMW 320i ED M Sport 1.6",
            "fiyat": "980.000 TL",
            "km": "142.000 KM",
            "sehir": "Ankara",
            "kaynak": "Arabam.com",
            "link": "https://www.arabam.com",
            "detay": "M Sport paket, borusan çıkışlı, sanruf var."
        },
        {
            "baslik": "2020 Yamaha MT-07 ABS",
            "fiyat": "310.000 TL",
            "km": "18.000 KM",
            "sehir": "İzmir",
            "kaynak": "Sahibinden",
            "link": "https://www.sahibinden.com",
            "detay": "Akrapovic egzoz, çanta demiri mevcut."
        }
    ]

# ---------------------------------------------------------
# MİNİ İLAN KARTLARI VE NEON CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #0f172a 0%, #020617 80%, #000000 100%);
        color: #f8fafc;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        text-align: center;
        color: #cbd5e1;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    
    /* MİNİ İLAN KARTI STİLİ */
    .mini-ad-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
        transition: all 0.2s ease-in-out;
    }
    .mini-ad-box:hover {
        border-color: #38bdf8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }
    .source-tag {
        background: #0ea5e9;
        color: white;
        padding: 2px 8px;
        font-size: 0.75rem;
        border-radius: 4px;
        font-weight: bold;
    }
    .price-text {
        color: #22c55e;
        font-weight: 800;
        font-size: 1.1rem;
    }
    .go-btn {
        display: inline-block;
        background: #2563eb;
        color: white !important;
        text-decoration: none;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: bold;
        text-align: center;
        margin-top: 5px;
    }
    .go-btn:hover {
        background: #1d4ed8;
    }
    .report-box {
        background: rgba(15, 23, 42, 0.95);
        border: 2px solid #38bdf8;
        border-radius: 16px;
        padding: 20px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ÜST BAŞLIK
# ---------------------------------------------------------
st.markdown('<div class="hero-title">🏎️ AutoCheck Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Sahibinden, Letgo ve Arabam.com İlanları Tek Tıkla Önünde!</div>', unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password")

# ---------------------------------------------------------
# ANA AKIŞ: KÜÇÜK İLAN LİSTESİ VE AI ANALİZİ
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🌐 TÜM İLANLAR (TEK TIK MENTÖRÜ)", "➕ HIZLI İLAN/LINK EKLE", "🤖 AI ARAÇ BULUCU"])

with tab1:
    st.subheader("🔥 Canlı İlan Akışı")
    st.caption("İstediğin ilanın orijinal sayfasına gitmek için 'SİTEYE GİT' butonuna basabilirsin.")
    
    # İlanları 2'li kolonlar halinde küçük kartlar olarak basıyoruz
    cols = st.columns(2)
    for idx, item in enumerate(st.session_state.pazar_ilanlari):
        col_target = cols[idx % 2]
        with col_target:
            st.markdown(f"""
            <div class="mini-ad-box">
                <span class="source-tag">{item['kaynak']}</span>
                <span style="float:right;" class="price-text">{item['fiyat']}</span>
                <h4 style="margin: 8px 0 4px 0; font-size:1.05rem;">{item['baslik']}</h4>
                <p style="color:#94a3b8; font-size:0.85rem; margin-bottom:8px;">📍 {item['sehir']} | 📐 {item['km']}</p>
                <p style="color:#cbd5e1; font-size:0.8rem;">{item['detay']}</p>
                <a href="{item['link']}" target="_blank" class="go-btn">🔗 İlana Git ({item['kaynak']})</a>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"⚡ AI İle Orijinal İlanı İncele", key=f"btn_quick_{idx}"):
                st.session_state.analiz_metni_aktar = f"Araç: {item['baslik']} | Fiyat: {item['fiyat']} | KM: {item['km']} | Detay: {item['detay']} | Link: {item['link']}"
                st.toast("İlan AI Analiz hafızasına alındı!", icon="🧠")

    if st.session_state.analiz_metni_aktar:
        st.markdown("---")
        st.markdown("### 🧠 Seçilen İlanın Yapay Zeka Ekspertiz Raporu")
        st.info(st.session_state.analiz_metni_aktar)
        if st.button("🚀 SEÇİLİ İLANI HIZLICA ANALİZ ET", key="btn_run_ai"):
            if api_key:
                with st.spinner("AI İlanı inceliyor..."):
                    client = genai.Client(api_key=api_key)
                    res = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=[f"Şu ilanı incele, 10 üzerinden puan ver ve alırken bakılacak 3 kronik arızayı söyle:\n{st.session_state.analiz_metni_aktar}"]
                    )
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.markdown(res.text)
                    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("🔗 İnternetten İlan Ekle")
    st.caption("Sahibinden veya Letgo'da gördüğün bir ilanın linkini yapıştır, siteye kartsı eklensin!")
    
    col_a, col_b = st.columns(2)
    with col_a:
        in_baslik = st.text_input("İlan Başlığı:", placeholder="Örn: 2017 Polo 1.2 TSI")
        in_fiyat = st.text_input("Fiyat:", placeholder="Örn: 650.000 TL")
        in_km = st.text_input("KM / Şehir:", placeholder="Örn: 95.000 KM / İzmir")
    with col_b:
        in_site = st.selectbox("Hangi Siteden?", ["Sahibinden", "Letgo", "Arabam.com", "Diğer"])
        in_link = st.text_input("İlan Linki (URL):", placeholder="https://...")
        in_detay = st.text_area("İlan Notu / Ekspertiz:", placeholder="Sol kapı boyalı...")

    if st.button("📌 İLANI HUB'A EKLE"):
        if in_baslik and in_link:
            st.session_state.pazar_ilanlari.insert(0, {
                "baslik": in_baslik,
                "fiyat": in_fiyat,
                "km": in_km,
                "sehir": "Türkiye",
                "kaynak": in_site,
                "link": in_link,
                "detay": in_detay
            })
            st.success("İlan başarıyla eklendi! Tek tıkla orijinal siteye gidilebilir.")
            st.rerun()

with tab3:
    st.subheader("💰 Bütçene Göre Araç Bul")
    b_price = st.number_input("Bütçen (TL):", value=500000, step=25000)
    b_note = st.text_input("Özel İstek (Örn: BMW olsun, Scooter olsun):")
    if st.button("🔍 SEÇENEKLERİ LİSTELE"):
        if api_key:
            with st.spinner("AI Arıyor..."):
                client = genai.Client(api_key=api_key)
                res = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[f"Bütçe: {b_price} TL. İstek: {b_note}. Tam 5 araç/motosiklet önerisi yap."]
                )
                st.markdown('<div class="report-box">', unsafe_allow_html=True)
                st.markdown(res.text)
                st.markdown('</div>', unsafe_allow_html=True)