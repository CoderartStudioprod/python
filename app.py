import streamlit as st
import instaloader
from instaloader import Post
import os
from urllib.parse import urlparse, parse_qs
import requests
import re
from pathlib import Path
from pytube import YouTube
from pydub import AudioSegment
from tqdm import tqdm
import bs4
from bs4 import BeautifulSoup

# Function to check if the URL is an Instagram reels URL
def is_instagram_reels_url(url) -> bool:
    pattern = r"https?://(?:www\.)?instagram\.com/reel/.*"
    return bool(re.match(pattern, url))

# Function to get the default download path
def get_download_path():
    return str(Path.home() / "Downloads")

# Function to display video with download option
def display_media(video_url):
    video_html = f"""
    <video width="640" height="360" controls>
        <source src="{video_url}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    <br>
    <a href="{video_url}" target="_blank" class="button">Download Now</a>
    <style>
        .button {{
            background-color: #240750;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
            border-radius: 8px;
        }}
        .button:hover {{
            background-color: #45a049;
        }}
    </style>
    """
    st.markdown(video_html, unsafe_allow_html=True)

# Function to download Instagram content
def download_instagram_content(url):
    try:
        L = instaloader.Instaloader()
        download_folder = get_download_path()
        shortcode = url.split("/")[-2]
        post = Post.from_shortcode(L.context, shortcode)
        target_folder = os.path.join(download_folder, f"Instagram_{shortcode}")
        os.makedirs(target_folder, exist_ok=True)

        # Check if the post is a Reel
        if post.typename == "GraphSidecar":
            for sidecar_node in post.get_sidecar_nodes():
                if sidecar_node.is_video:
                    video_url = sidecar_node.video_url
                    display_media(video_url)
        elif post.typename == "GraphVideo":
            video_url = post.video_url
            display_media(video_url)
        else:
            return False, "Unsupported post type"

        return True, target_folder
    except Exception as e:
        return False, str(e)

# Streamlit app settings and layout
st.set_page_config(page_title="InstaLink Downloader", page_icon="😍")

# Remove whitespace from the top of the page and sidebar
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 1rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 20px;
            white-space: pre-wrap;
            background-color: #378299;
            border-radius: 4px 4px 0px 0px;
            padding: 1px 10px;
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
st.markdown("<h6 style='text-align: center; color: #033333;'>Download videos from Instagram, Twitter, YouTube, and more with our all-in-one solution. Easily save your favorite videos from multiple platforms using just a link.</h6>", unsafe_allow_html=True)
st.subheader('The best place to download video via link')

tab1, tab2, tab3 = st.tabs([":dancers: Insta", ":bird: Twitter", "YouTube"])

# Instagram Downloader Tab
with tab1:
    st.header("Insta Downloader")
    st.write("Features of Bit Link downloader Instagram video Downloader: · Instagram video Download Fast, easy and safe. · No need to login to your Instagram account.")
    url = st.text_input("Enter the Instagram Reel URL:")
    if st.button("Fetch"):
        if url and is_instagram_reels_url(url):
            success, media_path = download_instagram_content(url)
            if success:
                st.success(f"Content downloaded successfully! Saved to {media_path}")
            else:
                st.error(f"Failed to download content: {media_path}")
        else:
            st.error("Please enter a valid URL.")

# Twitter Downloader Tab
with tab2:
    st.header("Twitter Downloader")

    def download_video(url, file_name):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

        download_path = os.path.join(Path.home(), "Downloads", file_name)

        with open(download_path, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()
        st.success("Video downloaded successfully!")

    def download_twitter_video(url):
        api_url = f"https://twitsave.com/info?url={url}"
        response = requests.get(api_url)
        data = BeautifulSoup(response.text, "html.parser")
        download_button = data.find_all("div", class_="origin-top-right")[0]
        quality_buttons = download_button.find_all("a")
        highest_quality_url = quality_buttons[0].get("href")
        
        file_name = data.find_all("div", class_="leading-tight")[0].find_all("p", class_="m-2")[0].text
        file_name = re.sub(r"[^a-zA-Z0-9]+", ' ', file_name).strip() + ".mp4"
        
        download_video(highest_quality_url, file_name)

    url = st.text_input("Enter the Twitter Video URL")
    if st.button("Download Video"):
        if url:
            download_twitter_video(url)
        else:
            st.error("Please enter a valid Twitter video URL.")

# YouTube Downloader Tab
with tab3:
    st.title('YouTube Video Downloader')

    def download_youtube_video(url, download_type):
        try:
            yt = YouTube(url)
            if download_type == 'Video (mp4)':
                stream = yt.streams.get_highest_resolution()
                output_path = stream.download()
            elif download_type == 'Audio (mp3)':
                stream = yt.streams.filter(only_audio=True).first()
                output_path = stream.download()
                base, ext = os.path.splitext(output_path)
                new_file = base + '.mp3'
                audio = AudioSegment.from_file(output_path)
                audio.export(new_file, format='mp3')
                os.remove(output_path)
                output_path = new_file
            return output_path
        except Exception as e:
            return str(e)

    url = st.text_input('Enter YouTube URL:', '')
    download_type = st.radio('Select Download Type:', ('Video (mp4)', 'Audio (mp3)'))
    if st.button('Download'):
        if url:
            output_path = download_youtube_video(url, download_type)
            if os.path.exists(output_path):
                st.success(f"{download_type} downloaded successfully! Saved to {output_path}")
                st.write(output_path)
            else:
                st.error(output_path)
        else:
            st.error("Please enter a valid YouTube URL.")
