import streamlit as st
from google import genai
from PIL import Image
import time

# Sayfa Yapılandırması
st.set_page_config(
    page_title="AutoCheck AI PRO - Garaj & Sosyal Oylama",
    page_icon="🏎️",
    layout="wide"
)

# Oturum Hafızası (Session State) Tanımlamaları
if 'garaj' not in st.session_state:
    st.session_state.garaj = []
if 'oylar' not in st.session_state:
    st.session_state.oylar = {"alinir": 42, "uzak_dur": 12}
if 'puan' not in st.session_state:
    st.session_state.puan = 250

# CSS Tasarımları ve Neon Teması
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #1e293b 0%, #0f172a 60%, #020617 100%);
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
    .garaj-card {
        background: #1e293b;
        border: 1px solid #38bdf8;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }
    .vote-box {
        background: #0f172a;
        border: 2px solid #6366f1;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #2563eb 0%, #4f46e5 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# ANA BAŞLIK & PROFİL BİLGİSİ
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown('<div class="hero-title">🏎️ AutoCheck AI PRO</div>', unsafe_allow_html=True)
with col_head2:
    st.markdown(f"🏆 **Garaj Puanın:** `{st.session_state.puan} XP`")
    if st.button("🎁 Günlük Giriş Ödülü (+50 XP)"):
        st.session_state.puan += 50
        st.toast("50 XP Kazandın!", icon="🎉")

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password")

# YAN PANEL (SIDEBAR) GARAJ ÖZETİ
with st.sidebar:
    st.markdown("### 🚘 SANAL GARAJIM")
    if not st.session_state.garaj:
        st.caption("Henüz garajına araç eklemedin.")
    else:
        for idx, car in enumerate(st.session_state.garaj):
            st.markdown(f"""
            <div class="garaj-card">
                <b>{car['marka']}</b><br>
                <small>💰 Değer: {car['deger']}</small>
            </div>
            """, unsafe_allow_html=True)

# DÖRT ANA SEKMELİ YAPILANDIRMA
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 TEK ARAÇ ANALİZİ", 
    "⚔️ İKİ ARAÇ KIYASLAMA", 
    "🗳️ BU ARAÇ ALINIR MI? (ANKET)", 
    "🚗 SANAL GARAJ EKLE"
])

# ---------------------------------------------------------
# SEKME 1: TEK ARAÇ ANALİZİ
# ---------------------------------------------------------
with tab1:
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        link_single = st.text_input("🔗 İlan Linki:", key="link_s")
        text_single = st.text_area("✍️ İlan Metni / Notlar:", height=120, key="text_s")
    with col_input2:
        up_single = st.file_uploader("📷 Görsel Yükle:", type=["jpg", "jpeg", "png"], key="up_s")
        img_single = Image.open(up_single) if up_single else None
        if img_single: st.image(img_single, height=150)

    if st.button("⚡ DETAYLI ANALİZ ET", key="btn_s"):
        if not api_key:
            st.error("API Key eksik.")
        else:
            with st.spinner("Yapay zekâ turluyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = "Sen otomotiv uzmanısın. Aracı incele; 10 üzerinden puan ver, mekanik ve kronik riskleri sırala."
                    contents = [prompt]
                    if link_single: contents.append(link_single)
                    if text_single: contents.append(text_single)
                    if img_single: contents.append(img_single)
                    
                    res = client.models.generate_content(model='gemini-3.6-flash', contents=contents)
                    st.balloons()
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Hata: {e}")

# ---------------------------------------------------------
# SEKME 2: İKİ ARAÇ KIYASLAMA
# ---------------------------------------------------------
with tab2:
    colA, colB = st.columns(2)
    with colA:
        st.markdown("### 🚘 Araç A")
        text_A = st.text_area("Araç A Detayları:", key="t_a")
    with colB:
        st.markdown("### 🚘 Araç B")
        text_B = st.text_area("Araç B Detayları:", key="t_b")
    
    if st.button("⚔️ KIYASLA", key="btn_c"):
        if api_key and (text_A or text_B):
            client = genai.Client(api_key=api_key)
            res = client.models.generate_content(model='gemini-3.6-flash', contents=[f"Şu iki aracı kıyasla ve kazananı seç:\nAraç A: {text_A}\nAraç B: {text_B}"])
            st.markdown(res.text)

# ---------------------------------------------------------
# SEKME 3: SOSYAL OYLAMA MODÜLÜ (BAĞIMLILIK YAPICI)
# ---------------------------------------------------------
with tab3:
    st.subheader("🔥 Günün Topluluk İlanı: Bu Araç Alınır mı?")
    
    st.markdown("""
    <div class="vote-box">
        <h3>🚘 2012 Volkswagen Crafter 2.0 TDI (220.000 km)</h3>
        <p><i>"Motor sıfır yapıldı deniyor, sol çamurluk lokal boyalı. Fiyat piyasanın %10 altında."</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("🟢 MANTIKLI, ALINIR", key="v_yes"):
            st.session_state.oylar["alinir"] += 1
            st.session_state.puan += 10
            st.toast("Oyun kaydedildi! +10 XP")
    with col_v2:
        if st.button("🔴 UZAK DUR, RİSKLİ", key="v_no"):
            st.session_state.oylar["uzak_dur"] += 1
            st.session_state.puan += 10
            st.toast("Oyun kaydedildi! +10 XP")

    # Canlı Anket Sonucu Çubuğu
    toplam = st.session_state.oylar["alinir"] + st.session_state.oylar["uzak_dur"]
    oran = int((st.session_state.oylar["alinir"] / toplam) * 100) if toplam > 0 else 50
    
    st.markdown(f"### 📊 Topluluk Kararı: **%{oran} ALINIR**")
    st.progress(oran / 100)
    st.caption(f"Toplam {toplam} kişi oy kullandı.")

# ---------------------------------------------------------
# SEKME 4: SANAL GARAJ EKLEME
# ---------------------------------------------------------
with tab4:
    st.subheader("🚘 Kendi Aracını Garaja Ekle (Değerini İzle)")
    g_marka = st.text_input("Marka ve Model:", placeholder="Örn: 2011 Opel Astra J 1.6")
    g_km = st.number_input("Kilometre:", value=150000, step=5000)
    g_deger = st.text_input("Tahmini Piyasa Değeri (TL):", placeholder="Örn: 650.000 TL")
    
    if st.button("➕ Garajıma Ekle", key="btn_g"):
        if g_marka:
            st.session_state.garaj.append({"marka": g_marka, "km": g_km, "deger": g_deger})
            st.session_state.puan += 100
            st.success(f"{g_marka} garajına eklendi! (+100 XP Kazandın)")
            st.rerun()