import streamlit as st
from google import genai
from PIL import Image
import time
from datetime import date

# ---------------------------------------------------------
# SAYFA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="AutoCheck AI PRO - Cyber Garaj Portal",
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

# ---------------------------------------------------------
# SİBER GARAJ CSS & GELİŞMİŞ GÖRSEL EFEKTLER
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Koyu Garaj Arka Planı & Izgara Animasyon Hissi */
    .stApp {
        background: radial-gradient(circle at top, #0f172a 0%, #020617 80%, #000000 100%);
        color: #f8fafc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Kayan Duyuru / Sponsor Bandı */
    .marquee-box {
        background: linear-gradient(90deg, #b91c1c 0%, #dc2626 50%, #b91c1c 100%);
        color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: 800;
        font-size: 0.95rem;
        box-shadow: 0 0 20px rgba(220, 38, 38, 0.4);
        margin-bottom: 25px;
        border: 1px solid #f87171;
    }

    /* Neon Dev Başlık */
    .hero-title {
        font-size: 3.2rem;
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

    /* XP & Garaj Puan Kartı */
    .xp-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 2px solid #818cf8;
        border-radius: 14px;
        padding: 12px 20px;
        text-align: center;
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.3);
    }

    /* Kartlar ve Çerçeveler */
    .cyber-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #38bdf8;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.15);
        backdrop-filter: blur(8px);
        margin-bottom: 15px;
    }

    .vote-box {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
        border: 2px solid #6366f1;
        border-radius: 18px;
        padding: 22px;
        text-align: center;
        box-shadow: 0 0 25px rgba(99, 102, 241, 0.25);
    }

    .report-box {
        background: rgba(15, 23, 42, 0.95);
        border: 2px solid #38bdf8;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.25);
        margin-top: 15px;
    }

    /* Buton Tasarımları & Hover Efekti */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #4f46e5 50%, #7c3aed 100%);
        color: white;
        font-weight: 800;
        font-size: 1.05rem;
        border-radius: 12px;
        border: none;
        padding: 14px;
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(124, 58, 237, 0.7);
    }

    /* Pasif Buton Stili (Ödül Alındığında) */
    .stButton>button:disabled {
        background: #334155 !important;
        color: #94a3b8 !important;
        border: 1px solid #475569 !important;
        box-shadow: none !important;
        transform: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SPONSOR & DUYURU BANT
# ---------------------------------------------------------
st.markdown("""
<div class="marquee-box">
    🔥 <b>GARAJ2026 KUPO KODU İLE:</b> Anlaşmalı Kurumsal Ekspertiz Merkezlerinde <b>%20 İndirim!</b>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ÜST BAŞLIK VE GÜNLÜK ÖDÜL KONTROLÜ
# ---------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    st.markdown('<div class="hero-title">🏎️ AutoCheck AI PRO</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Yapay Zekâ Destekli Cyber-Ekspertiz, İkinci El Araç & Motosiklet Analiz Portalı</div>', unsafe_allow_html=True)

with col_head2:
    st.markdown(f"""
    <div class="xp-card">
        <small style="color: #cbd5e1;">TOPLAM PUANIN</small><br>
        <span style="font-size: 1.5rem; font-weight: 900; color: #38bdf8;">🏆 {st.session_state.puan} XP</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    today = str(date.today())
    
    # Günlük Tek Seferlik Ödül Kontrolü
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
    api_key = st.sidebar.text_input("🔑 Gemini API Key (Giriş Yapın):", type="password")

# ---------------------------------------------------------
# YAN PANEL (SIDEBAR) SANAL GARAJ BİLGİSİ
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚘 SANAL GARAJIM")
    if not st.session_state.garaj:
        st.info("Garajın boş. 'Sanal Garaj' sekmesinden aracını ekleyip değerini izleyebilirsin.")
    else:
        for car in st.session_state.garaj:
            st.markdown(f"""
            <div style="background: #1e293b; border: 1px solid #38bdf8; border-radius: 10px; padding: 10px; margin-bottom: 8px;">
                <b>{car['marka']}</b><br>
                <small>📐 {car['km']} KM | 💰 {car['deger']}</small>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("AutoCheck Engine v4.2 Pro | Cyber Edition")

# ---------------------------------------------------------
# 5 ANA SEKMELİ YAPILANDIRMA
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
        link_single = st.text_input("🔗 İlan Linki (Sahibinden, Letgo vb.):", key="link_s")
        text_single = st.text_area("✍️ İlan Metni / Notlar:", height=130, key="text_s", placeholder="Örn: 2012 VW Crafter 2.0 TDI, 220.000 km, sol çamurluk boyalı...")
    with col_input2:
        up_single = st.file_uploader("📷 Araç / Ekspertiz Fotoğrafı Yükle:", type=["jpg", "jpeg", "png"], key="up_s")
        img_single = Image.open(up_single) if up_single else None
        if img_single: 
            st.image(img_single, caption="⚡ Visual Scan Aktif", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ DETAYLI CYBER ANALİZ BAŞLAT", key="btn_s"):
        if not api_key:
            st.error("Gemini API Key bulunamadı.")
        elif not link_single and img_single is None and not text_single.strip():
            st.warning("Lütfen analiz için ilan linki, metin veya resim ekleyin.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for p in range(0, 101, 25):
                time.sleep(0.1)
                progress_bar.progress(p)
                if p == 25: status_text.text("⚙️ Motor ve Şanzıman Veritabanı Taranıyor...")
                elif p == 75: status_text.text("⚡ Görsel Optik İnceleme Tamamlanıyor...")
                elif p == 100: status_text.text("✅ Analiz Tamamlandı!")

            try:
                client = genai.Client(api_key=api_key)
                prompt = """
                Sen usta bir oto ekspertiz mekanikerisin. Sana verilen verileri detaylı incele.
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚔️ İKİ ARACI KIYASLA VE KAZANANI SEÇ", key="btn_c"):
        if not api_key:
            st.error("API Key eksik.")
        elif not text_A and not text_B and not link_A and not link_B:
            st.warning("Lütfen her iki araç için de bilgi veya link girin.")
        else:
            with st.spinner("İki araç kapıştırılıyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt_c = f"Şu iki aracı detaylı kıyasla, ikisine de 10 üzerinden puan ver ve hangisinin neden alınması gerektiğini açıkla:\nAraç A: {link_A} {text_A}\nAraç B: {link_B} {text_B}"
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
    st.subheader("🔥 Günün Topluluk İlanı: Bu Araç Alınır mı?")
    
    st.markdown("""
    <div class="vote-box">
        <h3>🚘 2012 Volkswagen Crafter 2.0 TDI (220.000 km)</h3>
        <p><i>"Motor sıfır yapıldı deniyor, sol çamurluk lokal boyalı. Fiyat piyasanın %10 altında."</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### 📊 Topluluk Kararı: **%{oran} ALINIR**")
    st.progress(oran / 100)
    st.caption(f"Toplam {toplam} kullanıcı oy kullandı.")

# ---------------------------------------------------------
# SEKME 4: SANAL GARAJ EKLEME
# ---------------------------------------------------------
with tab4:
    st.subheader("🚗 Kendi Aracını Garaja Ekle (Değerini İzle)")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        g_marka = st.text_input("Marka ve Model:", placeholder="Örn: 2011 Opel Astra J 1.6", key="g_m")
        g_km = st.number_input("Kilometre:", value=150000, step=5000, key="g_k")
    with col_g2:
        g_deger = st.text_input("Tahmini Piyasa Değeri (TL):", placeholder="Örn: 650.000 TL", key="g_d")
    
    if st.button("➕ Garajıma Ekle (+100 XP)", key="btn_g"):
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
        
    ekra_not = st.text_input("📝 Özel İsteğiniz Var mı?", placeholder="Örn: Otomatik vites olsun, Scooter olsun vb.", key="b_note")

    st.markdown("<br>", unsafe_allow_html=True)
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