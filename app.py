# Sekme Listesini Güncelle:
# tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 TEK ARAÇ ANALİZİ", "⚔️ İKİ ARAÇ KIYASLAMA", "🗳️ SOSYAL OYLAMA", "🚗 SANAL GARAJ", "💰 BÜTÇEYE GÖRE ARAÇ/MOTOR BUL"])

# ---------------------------------------------------------
# SEKME 5: BÜTÇEYE UYGUN ARAÇ & MOTOSİKLET BULUCU
# ---------------------------------------------------------
with tab5:
    st.subheader("💰 Bütçenize En Uygun Otomobil & Motosiklet Teşhisi")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        butce = st.number_input("💵 Toplam Bütçeniz (TL):", min_value=30000, value=350000, step=10000)
    with col_b2:
        vasita_turu = st.selectbox("🛵 Vasıta Türü:", ["Otomobil", "Motosiklet", "Ticari / Van"])
    with col_b3:
        oncelik = st.selectbox("🎯 Ana Önceliğiniz:", [
            "Az Yaksın / Ekonomik",
            "Kronik Arızası Olmasın / Sanayi Yüzü Görmesin",
            "Ayağımı Yerden Kessin / İlk Araç",
            "Yedek Parçası Ucuz & Piyasa Satışı Hızlı",
            "Performans & Görsel Karizma"
        ])
        
    ekra_not = st.text_input("📝 Özel İsteğiniz var mı?", placeholder="Örn: Otomatik vites olsun, Scooter olsun vb.")

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