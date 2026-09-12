import streamlit as st
from google import genai
from PIL import Image
from datetime import date
import random

# ---------------------------------------------------------
# SAYFA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="AutoCheck Hub - Tüm İlanlar Tek Yerde",
    page_icon="🏎️",
    layout="wide"
)

# ---------------------------------------------------------
# TASLAK / RASTGELE İNTERNET İLANLARI BOT HAVUZU
# ---------------------------------------------------------
HAZIR_ILAN_HAVUZU = [
    {"baslik": "2016 BMW 320i ED 1.6 M Sport", "fiyat": "980.000 TL", "km": "142.000 KM", "sehir": "Ankara / Çankaya", "kaynak": "Sahibinden", "link": "https://www.sahibinden.com", "detay": "Borusan çıkışlı, sanruf, recaro koltuk, sol çamurluk boyalı."},
    {"baslik": "2020 Renault Megane 1.5 dCi Joy", "fiyat": "820.000 TL", "km": "98.000 KM", "sehir": "İstanbul / Kadıköy", "kaynak": "Letgo", "link": "https://www.letgo.com", "detay": "Hatasız, boyasız, bakımları yetkili serviste yapılmıştır."},
    {"baslik": "2021 Honda PCX 125 Scooter", "fiyat": "125.000 TL", "km": "12.500 KM", "sehir": "Hatay / İskenderun", "kaynak": "Sahibinden", "link": "https://www.sahibinden.com", "detay": "Düşmesi kalkması yok. Çanta ve konfor sele eklentili."},
    {"baslik": "2019 Volkswagen Golf 1.6 TDI Comfortline", "fiyat": "890.000 TL", "km": "115.000 KM", "sehir": "İzmir / Bornova", "kaynak": "Arabam.com", "link": "https://www.arabam.com", "detay": "Cam tavanlı, değişensiz, 2 parça lokal boyalı."},
    {"baslik": "2022 Yamaha MT-07 ABS", "fiyat": "325.000 TL", "km": "14.000 KM", "sehir": "Bursa / Nilüfer", "kaynak": "Sahibinden", "link": "https://www.sahibinden.com", "detay": "Akrapovic egzoz, koruma takozları ve radyatör koruma mevcut."},
    {"baslik": "2015 Opel Astra J 1.6 CDTI Sport", "fiyat": "640.000 TL", "km": "168.000 KM", "sehir": "Adana / Seyhan", "kaynak": "Letgo", "link": "https://www.letgo.com", "detay": "136 hp güçlü motor, tesla ekranlı, tramer 3 bin TL."},
    {"baslik": "2018 Toyota Corolla 1.8 Hybrid Dream", "fiyat": "875.000 TL", "km": "85.000 KM", "sehir": "Antalya / Muratpaşa", "kaynak": "Arabam.com", "link": "https://www.arabam.com", "detay": "Batarya garantisi devam ediyor, çok az yakar, yakıt cimrisi."},
    {"baslik": "2017 Fiat Egea 1.3 Multijet Easy", "fiyat": "530.000 TL", "km": "150.000 KM", "sehir": "Kayseri / Melikgazi", "kaynak": "Sahibinden", "link": "https://www.sahibinden.com", "detay": "Taksi çıkması değildir. Orijinal km, masrafsız aile aracı."},
    {"baslik": "2023 Honda Civic 1.5 VTEC Executive+", "fiyat": "1.450.000 TL", "km": "22.000 KM", "sehir": "İstanbul / Ataşehir", "kaynak": "Sahibinden", "link": "https://www.sahibinden.com", "detay": "Bayi çıkışlı, seramik kaplama yapılmış, sıfır ayarında."},
    {"baslik": "2020 Vespa GTS 300 HPE", "fiyat": "240.000 TL", "km": "9.500 KM", "sehir": "Muğla / Bodrum", "kaynak": "Letgo", "link": "https://www.letgo.com", "detay": "Kapalı garaj motoru, çiziksiz, özel lansman rengi."}
]

# ---------------------------------------------------------
# OTURUM HAFIZASI (SESSION STATE)
# ---------------------------------------------------------
if 'pazar_ilanlari' not in st.session_state:
    st.session_state.pazar_ilanlari = HAZIR_ILAN_HAVUZU.copy()

if 'garaj' not in st.session_state:
    st.session_state.garaj = []
if 'puan' not in st.session_state:
    st.session_state.puan = 250
if 'son_odul_tarihi' not in st.session_state:
    st.session_state.son_odul_tarihi = None
if 'analiz_metni_aktar' not in st.session_state:
    st.session_state.analiz_metni_aktar = ""

# ---------------------------------------------------------
# CSS TASARIM DOKUNUŞLARI
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
        transition: all 0.2s ease-in-out;
        min-height: 180px;
    }
    .mini-ad-box:hover {
        border-color: #38bdf8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
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
    .xp-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 2px solid #818cf8;
        border-radius: 12px;
        padding: 8px 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ÜST BAŞLIK & PUAN PANOLARI
# ---------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    st.markdown('<div class="hero-title">🏎️ AutoCheck Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Sahibinden, Letgo ve Arabam.com İlanları Tek Tıkla Önünde!</div>', unsafe_allow_html=True)

with col_head2:
    st.markdown(f"""
    <div class="xp-card">
        <small style="color: #cbd5e1;">PUANIN</small> | 
        <span style="font-size: 1.2rem; font-weight: 900; color: #38bdf8;">🏆 {st.session_state.puan} XP</span>
    </div>
    """, unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password")

# ---------------------------------------------------------
# SEKMELER (İLAN VERME VE İNCELEME DAHİL)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🌐 TÜM İLANLAR (SAYFA SAYFA)", 
    "📢 İLAN EKLE (PAZARA SÜR)", 
    "🤖 AI ARAÇ BULUCU", 
    "🔍 TEK ARAÇ ANALİZİ"
])

# ---------------------------------------------------------
# SEKME 1: SAYFA SAYFA İLANLAR & RASTGELE BULUCU
# ---------------------------------------------------------
with tab1:
    st.subheader("🔥 İnternetteki Canlı İlan Akışı")
    
    col_top1, col_top2 = st.columns([2, 1])
    with col_top1:
        st.caption("İstediğin ilanın orijinal sayfasına gitmek için **'İlana Git'** butonuna basabilirsin.")
    with col_top2:
        # İnternetten/Havuzdan rastgele 4 yeni ilan ekleme botu
        if st.button("🎲 RASTGELE 4 YENİ İLAN BUL & EKLE", key="btn_fetch_random"):
            random_sample = random.sample(HAZIR_ILAN_HAVUZU, min(4, len(HAZIR_ILAN_HAVUZU)))
            for item in random_sample:
                st.session_state.pazar_ilanlari.insert(0, item)
            st.toast("İnternetten 4 yeni linkli ilan çekildi!", icon="🔄")
            st.rerun()

    st.markdown("---")

    # --- SAYFALAMA (PAGINATION) MANTIĞI ---
    ILAN_PER_PAGE = 4
    toplam_ilan = len(st.session_state.pazar_ilanlari)
    toplam_sayfa = (toplam_ilan + ILAN_PER_PAGE - 1) // ILAN_PER_PAGE

    col_p1, col_p2 = st.columns([1, 3])
    with col_p1:
        secilen_sayfa = st.number_input("📄 Sayfa Seç:", min_value=1, max_value=max(1, toplam_sayfa), value=1, step=1)
    with col_p2:
        st.markdown(f"<br><small style='color:#94a3b8;'>Toplam <b>{toplam_ilan}</b> ilan içerisinden Sayfa <b>{secilen_sayfa} / {toplam_sayfa}</b> gösteriliyor.</small>", unsafe_allow_html=True)

    start_idx = (secilen_sayfa - 1) * ILAN_PER_PAGE
    end_idx = start_idx + ILAN_PER_PAGE
    sayfa_ilanlari = st.session_state.pazar_ilanlari[start_idx:end_idx]

    # İlanları 2'li Kolonlar Halinde Kart Yapma
    cols = st.columns(2)
    for idx, item in enumerate(sayfa_ilanlari):
        col_target = cols[idx % 2]
        with col_target:
            img_html = ""
            if item.get("img"):
                st.image(item["img"], use_container_width=True)
            
            st.markdown(f"""
            <div class="mini-ad-box">
                <span class="source-badge">{item.get('kaynak', 'Özel İlan')}</span>
                <span style="float:right;" class="price-text">{item['fiyat']}</span>
                <h4 style="margin: 10px 0 6px 0; font-size:1.05rem;">{item['baslik']}</h4>
                <p style="color:#94a3b8; font-size:0.85rem; margin-bottom:6px;">📍 {item['sehir']} | 📐 {item['km']}</p>
                <p style="color:#cbd5e1; font-size:0.8rem;">{item['detay']}</p>
                <a href="{item.get('link', '#')}" target="_blank" class="go-btn">🔗 {item.get('kaynak', 'İlgili Sitede')} İlana Git</a>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"⚡ AI İle Analiz Et", key=f"btn_quick_{start_idx + idx}"):
                st.session_state.analiz_metni_aktar = f"Araç: {item['baslik']} | Fiyat: {item['fiyat']} | KM: {item['km']} | Lokasyon: {item['sehir']} | Detay: {item['detay']}"
                st.toast("İlan AI Analiz Sekmesine Gönderildi!", icon="🧠")

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
                        contents=[f"Şu ilanı detaylı incele, 10 üzerinden puan ver ve alırken dikkat edilecek 3 mekanik riski söyle:\n{st.session_state.analiz_metni_aktar}"]
                    )
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.markdown(res.text)
                    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# SEKME 2: İLAN VERME / PAZARA EKLEME
# ---------------------------------------------------------
with tab2:
    st.subheader("📢 Aracının veya Bulduğun Bir İlanın Linkini Ekle")
    st.caption("Kendi aracını satabilir veya internette gördüğün güzel bir Sahibinden/Letgo ilan linkini ekleyerek topluluğa sunabilirsin.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        in_baslik = st.text_input("İlan Başlığı (Marka Model Yıl):", placeholder="Örn: 2017 Polo 1.2 TSI", key="add_b")
        in_fiyat = st.text_input("Satış Fiyatı (TL):", placeholder="Örn: 650.000 TL", key="add_f")
        in_km = st.text_input("KM & Şehir:", placeholder="Örn: 95.000 KM / İzmir", key="add_k")
    with col_b:
        in_site = st.selectbox("İlan Hangi Siteden?", ["Sahibinden", "Letgo", "Arabam.com", "Kendi İlanım"], key="add_s")
        in_link = st.text_input("Orijinal İlan Linki (URL):", placeholder="https://www.sahibinden.com/ilan/...", key="add_l")
        in_detay = st.text_area("İlan Açıklaması / Ekspertiz:", placeholder="Sol kapı boyalı, bakımları yeni...", key="add_d")
        in_img = st.file_uploader("Araç Fotoğrafı (Opsiyonel):", type=["jpg", "png", "jpeg"], key="add_img")

    if st.button("🚀 İLANI SİTEYE YAYINLA (+150 XP)", key="btn_save_ad"):
        if in_baslik and in_fiyat:
            uploaded_img = Image.open(in_img) if in_img else None
            yeni_ilan = {
                "baslik": in_baslik,
                "fiyat": in_fiyat,
                "km": in_km,
                "sehir": "Türkiye",
                "kaynak": in_site,
                "link": in_link if in_link else "#",
                "detay": in_detay,
                "img": uploaded_img
            }
            st.session_state.pazar_ilanlari.insert(0, yeni_ilan)
            st.session_state.puan += 150
            st.success("İlan başarıyla yayınlandı! En üste eklendi (+150 XP).")
            st.rerun()
        else:
            st.warning("Lütfen en az Başlık ve Fiyat kısımlarını doldurun.")

# ---------------------------------------------------------
# SEKME 3: BÜTÇEYE GÖRE ARAÇ BULUCU
# ---------------------------------------------------------
with tab3:
    st.subheader("💰 Bütçene Göre Araç/Motor Bul")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        b_price = st.number_input("Bütçen (TL):", value=600000, step=25000, key="b_p")
        b_type = st.selectbox("Tür:", ["Otomobil", "Motosiklet", "Ticari / Van"], key="b_t")
    with col_b2:
        b_prio = st.selectbox("Öncelik:", ["Performans", "Az Yaksın", "Kronik Arızasız", "Yedek Parça Ucuz"], key="b_pr")
        b_note = st.text_input("Özel Not (Örn: BMW olsun, Otomatik olsun):", key="b_n")

    if st.button("🔍 SEÇENEKLERİ LİSTELE", key="btn_b_find"):
        if api_key:
            with st.spinner("🤖 Yapay zekâ uygun 5 araç seçeneğini hazırlıyor..."):
                client = genai.Client(api_key=api_key)
                prompt = f"Bütçe: {b_price} TL, Tür: {b_type}, Öncelik: {b_prio}, Not: {b_note}. Kullanıcıya tam 5 farklı araç/motor öner. Artılarını ve eksilerini detaylı listele."
                res = client.models.generate_content(model='gemini-3.6-flash', contents=[prompt])
                st.markdown('<div class="report-box">', unsafe_allow_html=True)
                st.markdown(res.text)
                st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# SEKME 4: TEK ARAÇ ANALİZİ
# ---------------------------------------------------------
with tab4:
    st.subheader("🔍 Özel Metin & Fotoğraf Analizi")
    in_text = st.text_area("İlan Metni / Notlar:", height=100, key="single_t")
    in_img_s = st.file_uploader("Fotoğraf Yükle:", type=["jpg", "png"], key="single_i")
    
    if st.button("⚡ ANALİZ ET", key="btn_single_run"):
        if api_key and (in_text or in_img_s):
            with st.spinner("İnceleniyor..."):
                client = genai.Client(api_key=api_key)
                contents = ["Oto ekspertiz uzmanı olarak bu aracı puanla ve mekanik durumunu yorumla:"]
                if in_text: contents.append(in_text)
                if in_img_s: contents.append(Image.open(in_img_s))
                
                res_s = client.models.generate_content(model='gemini-3.6-flash', contents=contents)
                st.markdown('<div class="report-box">', unsafe_allow_html=True)
                st.markdown(res_s.text)
                st.markdown('</div>', unsafe_allow_html=True)