import streamlit as st
import os
import re
from pathlib import Path
import requests as r
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

def get_download_path():
    """Return the default downloads path for the current OS."""
    return str(Path.home() / "Downloads")

def is_instagram_reels_url(url) -> bool:
    """Check if the URL is an Instagram reels URL."""
    pattern = r"https?://(?:www\.)?instagram\.com/reel/.*"
    return bool(re.match(pattern, url))

def download_reels(url) -> bytes:
    """Download reels video."""
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'video')))
    reel_source = element.get_attribute('src')
    return r.get(reel_source).content

def save_reel(content, filename):
    """Save the downloaded content to a file."""
    download_folder = get_download_path()
    file_path = os.path.join(download_folder, filename)
    with open(file_path, 'wb') as file:
        file.write(content)
    return file_path

def display_media(file_path):
    """Display the media file in the Streamlit app."""
    st.video(file_path)
    with open(file_path, 'rb') as file:
        st.download_button(label=f"Download {os.path.basename(file_path)}", data=file, file_name=os.path.basename(file_path))

# Streamlit UI for Instagram Reel Downloader
st.set_page_config(page_title="InstaLink Downloader", page_icon="😍")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            align: center;
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 20px;
            white-space: pre-wrap;
            background-color: #378299;
            border-radius: 4px 4px 0px 0px;
            gap: 10px;
            padding-top: 1px;
            padding-left: 10px;
            padding-right: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #B30B19;
        }
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.2rem;
            color: #00FFDD;
        }
        [data-baseweb="base-input"] {
            border: 1px solid #555;
            border-radius: 3px;
        }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: grey;'>Bit Link Downloader</h1>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center; color: #033333;'>Download videos from Instagram, Twitter, X, Terabos, YouTube, and more with our all-in-one solution. Easily save your favorite videos from multiple platforms using just a link.</h6>", unsafe_allow_html=True)
st.subheader('The best place to download video via :blue[link] :sunglasses:')

tab1, tab2, tab3, tab4 = st.tabs([":dancers: Insta", ":bird: tweet", "YouTube", " :yum: Other"])

with tab1:
    st.header("Insta Downloader", divider="rainbow")
    st.write("Features of Bit Link downloader Instagram video Downloader: · Instagram video Download Fast, easy and safe. · No need to login to your Instagram account.")
    url = st.text_input("Enter the Instagram Reel URL:")
    if st.button("Fetch"):
        if url and is_instagram_reels_url(url):
            try:
                content = download_reels(url)
                filename = f"reel_{url.split('/')[-2]}.mp4"
                file_path = save_reel(content, filename)
                st.success(f"Reel downloaded successfully! Saved to {file_path}")
                display_media(file_path)
            except Exception as e:
                st.error(f"Failed to download content: {str(e)}")
        else:
            st.error("Please enter a valid Instagram reel URL.")

with tab2:
    st.header("Twitter Downloader", divider="rainbow")
    url = st.text_input("Enter the Twitter Video URL")
    if st.button("Download Video"):
        if url:
            download_twitter_video(url)
        else:
            st.error("Please enter a valid Twitter video URL.")

with tab3:
    st.title('YouTube Video Downloader')
    url = st.text_input('Enter YouTube URL:', '')
    download_type = st.radio('Select Download Type:', ('Video (mp4)', 'Audio (mp3)'))
    if st.button('youtube Download'):
        if url:
            st.write('Downloading...')
            file_path = download_youtube_video(url, download_type)
            if os.path.exists(file_path):
                st.success('Download completed!')
                file_name = os.path.basename(file_path)
                st.download_button(label=f"Download {file_name}", data=open(file_path, "rb").read(), file_name=file_name)
        else:
            st.error("Please enter a valid YouTube URL.")

with tab4:
    st.header("Other Platform Downloader", divider="rainbow")
    url = st.text_input("Enter the URL")
    if st.button("url Download"):
        if url:
            download_link = download_dynamic_link(url)
            if download_link:
                st.success(f"Download link: {download_link}")
                st.write(download_link)
            else:
                st.error("Failed to retrieve download link.")
        else:
            st.error("Please enter a valid URL.")

