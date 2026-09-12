import streamlit as st
from google import genai
from PIL import Image
import time
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
if 'pazar_ilanlari' not in st.session_state:
    # Örnek Başlangıç İlanı
    st.session_state.pazar_ilanlari = [
        {
            "baslik": "2018 Renault Megane 1.5 dCi Touch",
            "fiyat": "850.000 TL",
            "km": "110.000",
            "sehir": "İstanbul / Kadıköy",
            "detay": "Hatasız boyasız, bakımları yetkili serviste yapılmıştır.",
            "img": None
        }
    ]

# ---------------------------------------------------------
# SİBER GARAJ CSS & GELİŞMİŞ GÖRSEL EFEKTLER
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #0f172a 0%, #020617 80%, #000000 100%);
        color: #f8fafc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .hero-title {
        font-size: 3rem;
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
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 25px;
    }
    .xp-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 2px solid #818cf8;
        border-radius: 14px;
        padding: 12px 20px;
        text-align: center;
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.3);
    }
    .market-card {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #38bdf8;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
    }
    .vote-box {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
        border: 2px solid #6366f1;
        border-radius: 18px;
        padding: 22px;
        text-align: center;
    }
    .report-box {
        background: rgba(15, 23, 42, 0.95);
        border: 2px solid #38bdf8;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.25);
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
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.4);
    }
    .stButton>button:disabled {
        background: #334155 !important;
        color: #94a3b8 !important;
        border: 1px solid #475569 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ÜST BAŞLIK VE GÜNLÜK ÖDÜL KONTROLÜ
# ---------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    st.markdown('<div class="hero-title">🏎️ AutoCheck AI PRO</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Yapay Zekâ Destekli Ekspertiz & İkinci El İlan Pazarı</div>', unsafe_allow_html=True)

with col_head2:
    st.markdown(f"""
    <div class="xp-card">
        <small style="color: #cbd5e1;">TOPLAM PUANIN</small><br>
        <span style="font-size: 1.5rem; font-weight: 900; color: #38bdf8;">🏆 {st.session_state.puan} XP</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    today = str(date.today())
    if st.session_state.son_odul_tarihi == today:
        st.button("✅ Bugünün Ödülü Alındı", disabled=True, key="btn_daily_done")
    else:
        if st.button("🎁 Günlük Ödül (+50 XP)", key="btn_daily"):
            st.session_state.puan += 50
            st.session_state.son_odul_tarihi = today
            st.toast("50 XP Hesabına Eklendi!", icon="🎉")
            st.rerun()

# API Key Kontrolü
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password")

# ---------------------------------------------------------
# YAN PANEL (SIDEBAR) GARAJ BİLGİSİ
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚘 SANAL GARAJIM")
    if not st.session_state.garaj:
        st.info("Garajın boş. Garajım sekmesinden aracını ekleyebilirsin.")
    else:
        for car in st.session_state.garaj:
            st.markdown(f"""
            <div style="background: #1e293b; border: 1px solid #38bdf8; border-radius: 10px; padding: 10px; margin-bottom: 8px;">
                <b>{car['marka']}</b><br>
                <small>📐 {car['km']} KM | 💰 {car['deger']}</small>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("AutoCheck Engine v5.0 Marketplace")

# ---------------------------------------------------------
# 7 ANA SEKMELİ YAPILANDIRMA
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🔍 TEK ARAÇ ANALİZİ", 
    "⚔️ İKİ ARAÇ KIYASLAMA", 
    "🛍️ SATILIK İLANLAR", 
    "📢 İLAN VER", 
    "🗳️ SOSYAL OYLAMA", 
    "🚗 SANAL GARAJ", 
    "💰 ARAÇ/MOTOR BUL"
])

# ---------------------------------------------------------
# SEKME 1: TEK ARAÇ ANALİZİ
# ---------------------------------------------------------
with tab1:
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        link_single = st.text_input("🔗 İlan Linki:", key="link_s")
        text_single = st.text_area("✍️ İlan Metni / Notlar:", height=130, key="text_s", placeholder="Örn: 2012 VW Crafter 2.0 TDI, 220.000 km, sol çamurluk boyalı...")
    with col_input2:
        up_single = st.file_uploader("📷 Araç Fotoğrafı Yükle:", type=["jpg", "jpeg", "png"], key="up_s")
        img_single = Image.open(up_single) if up_single else None
        if img_single: 
            st.image(img_single, caption="⚡ Visual Scan Aktif", use_container_width=True)

    if st.button("⚡ DETAYLI CYBER ANALİZ BAŞLAT", key="btn_s"):
        if not api_key:
            st.error("Gemini API Key bulunamadı.")
        elif not link_single and img_single is None and not text_single.strip():
            st.warning("Lütfen analiz için ilan linki, metin veya resim ekleyin.")
        else:
            with st.spinner("Analiz ediliyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = "Sen oto ekspertiz uzmanısın. Bilgileri incele; 10 üzerinden puan ver, mekanik/kronik riskleri ve bakılacak 3 kritik noktayı yaz."
                    contents = [prompt]
                    if link_single: contents.append(f"Link: {link_single}")
                    if text_single: contents.append(text_single)
                    if img_single: contents.append(img_single)

                    res = client.models.generate_content(model='gemini-3.6-flash', contents=contents)
                    st.balloons()
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.markdown(res.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")

# ---------------------------------------------------------
# SEKME 2: İKİ ARAÇ KIYASLAMA
# ---------------------------------------------------------
with tab2:
    colA, colB = st.columns(2)
    with colA:
        st.markdown("### 🚘 1. Araç (Araç A)")
        link_A = st.text_input("1. Araç Linki:", key="link_A")
        text_A = st.text_area("1. Araç Bilgileri:", height=100, key="text_A")
    with colB:
        st.markdown("### 🚘 2. Araç (Araç B)")
        link_B = st.text_input("2. Araç Linki:", key="link_B")
        text_B = st.text_area("2. Araç Bilgileri:", height=100, key="text_B")
    
    if st.button("⚔️ İKİ ARACI KIYASLA VE KAZANANI SEÇ", key="btn_c"):
        if api_key and (text_A or text_B or link_A or link_B):
            client = genai.Client(api_key=api_key)
            res_c = client.models.generate_content(model='gemini-3.6-flash', contents=[f"Şu iki aracı kıyasla ve kazananı seç:\nAraç A: {link_A} {text_A}\nAraç B: {link_B} {text_B}"])
            st.markdown('<div class="report-box">', unsafe_allow_html=True)
            st.markdown(res_c.text)
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# SEKME 3: SATILIK İLANLAR PAZARI
# ---------------------------------------------------------
with tab3:
    st.subheader("🛍️ Kullanıcılardan Satılık Araç & Motosiklet İlanları")
    
    if not st.session_state.pazar_ilanlari:
        st.info("Henüz pazarda ilan yok. İlk ilanı sen ver!")
    else:
        for idx, item in enumerate(st.session_state.pazar_ilanlari):
            with st.container():
                col_i1, col_i2 = st.columns([1, 2])
                with col_i1:
                    if item["img"]:
                        st.image(item["img"], use_container_width=True)
                    else:
                        st.markdown("📷 *Fotoğraf Yok*")
                with col_i2:
                    st.markdown(f"### {item['baslik']}")
                    st.markdown(f"💰 **Fiyat:** `{item['fiyat']}` | 📐 **KM:** `{item['km']}` | 📍 **Konum:** `{item['sehir']}`")
                    st.write(f"📝 **Açıklama:** {item['detay']}")
                    
                    if st.button(f"🔍 Yapay Zekâ İle Bu İlanı Analiz Et", key=f"btn_pazar_{idx}"):
                        st.session_state["text_s"] = f"{item['baslik']} - {item['fiyat']} - {item['km']} KM - {item['detay']}"
                        st.toast("İlan bilgileri 'Tek Araç Analizi' sekmesine aktarıldı! En üstteki 1. Sekmeye geçebilirsiniz.")

# ---------------------------------------------------------
# SEKME 4: İLAN VERME MODÜLÜ
# ---------------------------------------------------------
with tab4:
    st.subheader("📢 Aracını Ücretsiz İlana Koy")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        p_baslik = st.text_input("Araç Başlığı (Marka Model Yıl):", placeholder="Örn: 2015 BMW 320i ED 1.6", key="p_b")
        p_fiyat = st.text_input("Satış Fiyatı (TL):", placeholder="Örn: 920.000 TL", key="p_f")
        p_km = st.text_input("Kilometre:", placeholder="Örn: 145.000", key="p_k")
    with col_p2:
        p_sehir = st.text_input("Şehir / İlçe:", placeholder="Örn: Hatay / İskenderun", key="p_s")
        p_detay = st.text_area("İlan Açıklaması & Ekspertiz Durumu:", placeholder="Boya, değişen, tramer bilgisi vb.", height=100, key="p_d")
        p_img = st.file_uploader("Araç Fotoğrafı Yükle:", type=["jpg", "jpeg", "png"], key="p_img")

    if st.button("🚀 İLANI PAZARDA YAYINLA (+150 XP)", key="btn_add_ad"):
        if p_baslik and p_fiyat:
            uploaded_img = Image.open(p_img) if p_img else None
            yeni_ilan = {
                "baslik": p_baslik,
                "fiyat": p_fiyat,
                "km": p_km,
                "sehir": p_sehir,
                "detay": p_detay,
                "img": uploaded_img
            }
            st.session_state.pazar_ilanlari.append(yeni_ilan)
            st.session_state.puan += 150
            st.success("İlanınız başarıyla eklendi! 150 XP Kazandınız.")
            st.rerun()
        else:
            st.warning("Lütfen en az Başlık ve Fiyat kısımlarını doldurun.")

# ---------------------------------------------------------
# SEKME 5: SOSYAL OYLAMA MODÜLÜ
# ---------------------------------------------------------
with tab5:
    st.subheader("🔥 Günün İlanı: Bu Araç Alınır mı?")
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
            st.toast("Oyun kaydedildi! (+10 XP)")
    with col_v2:
        if st.button("🔴 UZAK DUR, RİSKLİ", key="v_no"):
            st.session_state.oylar["uzak_dur"] += 1
            st.session_state.puan += 10
            st.toast("Oyun kaydedildi! (+10 XP)")

    toplam = st.session_state.oylar["alinir"] + st.session_state.oylar["uzak_dur"]
    oran = int((st.session_state.oylar["alinir"] / toplam) * 100) if toplam > 0 else 50
    st.markdown(f"### 📊 Topluluk Kararı: **%{oran} ALINIR**")
    st.progress(oran / 100)

# ---------------------------------------------------------
# SEKME 6: SANAL GARAJ EKLEME
# ---------------------------------------------------------
with tab6:
    st.subheader("🚗 Kendi Aracını Garaja Ekle")
    g_marka = st.text_input("Marka ve Model:", key="g_m")
    g_km = st.number_input("Kilometre:", value=150000, step=5000, key="g_k")
    g_deger = st.text_input("Piyasa Değeri (TL):", key="g_d")
    
    if st.button("➕ Garajıma Ekle", key="btn_g"):
        if g_marka:
            st.session_state.garaj.append({"marka": g_marka, "km": g_km, "deger": g_deger})
            st.session_state.puan += 100
            st.success(f"{g_marka} garajına eklendi!")
            st.rerun()

# ---------------------------------------------------------
# SEKME 7: BÜTÇEYE UYGUN ARAÇ & MOTOSİKLET BULUCU
# ---------------------------------------------------------
with tab7:
    st.subheader("💰 Bütçenize En Uygun Araç/Motor Bulucu")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        butce = st.number_input("Bütçe (TL):", value=350000, step=10000, key="b_price")
        vasita_turu = st.selectbox("Vasıta Türü:", ["Otomobil", "Motosiklet", "Ticari / Van"], key="b_type")
    with col_b2:
        oncelik = st.selectbox("Öncelik:", ["Az Yaksın", "Kronik Arızasız", "İlk Araç", "Yedek Parça Ucuz"], key="b_prio")
        ekra_not = st.text_input("Not:", key="b_note")

    if st.button("🚀 UYGUN SEÇENEKLERİ LİSTELE", key="btn_budget"):
        if api_key:
            client = genai.Client(api_key=api_key)
            res_b = client.models.generate_content(model='gemini-3.6-flash', contents=[f"Bütçe: {butce} TL, Tür: {vasita_turu}, Öncelik: {oncelik}. 3 araç öner."])
            st.markdown('<div class="report-box">', unsafe_allow_html=True)
            st.markdown(res_b.text)
            st.markdown('</div>', unsafe_allow_html=True)