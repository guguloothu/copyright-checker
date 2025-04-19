import streamlit as st
import requests
import pandas as pd
import base64
from urllib.parse import urlparse

st.set_page_config(page_title="Copyright Checker Tool", layout="centered")

# 💡 Mobile-friendly styling
st.markdown("""<style>
    .block-container {
        padding: 1rem 1rem 2rem 1rem;
        max-width: 600px;
        margin: auto;
    }
    audio, img {
        max-width: 100% !important;
        height: auto;
    }
    @media (prefers-color-scheme: dark) {
        html, body {
            background-color: #1e1e1e;
            color: #ffffff;
        }
    }
</style>""", unsafe_allow_html=True)

st.title("🛡️ Copyright Checker Tool")

option = st.selectbox("Choose the content type to check:", ["Image URL or Upload", "Music URL or Upload", "Text"])

log = []

def check_image_source(url):
    known_free_domains = ["unsplash.com", "pexels.com", "pixabay.com"]
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    for free_domain in known_free_domains:
        if free_domain in domain:
            return f"✅ This image is from {domain} — typically copyright-free."
    return f"⚠️ This image source ({domain}) is not a known copyright-free provider."

def check_music_audd_api(file_or_url):
    audd_api_token = "your_audd_api_key"  # Replace with your actual token
    if isinstance(file_or_url, str):
        response = requests.post("https://api.audd.io/", data={
            'api_token': audd_api_token,
            'url': file_or_url,
            'return': 'apple_music,spotify',
        })
    else:
        file_bytes = file_or_url.read()
        encoded_file = base64.b64encode(file_bytes).decode('utf-8')
        response = requests.post("https://api.audd.io/", data={
            'api_token': audd_api_token,
            'audio': encoded_file,
            'return': 'apple_music,spotify',
        })
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success' and result['result']:
            return f"❌ Copyrighted: {result['result']['title']} by {result['result']['artist']}"
        else:
            return "✅ No match found. May be copyright-free."
    return "⚠️ Error contacting AudD API."

def check_text_similarity(text):
    if len(text) < 20:
        return "⚠️ Text too short to analyze."
    # Sample placeholder for real-time check
    response = requests.post("https://api.text-similarity.com/compare", json={
        "text1": text,
        "text2": "publicly available content to compare"
    })
    if response.status_code == 200:
        score = response.json().get("score", 0)
        if score > 0.8:
            return f"❌ High similarity detected (score: {score:.2f}) — Potential copyright."
        else:
            return f"✅ Low similarity (score: {score:.2f}) — Likely original."
    return "⚠️ Could not connect to similarity API."

if option == "Image URL or Upload":
    image_url = st.text_input("Enter Image URL")
    uploaded_image = st.file_uploader("Or upload an image", type=["png", "jpg", "jpeg"])
    
    if image_url:
        st.image(image_url, use_column_width=True)
        result = check_image_source(image_url)
        st.info(result)
        log.append(["Image", image_url, result])
    elif uploaded_image:
        st.image(uploaded_image, use_column_width=True)
        st.info("⚠️ Upload check for copyright not available — use URL.")
        log.append(["Image Upload", uploaded_image.name, "Manual Check Required"])

elif option == "Music URL or Upload":
    music_url = st.text_input("Enter Music URL")
    uploaded_music = st.file_uploader("Or upload MP3", type=["mp3"])

    if music_url:
        st.audio(music_url)
        result = check_music_audd_api(music_url)
        st.info(result)
        log.append(["Music URL", music_url, result])
    elif uploaded_music:
        st.audio(uploaded_music)
        result = check_music_audd_api(uploaded_music)
        st.info(result)
        log.append(["Music Upload", uploaded_music.name, result])

elif option == "Text":
    user_text = st.text_area("Paste text here")
    if user_text:
        result = check_text_similarity(user_text)
        st.success(result)
        log.append(["Text", user_text[:50] + "...", result])

if log:
    if st.button("📥 Download Check Log"):
        df = pd.DataFrame(log, columns=["Type", "Input", "Result"])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Log as CSV", data=csv, file_name="copyright_check_log.csv", mime="text/csv")

st.caption("🔧 Built with ❤️ by Arjun using Streamlit")
