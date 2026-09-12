import streamlit as st
from google import genai
from PIL import Image
from datetime import date
import random

# ---------------------------------------------------------
# SAYFA YAPILANDIRMASI & GOOGLE DOĞRULAMA ENJEKSİYONU
# ---------------------------------------------------------
st.set_page_config(
    page_title="AutoCheck Hub - AI Ekspertiz & İlan Pazarı",
    page_icon="🏎️",
    layout="wide"
)

# Google Search Console Meta Etiketini Kesin Olarak <head> Bölümüne Ekleyen Kod
st.markdown("""
    <head>
        <meta name="google-site-verification" content="kpgYSInnO1b5m2qVBtQKoH0uyLWfg7FJPX9-Gsxjk2Y" />
    </head>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# RASTGELE İNTERNET İLANLARI HAVUZU
# ---------------------------------------------------------
HAZIR_ILAN_HAVUZU = [
    {"baslik": "2016 BMW 320i ED 1.6 M Sport", "fiyat": "980.000 TL", "km": "142.000 KM", "sehir": "Ankara", "kaynak": "Sahibinden", "link": "https://www.sahibinden.com", "detay": "Borusan çıkışlı, sanruf, sol çamurluk boyalı."},
    {"baslik": "2020 Renault Megane 1.5 dCi Joy", "fiyat": "820.000 TL", "km": "98.000 KM", "sehir": "İstanbul", "kaynak": "Letgo", "link": "https://www.letgo.com", "detay": "Hatasız, boyasız, yetkili servis bakımlı."},
    {"baslik": "2021 Honda PCX 125 Scooter", "fiyat": "125.000 TL", "km": "12.500 KM", "sehir": "Hatay", "kaynak": "Sahibinden", "link": "https://www.sahibinden.com", "detay": "Düşmesi kalkması yok. Çanta ve sele eklentili."},
    {"baslik": "2019 Volkswagen Golf 1.6 TDI", "fiyat": "890.000 TL", "km": "115.000 KM", "sehir": "İzmir", "kaynak": "Arabam.com", "link": "https://www.arabam.com", "detay": "Cam tavanlı, değişensiz, temiz aile aracı."}
]

# ---------------------------------------------------------
# OTURUM HAFIZASI & KULLANICI VERİTABANI
# ---------------------------------------------------------
if 'pazar_ilanlari' not in st.session_state:
    st.session_state.pazar_ilanlari = HAZIR_ILAN_HAVUZU.copy()
if 'kullanicilar' not in st.session_state:
    st.session_state.kullanicilar = {"admin": "1234"}
if 'giris_yapan' not in st.session_state:
    st.session_state.giris_yapan = None
if 'puan' not in st.session_state:
    st.session_state.puan = 250
if 'analiz_metni_aktar' not in st.session_state:
    st.session_state.analiz_metni_aktar = ""
if 'analiz_link_aktar' not in st.session_state:
    st.session_state.analiz_link_aktar = ""

# ---------------------------------------------------------
# CSS STİLLERİ
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
    .mini-ad-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 15px;
        min-height: 180px;
    }
    .source-badge {
        background: #0ea5e9;
        color: white;
        padding: 3px 8px;
        font-size: 0.75rem;
        border-radius: 6px;
        font-weight: bold;
    }
    .price-text {
        color: #22c55e;
        font-weight: 800;
        font-size: 1.15rem;
    }
    .go-btn {
        display: inline-block;
        background: linear-gradient(90deg, #2563eb, #4f46e5);
        color: white !important;
        text-decoration: none;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: bold;
        text-align: center;
        margin-top: 8px;
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
# ÜST BAŞLIK & KENAR ÇUBUĞU (GİRİŞ/KAYIT ALANI)
# ---------------------------------------------------------
st.markdown('<div class="hero-title">🏎️ AutoCheck Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">İlanları İncele, Linkle Ekspertiz Yap, Alternatifleri Gör!</div>', unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password")

# --- KÜÇÜK YAN PANEL (SIDEBAR) GİRİŞ / KAYIT ALANI ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Kullanıcı Paneli")

if not st.session_state.giris_yapan:
    with st.sidebar.expander("🔑 Giriş Yap / Kayıt Ol", expanded=False):
        auth_secim = st.radio("İşlem Seçin:", ["Giriş Yap", "Kayıt Ol"], horizontal=True)
        
        if auth_secim == "Giriş Yap":
            l_user = st.text_input("Kullanıcı Adı:", key="sb_l_u")
            l_pass = st.text_input("Şifre:", type="password", key="sb_l_p")
            if st.button("Giriş Yap", key="sb_btn_login"):
                if l_user in st.session_state.kullanicilar and st.session_state.kullanicilar[l_user] == l_pass:
                    st.session_state.giris_yapan = l_user
                    st.success(f"Hoş geldin {l_user}!")
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre!")
        else:
            r_user = st.text_input("Yeni Kullanıcı Adı:", key="sb_r_u")
            r_pass = st.text_input("Yeni Şifre:", type="password", key="sb_r_p")
            if st.button("Kayıt Ol", key="sb_btn_reg"):
                if r_user and r_pass:
                    if r_user in st.session_state.kullanicilar:
                        st.warning("Bu kullanıcı adı alınmış.")
                    else:
                        st.session_state.kullanicilar[r_user] = r_pass
                        st.session_state.giris_yapan = r_user
                        st.success("Kayıt olundu ve giriş yapıldı!")
                        st.rerun()
                else:
                    st.warning("Alanları doldurun.")
else:
    st.sidebar.success(f"Aktif: **{st.session_state.giris_yapan}**")
    st.sidebar.markdown(f"🏆 Puanın: **{st.session_state.puan} XP**")
    if st.sidebar.button("🚪 Çıkış Yap"):
        st.session_state.giris_yapan = None
        st.rerun()

st.sidebar.markdown("---")

# ---------------------------------------------------------
# ANA SEKMELER
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🌐 İLANLAR & PİYASA", 
    "🔗 LİNK İLE EKSPERTİZ & ALTERNATİFLER", 
    "📢 İLAN EKLE", 
    "🤖 BÜTÇEYE GÖRE ARAÇ BUL"
])

with tab1:
    st.subheader("🔥 İnternetteki Güncel İlan Akışı")
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.caption("İstediğin ilanı inceleyebilir, orijinal sitesine gidebilir veya AI ekspertiz sekmesine aktarabilirsin.")
    with col_t2:
        if st.button("🎲 RASTGELE 4 İLAN GETİR", key="btn_rnd"):
            for item in random.sample(HAZIR_ILAN_HAVUZU, min(2, len(HAZIR_ILAN_HAVUZU))):
                st.session_state.pazar_ilanlari.insert(0, item)
            st.rerun()

    st.markdown("---")
    
    ILAN_PER_PAGE = 4
    toplam = len(st.session_state.pazar_ilanlari)
    top_sayfa = (toplam + ILAN_PER_PAGE - 1) // ILAN_PER_PAGE
    sayfa = st.number_input("Sayfa:", min_value=1, max_value=max(1, top_sayfa), value=1, step=1)
    
    start = (sayfa - 1) * ILAN_PER_PAGE
    current_list = st.session_state.pazar_ilanlari[start:start+ILAN_PER_PAGE]

    cols = st.columns(2)
    for idx, item in enumerate(current_list):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="mini-ad-box">
                <span class="source-badge">{item.get('kaynak', 'İlan')}</span>
                <span style="float:right;" class="price-text">{item['fiyat']}</span>
                <h4 style="margin: 10px 0 6px 0; font-size:1.05rem;">{item['baslik']}</h4>
                <p style="color:#94a3b8; font-size:0.85rem; margin-bottom:6px;">📍 {item['sehir']} | 📐 {item['km']}</p>
                <p style="color:#cbd5e1; font-size:0.8rem;">{item['detay']}</p>
                <a href="{item.get('link', '#')}" target="_blank" class="go-btn">🔗 Orijinal Siteye Git</a>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"⚡ AI İle Ekspertiz Yap", key=f"b_ai_{start+idx}"):
                st.session_state.analiz_link_aktar = item.get('link', '')
                st.session_state.analiz_metni_aktar = f"Araç: {item['baslik']} | Fiyat: {item['fiyat']} | KM: {item['km']} | Detay: {item['detay']}"
                st.toast("2. Sekmeye aktarıldı!", icon="🚀")

with tab2:
    st.subheader("🔗 Link ile Araç Ekspertizi & Akıllı Alternatifler")
    link_input = st.text_input("🔗 İlan Linki (URL):", value=st.session_state.analiz_link_aktar, placeholder="https://...")
    text_input = st.text_area("✍️ İlan Açıklaması / Notlar:", value=st.session_state.analiz_metni_aktar, height=100)
    
    if st.button("🚀 EKSPERTİZİ BAŞLAT VE ALTERNATİFLERİ GETİR", key="btn_deep_analysis"):
        if not api_key:
            st.error("API Key tanımlı değil.")
        elif not link_input and not text_input:
            st.warning("Lütfen bir link veya ilan açıklaması girin.")
        else:
            with st.spinner("🔍 Yapay zekâ inceliyor ve alternatifleri hazırlıyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    Oto ekspertiz ve pazar analiz uzmanı olarak şu ilanı incele:
                    - **Link:** {link_input}
                    - **Detaylar:** {text_input}

                    Şu başlıklar altında rapor sun:
                    1. **Ekspertiz Puanı & Durumu:** (10 üzerinden puan, riskler)
                    2. **Kronik Arızalar:** Motor/şanzıman problemleri.
                    3. **🎯 Akıllı Alternatifler:** Bu bütçede alınabilecek **tam 3 FARKLI alternatif araç/motor önerisi**.
                    """
                    res = client.models.generate_content(model='gemini-3.6-flash', contents=[prompt])
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.markdown(res.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")

with tab3:
    st.subheader("📢 Pazara İlan Ekle")
    if not st.session_state.giris_yapan:
        st.warning("⚠️ İlan yayınlayabilmek için sol menüden **Giriş Yapmanız** gerekmektedir.")
    else:
        b_in = st.text_input("Başlık:", placeholder="Örn: 2018 Egea", key="i_b")
        f_in = st.text_input("Fiyat:", placeholder="550.000 TL", key="i_f")
        l_in = st.text_input("Link:", placeholder="https://...", key="i_l")
        d_in = st.text_area("Açıklama:", key="i_d")
        
        if st.button("📌 İLANI YAYINLA (+150 XP)", key="i_btn"):
            if b_in and f_in:
                st.session_state.pazar_ilanlari.insert(0, {"baslik": b_in, "fiyat": f_in, "km": "100.000 KM", "sehir": "Türkiye", "kaynak": st.session_state.giris_yapan, "link": l_in or "#", "detay": d_in})
                st.session_state.puan += 150
                st.success("İlan eklendi!")
                st.rerun()

with tab4:
    st.subheader("💰 Bütçene Göre Araç / Motor Bulucu")
    butce = st.number_input("Bütçe (TL):", value=600000, step=25000)
    notlar = st.text_input("Özel İstek:")
    if st.button("🔍 LİSTELE", key="b_list"):
        if api_key:
            with st.spinner("Aranıyor..."):
                client = genai.Client(api_key=api_key)
                res = client.models.generate_content(model='gemini-3.6-flash', contents=[f"Bütçe: {butce} TL, İstek: {notlar}. Tam 5 alternatif araç/motor öner."])
                st.markdown('<div class="report-box">', unsafe_allow_html=True)
                st.markdown(res.text)
                st.markdown('</div>', unsafe_allow_html=True)