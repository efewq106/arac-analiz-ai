import streamlit as st
from google import genai
from PIL import Image
from datetime import date

# ---------------------------------------------------------
# SAYFA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="AutoCheck AI PRO - Garaj & İlan Pazarı",
    page_icon="🏎️",
    layout="wide"
)

# ---------------------------------------------------------
# OTURUM HAFIZASI (SESSION STATE)
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

if 'pazar_ilanlari' not in st.session_state:
    st.session_state.pazar_ilanlari = [
        {
            "baslik": "2018 Renault Megane 1.5 dCi",
            "fiyat": "850.000 TL",
            "km": "110.000 KM",
            "sehir": "İstanbul",
            "detay": "Hatasız boyasız, bakımları yetkili serviste yapılmıştır.",
            "img": None
        },
        {
            "baslik": "2021 Honda PCX 125 Scooter",
            "fiyat": "125.000 TL",
            "km": "12.500 KM",
            "sehir": "Hatay",
            "detay": "Düşmesi kalkması yok. Çanta ve konfor sele eklentili.",
            "img": None
        },
        {
            "baslik": "2015 BMW 320i ED 1.6",
            "fiyat": "980.000 TL",
            "km": "142.000 KM",
            "sehir": "Ankara",
            "detay": "M Sport paket, borusan çıkışlı, sanruf var.",
            "img": None
        },
        {
            "baslik": "2020 Yamaha MTI-07",
            "fiyat": "310.000 TL",
            "km": "18.000 KM",
            "sehir": "İzmir",
            "detay": "Akrapovic egzoz, çanta demiri mevcut.",
            "img": None
        }
    ]

# ---------------------------------------------------------
# NEON KAYAR VİTRİN & KART CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #0f172a 0%, #020617 80%, #000000 100%);
        color: #f8fafc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        text-align: center;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        filter: drop-shadow(0 0 15px rgba(56, 189, 248, 0.4));
    }
    .hero-subtitle {
        text-align: center;
        color: #cbd5e1;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 15px;
    }
    .xp-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 2px solid #818cf8;
        border-radius: 14px;
        padding: 10px 15px;
        text-align: center;
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.3);
    }
    
    /* KAYAR BANT (MARQUEE) TASARIMI */
    .marquee-container {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        background: rgba(15, 23, 42, 0.6);
        border-top: 1px solid #334155;
        border-bottom: 1px solid #334155;
        padding: 12px 0;
        margin-bottom: 25px;
        position: relative;
    }
    .marquee-content {
        display: inline-block;
        white-space: nowrap;
        animation: marquee 22s linear infinite;
    }
    .marquee-container:hover .marquee-content {
        animation-play-state: paused;
    }
    .mini-card {
        display: inline-block;
        background: #1e293b;
        border: 1px solid #38bdf8;
        border-radius: 12px;
        padding: 10px 16px;
        margin-right: 15px;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.15);
        vertical-align: middle;
    }
    .mini-title {
        color: #f8fafc;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .mini-price {
        color: #22c55e;
        font-weight: 800;
        font-size: 0.9rem;
        margin-left: 8px;
    }
    .mini-tag {
        color: #94a3b8;
        font-size: 0.8rem;
    }

    @keyframes marquee {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-50%); }
    }

    .ad-card {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .price-badge {
        background: linear-gradient(90deg, #16a34a 0%, #22c55e 100%);
        color: white;
        padding: 6px 14px;
        font-weight: 900;
        font-size: 1.1rem;
        border-radius: 8px;
        display: inline-block;
    }
    .report-box {
        background: rgba(15, 23, 42, 0.95);
        border: 2px solid #38bdf8;
        border-radius: 16px;
        padding: 25px;
        margin-top: 15px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #4f46e5 50%, #7c3aed 100%);
        color: white;
        font-weight: 800;
        border-radius: 12px;
        border: none;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ÜST BAŞLIK & PUAN PANOLARI
# ---------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    st.markdown('<div class="hero-title">🏎️ AutoCheck AI PRO</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Yapay Zekâ Destekli Canlı İlan Pazarı & Ekspertiz</div>', unsafe_allow_html=True)

with col_head2:
    st.markdown(f"""
    <div class="xp-card">
        <small style="color: #cbd5e1;">TOPLAM PUANIN</small><br>
        <span style="font-size: 1.4rem; font-weight: 900; color: #38bdf8;">🏆 {st.session_state.puan} XP</span>
    </div>
    """, unsafe_allow_html=True)
    
    today = str(date.today())
    if st.session_state.son_odul_tarihi == today:
        st.button("✅ Ödül Alındı", disabled=True, key="btn_daily_done")
    else:
        if st.button("🎁 Günlük Ödül (+50 XP)", key="btn_daily"):
            st.session_state.puan += 50
            st.session_state.son_odul_tarihi = today
            st.toast("50 XP Hesabına Eklendi!", icon="🎉")
            st.rerun()

# ---------------------------------------------------------
# CANLI KAYAR İLAN VİTRİNİ (MARQUEE)
# ---------------------------------------------------------
vitrin_html = '<div class="marquee-container"><div class="marquee-content">'
# İki kez döngüye sokarak kesintisiz sonsuz akış sağlıyoruz
for item in st.session_state.pazar_ilanlari * 3:
    vitrin_html += f"""
    <div class="mini-card">
        <span class="mini-title">🔥 {item['baslik']}</span>
        <span class="mini-price">{item['fiyat']}</span><br>
        <span class="mini-tag">📍 {item['sehir']} | 📐 {item['km']}</span>
    </div>
    """
vitrin_html += '</div></div>'

st.markdown(vitrin_html, unsafe_allow_html=True)

# API Key Kontrolü
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password")

# SIDEBAR GARAJ
with st.sidebar:
    st.markdown("### 🚘 SANAL GARAJIM")
    if not st.session_state.garaj:
        st.info("Garajın boş.")
    else:
        for car in st.session_state.garaj:
            st.markdown(f"<b>{car['marka']}</b><br><small>📐 {car['km']} KM | 💰 {car['deger']}</small>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SEKMELER
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🔍 TEK ARAÇ ANALİZİ", 
    "🛍️ SATILIK İLANLAR PAZARI", 
    "📢 İLAN VER", 
    "⚔️ İKİ ARAÇ KIYASLAMA", 
    "🗳️ SOSYAL OYLAMA", 
    "🚗 SANAL GARAJ", 
    "💰 ARAÇ/MOTOR BUL"
])

# SEKME 1: TEK ARAÇ ANALİZİ
with tab1:
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        link_single = st.text_input("🔗 İlan Linki:", key="link_s")
        text_single = st.text_area(
            "✍️ İlan Metni / Notlar:", 
            value=st.session_state.analiz_metni_aktar, 
            height=130, 
            key="text_s"
        )
    with col_input2:
        up_single = st.file_uploader("📷 Araç Fotoğrafı Yükle:", type=["jpg", "jpeg", "png"], key="up_s")
        img_single = Image.open(up_single) if up_single else None
        if img_single: 
            st.image(img_single, caption="⚡ Visual Scan Aktif", use_container_width=True)

    if st.button("⚡ DETAYLI CYBER ANALİZ BAŞLAT", key="btn_s"):
        if not api_key:
            st.error("Gemini API Key bulunamadı.")
        elif not link_single and img_single is None and not text_single.strip():
            st.warning("Lütfen veri girin.")
        else:
            with st.spinner("🔍 Analiz ediliyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    contents = ["Sen oto ekspertiz uzmanısın. İncele ve 10 üzerinden puan ver, mekanik riskleri ve 3 kritik noktayı yaz."]
                    if link_single: contents.append(f"Link: {link_single}")
                    if text_single: contents.append(text_single)
                    if img_single: contents.append(img_single)

                    res = client.models.generate_content(model='gemini-3.6-flash', contents=contents)
                    st.balloons()
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.markdown(res.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")

# SEKME 2: İLANLAR PAZARI
with tab2:
    st.subheader("🛍️ İkinci El Otomobil & Motosiklet Pazarı")
    for idx, item in enumerate(st.session_state.pazar_ilanlari):
        st.markdown('<div class="ad-card">', unsafe_allow_html=True)
        col_i1, col_i2, col_i3 = st.columns([1.2, 2.5, 1])
        
        with col_i1:
            if item["img"]:
                st.image(item["img"], use_container_width=True)
            else:
                st.markdown("<div style='background:#0f172a; height:100px; border-radius:8px; display:flex; align-items:center; justify-content:center;'>📷 Fotoğraf Yok</div>", unsafe_allow_html=True)
        
        with col_i2:
            st.markdown(f"#### {item['baslik']}")
            st.markdown(f"📐 {item['km']} | 📍 {item['sehir']}")
            st.caption(item['detay'])
        
        with col_i3:
            st.markdown(f'<div class="price-badge">{item["fiyat"]}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"🤖 AI İle Analiz Et", key=f"btn_pazar_{idx}"):
                st.session_state.analiz_metni_aktar = f"Araç: {item['baslik']} | Fiyat: {item['fiyat']} | KM: {item['km']} | Detay: {item['detay']}"
                st.toast("1. Sekmeye yüklendi!", icon="✅")
        st.markdown('</div>', unsafe_allow_html=True)

# SEKME 3: İLAN VERME
with tab3:
    st.subheader("📢 Aracını İlana Koy ve Hemen Sat")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        p_baslik = st.text_input("Araç Başlığı:", key="p_b")
        p_fiyat = st.text_input("Fiyat:", key="p_f")
        p_km = st.text_input("KM:", key="p_k")
    with col_p2:
        p_sehir = st.text_input("Şehir:", key="p_s")
        p_detay = st.text_area("Açıklama:", key="p_d")
        p_img = st.file_uploader("Fotoğraf:", type=["jpg", "png"], key="p_img")

    if st.button("🚀 İLANI YAYINLA (+150 XP)", key="btn_add_ad"):
        if p_baslik and p_fiyat:
            uploaded_img = Image.open(p_img) if p_img else None
            st.session_state.pazar_ilanlari.insert(0, {
                "baslik": p_baslik, "fiyat": p_fiyat, "km": p_km, "sehir": p_sehir, "detay": p_detay, "img": uploaded_img
            })
            st.session_state.puan += 150
            st.success("İlan eklendi ve üst kayar vitrine girdi!")
            st.rerun()

# SEKME 4: KIYASLAMA
with tab4:
    colA, colB = st.columns(2)
    with colA:
        text_A = st.text_area("1. Araç Bilgileri:", key="text_A")
    with colB:
        text_B = st.text_area("2. Araç Bilgileri:", key="text_B")
    
    if st.button("⚔️ KIYASLA", key="btn_c"):
        if api_key and (text_A or text_B):
            client = genai.Client(api_key=api_key)
            res_c = client.models.generate_content(model='gemini-3.6-flash', contents=[f"Araç A: {text_A}\nAraç B: {text_B}\nKıyasla ve kazananı seç."])
            st.markdown('<div class="report-box">', unsafe_allow_html=True)
            st.markdown(res_c.text)
            st.markdown('</div>', unsafe_allow_html=True)

# SEKME 5: SOSYAL OYLAMA
with tab5:
    st.subheader("🔥 Bu Araç Alınır mı?")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("🟢 ALINIR", key="v_yes"):
            st.session_state.oylar["alinir"] += 1
            st.toast("Oy verildi!")
    with col_v2:
        if st.button("🔴 UZAK DUR", key="v_no"):
            st.session_state.oylar["uzak_dur"] += 1
            st.toast("Oy verildi!")

# SEKME 6: SANAL GARAJ
with tab6:
    st.subheader("🚗 Garajıma Araç Ekle")
    g_marka = st.text_input("Marka / Model:", key="g_m")
    g_km = st.number_input("KM:", value=100000, key="g_k")
    g_deger = st.text_input("Piyasa Değeri:", key="g_d")
    if st.button("➕ Ekle", key="btn_g"):
        if g_marka:
            st.session_state.garaj.append({"marka": g_marka, "km": g_km, "deger": g_deger})
            st.success("Garaja eklendi!")
            st.rerun()

# SEKME 7: ARAÇ/MOTOR BUL
with tab7:
    st.subheader("💰 Bütçene Göre Araç / Motor Bul")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        butce = st.number_input("Bütçe (TL):", value=500000, key="b_price")
        vasita_turu = st.selectbox("Tür:", ["Otomobil", "Motosiklet"], key="b_type")
    with col_b2:
        oncelik = st.selectbox("Öncelik:", ["Performans", "Az Yaksın", "Kroniksiz"], key="b_prio")
        ekra_not = st.text_input("Özel Not (Örn: BMW olsun):", key="b_note")

    if st.button("🚀 UYGUN SEÇENEKLERİ LİSTELE", key="btn_budget"):
        if api_key:
            with st.spinner("🤖 5 Seçenek taranıyor..."):
                client = genai.Client(api_key=api_key)
                prompt = f"Bütçe: {butce} TL, Tür: {vasita_turu}, Not: {ekra_not}. Tam 5 araç öner."
                res_b = client.models.generate_content(model='gemini-3.6-flash', contents=[prompt])
                st.markdown('<div class="report-box">', unsafe_allow_html=True)
                st.markdown(res_b.text)
                st.markdown('</div>', unsafe_allow_html=True)