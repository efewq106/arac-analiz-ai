import streamlit as st
from google import genai
from PIL import Image
import time

# ---------------------------------------------------------
# SAYFA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="AutoCheck AI PRO - Garaj, Ekspertiz & Bulucu",
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

# ---------------------------------------------------------
# ÖZEL CSS: CYBER GARAJ TEMASI & NEON STİLLER
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #1e293b 0%, #0f172a 60%, #020617 100%);
        color: #f8fafc;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    .garaj-card {
        background: #1e293b;
        border: 1px solid #38bdf8;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }
    .vote-box {
        background: #0f172a;
        border: 2px solid #6366f1;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    }
    .report-box {
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid #38bdf8;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.2);
        margin-top: 15px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #4f46e5 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 12px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(79, 70, 229, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ÜST BAŞLIK VE SKOR ALANI
# ---------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown('<div class="hero-title">🏎️ AutoCheck AI PRO</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Cyber-Ekspertiz, İkinci El Araç & Motosiklet Analiz Portalı</div>', unsafe_allow_html=True)
with col_head2:
    st.markdown(f"🏆 **Garaj Puanın:** `{st.session_state.puan} XP`")
    if st.button("🎁 Günlük Ödül (+50 XP)", key="btn_daily"):
        st.session_state.puan += 50
        st.toast("50 XP Hesabına Eklendi!", icon="🎉")

# API Key Kontrolü
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password")

# YAN PANEL (SIDEBAR) GARAJ ÖZETİ
with st.sidebar:
    st.markdown("### 🚘 SANAL GARAJIM")
    if not st.session_state.garaj:
        st.caption("Henüz garajına araç eklemedin.")
    else:
        for car in st.session_state.garaj:
            st.markdown(f"""
            <div class="garaj-card">
                <b>{car['marka']}</b><br>
                <small>📐 {car['km']} KM | 💰 {car['deger']}</small>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("AutoCheck Engine v4.0 Pro")

# ---------------------------------------------------------
# 5 ANA SEKMELİ YAPILANDIRMA (HATA ÇÖZÜMÜ BURADA)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 TEK ARAÇ ANALİZİ", 
    "⚔️ İKİ ARAÇ KIYASLAMA", 
    "🗳️ SOSYAL OYLAMA", 
    "🚗 SANAL GARAJ", 
    "💰 ARAÇ & MOTOR BUL"
])

# ---------------------------------------------------------
# SEKME 1: TEK ARAÇ ANALİZİ
# ---------------------------------------------------------
with tab1:
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        link_single = st.text_input("🔗 İlan Linki:", key="link_s")
        text_single = st.text_area("✍️ İlan Metni / Araç Notları:", height=130, key="text_s", placeholder="Örn: 2012 VW Crafter 2.0 TDI, 220.000 km, sol çamurluk boyalı...")
    with col_input2:
        up_single = st.file_uploader("📷 Araç Fotoğrafı / İlan Ekran Görüntüsü:", type=["jpg", "jpeg", "png"], key="up_s")
        img_single = Image.open(up_single) if up_single else None
        if img_single: 
            st.image(img_single, caption="⚡ Tarama İçin Yüklendi", use_container_width=True)

    if st.button("⚡ DETAYLI ANALİZ ET", key="btn_s"):
        if not api_key:
            st.error("Gemini API Key bulunamadı.")
        elif not link_single and img_single is None and not text_single.strip():
            st.warning("Lütfen analiz için link, metin veya resim ekleyin.")
        else:
            with st.spinner("Yapay zekâ turluyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = """
                    Sen usta bir oto ekspertiz mekanikerisin. Bilgileri detaylı incele.
                    Yanıtını Markdown formatında, bol emojili ve şu başlıklarla ver:
                    # 📊 CYBER EKSPERTİZ RAPORU
                    * **Genel Araç Puanı:** 🌟 (10 üzerinden)
                    ### ⚙️ 1. MEKANİK & KRONİK RİSK TEŞHİSİ
                    ### 🟢 2. ÖNE ÇIKAN AVANTAJLAR
                    ### 🔴 3. DEZAVANTAJLAR & MASRAFLAR
                    ### 🛠️ 4. EKSPERTİZDE BAKILACAK KRİTİK 3 NOKTA
                    """
                    contents = [prompt]
                    if link_single: contents.append(f"İlan Linki: {link_single}")
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
    st.subheader("⚔️ İki Araç İlanını Yan Yana Kıyaslayın")
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
        if not api_key:
            st.error("API Key eksik.")
        elif not text_A and not text_B and not link_A and not link_B:
            st.warning("Lütfen iki araç için de bilgi girin.")
        else:
            with st.spinner("Karşılaştırılıyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt_c = f"Şu iki aracı kıyasla, 10 üzerinden puanla ve hangisinin alınması gerektiğini gerekçeleriyle anlat:\nAraç A: {link_A} {text_A}\nAraç B: {link_B} {text_B}"
                    res_c = client.models.generate_content(model='gemini-3.6-flash', contents=[prompt_c])
                    st.balloons()
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.markdown(res_c.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")

# ---------------------------------------------------------
# SEKME 3: SOSYAL OYLAMA MODÜLÜ
# ---------------------------------------------------------
with tab3:
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
    st.caption(f"Toplam {toplam} kişi oy kullandı.")

# ---------------------------------------------------------
# SEKME 4: SANAL GARAJ EKLEME
# ---------------------------------------------------------
with tab4:
    st.subheader("🚗 Kendi Aracını Garaja Ekle")
    g_marka = st.text_input("Marka ve Model:", placeholder="Örn: 2011 Opel Astra J 1.6", key="g_m")
    g_km = st.number_input("Kilometre:", value=150000, step=5000, key="g_k")
    g_deger = st.text_input("Tahmini Piyasa Değeri (TL):", placeholder="Örn: 650.000 TL", key="g_d")
    
    if st.button("➕ Garajıma Ekle", key="btn_g"):
        if g_marka:
            st.session_state.garaj.append({"marka": g_marka, "km": g_km, "deger": g_deger})
            st.session_state.puan += 100
            st.success(f"{g_marka} garajına eklendi! (+100 XP Kazandın)")
            st.rerun()

# ---------------------------------------------------------
# SEKME 5: BÜTÇEYE UYGUN ARAÇ & MOTOSİKLET BULUCU
# ---------------------------------------------------------
with tab5:
    st.subheader("💰 Bütçenize En Uygun Otomobil & Motosiklet Teşhisi")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        butce = st.number_input("💵 Toplam Bütçeniz (TL):", min_value=30000, value=350000, step=10000, key="b_price")
    with col_b2:
        vasita_turu = st.selectbox("🛵 Vasıta Türü:", ["Otomobil", "Motosiklet", "Ticari / Van"], key="b_type")
    with col_b3:
        oncelik = st.selectbox("🎯 Ana Önceliğiniz:", [
            "Az Yaksın / Ekonomik",
            "Kronik Arızası Olmasın / Sanayi Yüzü Görmesin",
            "Ayağımı Yerden Kessin / İlk Araç",
            "Yedek Parçası Ucuz & Piyasa Satışı Hızlı",
            "Performans & Görsel Karizma"
        ], key="b_prio")
        
    ekra_not = st.text_input("📝 Özel İsteğiniz var mı?", placeholder="Örn: Otomatik vites olsun, Scooter olsun vb.", key="b_note")

    if st.button("🚀 BÜTÇEME EN UYGUN SEÇENEKLERİ LİSTELE", key="btn_budget"):
        if not api_key:
            st.error("API Key bulunamadı.")
        else:
            with st.spinner("🤖 Bütçenize göre piyasa taranıyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt_budget = f"""
                    Sen Türkiye ikinci el otomobil ve motosiklet piyasasını çok iyi bilen kıdemli bir danışmansın.
                    Kullanıcının Parametreleri:
                    - Bütçe: {butce} TL
                    - Vasıta Türü: {vasita_turu}
                    - Kullanıcı Önceliği: {oncelik}
                    - Ek İstek: {ekra_not}

                    Lütfen bu bütçeye ve kriterlere en uygun 3 Mantıklı Modeli öner. 
                    Formatın şöyle olsun:

                    # 🎯 BÜTÇENİZE EN UYGUN {vasita_turu.upper()} ÖNERİLERİ

                    ### 1. [Marka Model Yıl Aralığı]
                    * **Neden Seçilmeli:** (Önceliğe uygunluğu)
                    * **Piyasa Fiyat Aralığı:** ... TL
                    * **Kronik Dikkat Edilecek Nokta:** ...

                    ### 2. [Marka Model Yıl Aralığı]
                    * **Neden Seçilmeli:** ...
                    * **Piyasa Fiyat Aralığı:** ... TL
                    * **Kronik Dikkat Edilecek Nokta:** ...

                    ### 3. [Marka Model Yıl Aralığı]
                    * **Neden Seçilmeli:** ...
                    * **Piyasa Fiyat Aralığı:** ... TL
                    * **Kronik Dikkat Edilecek Nokta:** ...

                    💡 **Mekaniker Tavsiyesi:** Bu bütçede alım yaparken en çok dikkat etmeniz gereken altın kural.
                    """
                    
                    res_b = client.models.generate_content(model='gemini-3.6-flash', contents=[prompt_budget])
                    st.balloons()
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.markdown(res_b.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")