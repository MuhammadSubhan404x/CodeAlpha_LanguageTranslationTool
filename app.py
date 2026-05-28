import streamlit as st
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError, TooManyRequests
from gtts import gTTS
import io
import datetime

st.set_page_config(page_title="Language Translator", layout="wide")

LANGUAGES = {
    "Auto Detect": "auto",
    "Afrikaans": "af", "Albanian": "sq", "Amharic": "am", "Arabic": "ar",
    "Armenian": "hy", "Azerbaijani": "az", "Basque": "eu", "Belarusian": "be",
    "Bengali": "bn", "Bosnian": "bs", "Bulgarian": "bg", "Catalan": "ca",
    "Cebuano": "ceb", "Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW",
    "Corsican": "co", "Croatian": "hr", "Czech": "cs", "Danish": "da",
    "Dutch": "nl", "English": "en", "Esperanto": "eo", "Estonian": "et",
    "Finnish": "fi", "French": "fr", "Frisian": "fy", "Galician": "gl",
    "Georgian": "ka", "German": "de", "Greek": "el", "Gujarati": "gu",
    "Haitian Creole": "ht", "Hausa": "ha", "Hawaiian": "haw", "Hebrew": "iw",
    "Hindi": "hi", "Hmong": "hmn", "Hungarian": "hu", "Icelandic": "is",
    "Igbo": "ig", "Indonesian": "id", "Irish": "ga", "Italian": "it",
    "Japanese": "ja", "Javanese": "jw", "Kannada": "kn", "Kazakh": "kk",
    "Khmer": "km", "Korean": "ko", "Kurdish": "ku", "Kyrgyz": "ky",
    "Lao": "lo", "Latin": "la", "Latvian": "lv", "Lithuanian": "lt",
    "Luxembourgish": "lb", "Macedonian": "mk", "Malagasy": "mg", "Malay": "ms",
    "Malayalam": "ml", "Maltese": "mt", "Maori": "mi", "Marathi": "mr",
    "Mongolian": "mn", "Myanmar (Burmese)": "my", "Nepali": "ne", "Norwegian": "no",
    "Pashto": "ps", "Persian": "fa", "Polish": "pl", "Portuguese": "pt",
    "Punjabi": "pa", "Romanian": "ro", "Russian": "ru", "Samoan": "sm",
    "Serbian": "sr", "Sesotho": "st", "Shona": "sn", "Sindhi": "sd",
    "Sinhala": "si", "Slovak": "sk", "Slovenian": "sl", "Somali": "so",
    "Spanish": "es", "Sundanese": "su", "Swahili": "sw", "Swedish": "sv",
    "Tagalog (Filipino)": "tl", "Tajik": "tg", "Tamil": "ta", "Telugu": "te",
    "Thai": "th", "Turkish": "tr", "Ukrainian": "uk", "Urdu": "ur",
    "Uzbek": "uz", "Vietnamese": "vi", "Welsh": "cy", "Xhosa": "xh",
    "Yiddish": "yi", "Yoruba": "yo", "Zulu": "zu"
}

GTTS_SUPPORTED = {
    "af", "ar", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de", "el", "en",
    "eo", "es", "et", "fi", "fr", "gu", "hi", "hr", "hu", "hy", "id", "is",
    "it", "ja", "jw", "km", "ko", "la", "lv", "mk", "ml", "mr", "my", "ne",
    "nl", "no", "pl", "pt", "ro", "ru", "si", "sk", "sq", "sr", "su", "sv",
    "sw", "ta", "te", "th", "tl", "tr", "uk", "ur", "vi", "zh-CN", "zh-TW"
}

if "history" not in st.session_state:
    st.session_state.history = []

st.title("Language Translation Tool")
st.caption("Powered by Google Translate - supports 100+ languages with text-to-speech output")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Source")
    source_lang = st.selectbox("From", list(LANGUAGES.keys()), index=0)

with col2:
    st.subheader("Target")
    target_options = [k for k in LANGUAGES.keys() if k != "Auto Detect"]
    default_idx = target_options.index("Urdu") if "Urdu" in target_options else 0
    target_lang = st.selectbox("To", target_options, index=default_idx)

st.divider()

input_text = st.text_area(
    "Enter text to translate",
    height=160,
    placeholder="Type or paste your text here...",
    max_chars=5000
)

char_count = len(input_text)
remaining = 5000 - char_count
st.caption(f"{char_count} / 5000 characters  |  {remaining} remaining")

translate_btn = st.button("Translate", type="primary", use_container_width=True)

if translate_btn:
    if not input_text.strip():
        st.warning("Please enter some text to translate.")
    else:
        with st.spinner("Translating..."):
            try:
                src_code = LANGUAGES[source_lang]
                tgt_code = LANGUAGES[target_lang]

                translator = GoogleTranslator(source=src_code, target=tgt_code)
                result = translator.translate(input_text.strip())

                st.divider()
                st.subheader("Translation")

                res_col1, res_col2 = st.columns([6, 1])
                with res_col1:
                    st.text_area("Result", value=result, height=160, key="result_box")
                with res_col2:
                    st.write("")
                    st.write("")
                    st.download_button(
                        label="Save",
                        data=result,
                        file_name="translation.txt",
                        mime="text/plain"
                    )

                tgt_code_clean = tgt_code
                if tgt_code_clean in GTTS_SUPPORTED or tgt_code_clean.lower() in GTTS_SUPPORTED:
                    try:
                        tts = gTTS(text=result, lang=tgt_code_clean)
                        audio_buf = io.BytesIO()
                        tts.write_to_fp(audio_buf)
                        audio_buf.seek(0)
                        st.audio(audio_buf, format="audio/mp3")
                        st.caption("Text-to-speech output")
                    except Exception:
                        pass

                entry = {
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "from": source_lang,
                    "to": target_lang,
                    "input": input_text.strip()[:80] + ("..." if len(input_text) > 80 else ""),
                    "output": result[:80] + ("..." if len(result) > 80 else "")
                }
                st.session_state.history.insert(0, entry)
                if len(st.session_state.history) > 10:
                    st.session_state.history.pop()

            except TooManyRequests:
                st.error("Too many requests. Please wait a moment and try again.")
            except RequestError as e:
                st.error(f"Translation failed: {e}")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

if st.session_state.history:
    st.divider()
    with st.expander("Translation History (last 10)"):
        for i, entry in enumerate(st.session_state.history):
            st.markdown(
                f"**{entry['time']}** | {entry['from']} - {entry['to']}"
            )
            st.text(f"Input:  {entry['input']}")
            st.text(f"Output: {entry['output']}")
            if i < len(st.session_state.history) - 1:
                st.divider()
