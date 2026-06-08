import streamlit as st
from openai import OpenAI
import json
import urllib.parse
import random

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

st.set_page_config(page_title="Asistent Muzical", page_icon="🧸", layout="centered")

st.markdown("""
    <style>
    /* Importăm un font amuzant de tip Comic Book de la Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Bangers&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap');

    /* Stil pentru titlul principal (Efect 3D Comic Book) */
    .titlu-principal {
        color: #FFDE00; /* Galben aprins */
        text-align: center;
        font-family: 'Bangers', cursive;
        font-size: 70px;
        letter-spacing: 4px;
        text-shadow: 4px 4px 0px #E91E63, 8px 8px 0px #222222; /* Umbră dublă roz și neagră */
        margin-bottom: -10px;
    }

    /* Stil pentru subtitlu */
    .subtitlu {
        color: #17a2b8;
        text-align: center;
        font-family: 'Comic Neue', cursive;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 25px;
        margin-top: 15px;
    }

    /* Cartolină pentru joc */
    .card-joc {
        background-color: #fff9c4;
        padding: 20px;
        border-radius: 15px;
        border: 4px dashed #ff9800;
        box-shadow: 6px 6px 0px rgba(0,0,0,0.8); /* Umbră dură de benzi desenate */
        margin-top: 20px;
    }

    .titlu-joc {
        color: #e91e63;
        text-align: center;
        font-family: 'Bangers', cursive;
        font-size: 35px;
        letter-spacing: 2px;
        text-shadow: 2px 2px 0px #000;
    }

    /* Lista de reguli */
    .reguli-lista {
        color: #222;
        font-family: 'Comic Neue', cursive;
        font-size: 18px;
        line-height: 1.6;
        font-weight: bold;
    }

    /* Buton de YouTube */
    .yt-btn {
        display: block;
        background-color: #ff0000;
        color: white !important;
        padding: 12px 20px;
        border-radius: 10px;
        border: 2px solid #000;
        box-shadow: 4px 4px 0px #000;
        text-decoration: none;
        font-family: 'Comic Neue', cursive;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        width: 100%;
        transition: all 0.2s ease;
    }
    .yt-btn:hover {
        background-color: #cc0000;
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0px #000;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titlu-principal'>ASISTENT MUZICAL</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitlu'>Introdu versurile cântecului și lasă magia să găsească jocul perfect! ✨</p>",
            unsafe_allow_html=True)

lyrics_input = st.text_area("📝 Scrie aici versurile cântecelului:", height=150,
                            placeholder="Ex: Twinkle, twinkle, little star...")

JOCURI_SI_REGULI = {
    "Scaunele Muzicale Colaborative": [
        "🪑 Toate scaunele sunt puse în cerc, cu unul mai puțin decât numărul de copii.",
        "💃 Copiii dansează în jurul lor cât timp merge muzica.",
        "🫂 Când muzica se oprește, toți trebuie să se așeze, ajutându-se între ei (se pot lua în brațe).",
        "🏆 Nu este eliminat nimeni; la fiecare rundă scoatem un scaun și încercăm să încăpem toți."
    ],
    "Oglinda Ritmului": [
        "👯 Copiii se împart în perechi și stau față în față.",
        "🤪 Unul este „Liderul” și dansează haios pe ritmul vesel al muzicii.",
        "🪞 Celălalt este „Oglinda” și trebuie să îi copieze mișcările exact în același timp.",
        "🔄 La jumătatea melodiei, educatorul strigă „Schimb!” și rolurile se inversează."
    ],
    "Împăratul Tăcerii": [
        "👑 Un copil este „Împăratul” și stă pe un scaun cu spatele, păzind o jucărie.",
        "🤫 Ceilalți copii se apropie pe vârfuri, pe ritmul lent al muzicii, pentru a fura jucăria în liniște.",
        "👂 Dacă Împăratul aude un zgomot, se întoarce și arată spre copilul zgomotos, care o ia de la capăt.",
        "🏅 Câștigă cel care fură obiectul fără zgomot, devenind noul Împărat."
    ],
    "Podul Prieteniei": [
        "🌉 Copiii se împart în perechi și își țin mâinile ridicate, formând un pod.",
        "🚶 Pe rând, fiecare pereche trece pe sub podurile formate de colegi.",
        "💬 Când trec pe sub pod, colegii le spun un compliment scurt sau le fac cu mâna.",
        "❤️ Jocul aduce confort emoțional și sentimentul de siguranță pe o melodie reflexivă."
    ],
    "Detectivii în Misiune Secretă": [
        "🕵️ Copiii merg în vârful picioarelor prin clasă, foarte atenți la muzica misterioasă.",
        "🛑 Când educatorul oprește brusc muzica, toți trebuie să se lase la pământ și să devină „invizibili”.",
        "👮 Cine se mișcă după ce muzica s-a oprit, devine asistentul educatorului."
    ]
}

SYSTEM_PROMPT = """
Ești un asistent AI specializat în analiza muzicală. 
Sarcina ta este să analizezi versurile și să returnezi un răspuns strict în format JSON valid.

Reguli:
1. Emoția trebuie să fie strict una dintre: 'Veselă / Energetică', 'Calmă / Relaxantă', 'Tristă / Reflectivă', 'Anxioasă / Cu Suspans'.
2. Genul muzical: deduce un gen potrivit.

EXEMPLU JSON:
{
  "cantec": "Numele Piese",
  "artist": "Nume Artist",
  "emotie": "Calmă / Relaxantă",
  "gen_muzical": "Cântec de leagăn"
}

Este CRITIC să folosești EXACT aceste 4 chei: "cantec", "artist", "emotie", "gen_muzical".
Returnează DOAR codul JSON.
"""

if st.button("🚀 Analizează Versurile și Descoperă Jocul!", use_container_width=True, type="primary"):
    if not lyrics_input.strip():
        st.warning("⚠️ Te rog să introduci câteva versuri mai întâi!")
    else:
        with st.spinner("🧠 Rotițele AI-ului se învârt... BAM! ZAP! BOOM!"):
            try:
                response = client.chat.completions.create(
                    model="meta-llama-3-8b-instruct",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Analizează aceste versuri:\n\n{lyrics_input}"}
                    ],
                    temperature=0.1,
                )

                raw_content = response.choices[0].message.content.strip()
                if raw_content.startswith("```json"):
                    raw_content = raw_content.replace("```json", "").replace("```", "").strip()
                elif raw_content.startswith("```"):
                    raw_content = raw_content.replace("```", "").strip()

                data = json.loads(raw_content)

                st.balloons()
                st.success("🎉 SUPER! Iată ce am descoperit:")

                emotie_extrasa = data.get("emotie", "Necunoscută")
                gen_extras = data.get("gen_muzical", "Necunoscut")

                if "Vesel" in emotie_extrasa or "Energetic" in emotie_extrasa:
                    joc_ales = random.choice(["Scaunele Muzicale Colaborative", "Oglinda Ritmului"])
                elif "Calm" in emotie_extrasa or "Relaxant" in emotie_extrasa:
                    joc_ales = "Împăratul Tăcerii"
                elif "Trist" in emotie_extrasa or "Reflectiv" in emotie_extrasa:
                    joc_ales = "Podul Prieteniei"
                elif "Anxioas" in emotie_extrasa or "Suspans" in emotie_extrasa:
                    joc_ales = "Detectivii în Misiune Secretă"
                else:
                    joc_ales = "Oglinda Ritmului"

                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"🎭 **Emoție:** {emotie_extrasa}")
                with col2:
                    st.warning(f"🎸 **Gen:** {gen_extras}")

                st.markdown(
                    f"**🎼 Cântec:** *{data.get('cantec', 'Necunoscut')}* - **{data.get('artist', 'Necunoscut')}**")

                search_query = f"{data.get('cantec', '')} {data.get('artist', '')} song"
                encoded_query = urllib.parse.quote_plus(search_query.strip())
                youtube_url = f"[https://www.youtube.com/results?search_query=](https://www.youtube.com/results?search_query=){encoded_query}"

                st.markdown(f"<a href='{youtube_url}' target='_blank' class='yt-btn'>▶️ Ascultă piesa pe YouTube</a>",
                            unsafe_allow_html=True)

                reguli_finale = JOCURI_SI_REGULI.get(joc_ales, [])
                reguli_html = "".join([f"<li>{r}</li>" for r in reguli_finale])

                st.markdown(f"""
                <div class="card-joc">
                    <h2 class="titlu-joc">🕹️ JOC RECOMANDAT: <br>{joc_ales.upper()}</h2>
                    <p style="text-align: center; font-size: 18px; color: #555; font-family: 'Comic Neue', cursive;"><b>Cum ne jucăm?</b></p>
                    <ul class="reguli-lista">
                        {reguli_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                st.write("---")
                with st.expander("🛠️ Vezi răspunsul brut generat de AI (Pentru profesori)"):
                    st.json(data)

            except Exception as e:
                st.error(f"❌ Ups! A apărut o eroare: {e}")