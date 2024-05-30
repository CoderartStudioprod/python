import streamlit as st
import instaloader
from instaloader import Post
import os
from urllib.parse import urlparse, parse_qs
import requests
import time
from streamlit_option_menu import option_menu
import re
import bs4
from tqdm import tqdm
from pathlib import Path
from pytube import YouTube
from bs4 import BeautifulSoup
from pydub import AudioSegment

# Initialize Instaloader
L = instaloader.Instaloader()

def is_instagram_reels_url(url) -> bool:
    """
    Check the url is instagram reels url?
    :param url: instagram reels url
    :return: bool
    """
    pattern = r"https?://(?:www\.)?instagram\.com/reel/.*"
    match = re.match(pattern, url)
    return bool(match)

def download_reel(url) -> bytes:
    """
    Download reels video

    :param url: instagram reels url
    :return: bytes
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    video_tag = soup.find('meta', property='og:video')
    if video_tag and 'content' in video_tag.attrs:
        video_url = video_tag['content']
        return requests.get(video_url).content
    else:
        raise ValueError("Could not find video URL")

def get_download_path():
    """Return the default downloads path for the current OS."""
    return str(Path.home() / "Downloads")

def save_reel_content(content, shortcode):
    download_folder = get_download_path()
    target_folder = os.path.join(download_folder, f"Instagram_{shortcode}")
    os.makedirs(target_folder, exist_ok=True)
    file_path = os.path.join(target_folder, f"{shortcode}.mp4")
    with open(file_path, 'wb') as file:
        file.write(content)
    return file_path

def display_media(file_path):
    """Display the media file in the Streamlit app."""
    st.video(file_path)
    with open(file_path, 'rb') as file:
        st.download_button(label=f"Download {os.path.basename(file_path)}", data=file, file_name=os.path.basename(file_path))

st.set_page_config(page_title="InstaLink Downloader",
                   page_icon="😍",
                  )

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
              #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
              .block-container {
                    align:center;
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                }
              .stTabs [data-baseweb="tab-list"] {
                gap: 10px;
                }
              .stTabs [data-baseweb="tab"] {
                    font-size:20px;
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
                font-size:1.2rem;
                color: #00FFDD;
                }     
            [data-baseweb="base-input"]{
                 border: 1px solid #555;
                border-radius: 3px ;
                }
        </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: grey;'>Bit Link Downloader</h1>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center; color: #033333;'>Download videos from Instagram, Twitter, X, Terabos, YouTube, and more with our all-in-one solution. Easily save your favorite videos from multiple platforms using just a link.</h6>", unsafe_allow_html=True)
st.subheader('The best place to download video via :blue[link] :sunglasses:')

tab1, tab2, tab4, tab3 = st.tabs([":dancers: Insta", ":bird: tweet", "youtube", " :yum: Other"])

with tab1:
    st.header("Insta Downloader", divider="rainbow")
    st.write("Features of Bit Link downloader Instagram video Downloader: · Instagram video Download Fast, easy and safe. · No need to login to your Instagram account.")
    url = st.text_input("Enter the Instagram Reel URL:")
    if st.button("Fetch"):
        if url and is_instagram_reels_url(url):
            try:
                reel_content = download_reel(url)
                shortcode = url.split("/")[-2]
                file_path = save_reel_content(reel_content, shortcode)
                st.success(f"Reel downloaded successfully! Saved to {file_path}")
                display_media(file_path)
            except Exception as e:
                st.error(f"Failed to download content: {e}")
        else:
            st.error("Please enter a valid Instagram reel URL.")

with tab2:
    st.header("Twitter Downloader", divider="rainbow")

    def download_video(url, file_name) -> None:
        """Download a video from a URL into a filename.

        Args:
            url (str): The video URL to download
            file_name (str): The file name or path to save the video to.
        """
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
        """Extract the highest quality video url to download into a file

        Args:
            url (str): The twitter post URL to download from
        """
        api_url = f"https://twitsave.com/info?url={url}"
        response = requests.get(api_url)
        data = bs4.BeautifulSoup(response.text, "html.parser")
        download_button = data.find_all("div", class_="origin-top-right")[0]
        quality_buttons = download_button.find_all("a")
        highest_quality_url = quality_buttons[0].get("href")  # Highest quality video url
        
        file_name = data.find_all("div", class_="leading-tight")[0].find_all("p", class_="m-2")[0].text  # Video file name
        file_name = re.sub(r"[^a-zA-Z0-9]+", ' ', file_name).strip() + ".mp4"  # Remove special characters from file name
        
        download_video(highest_quality_url, file_name)

    # Streamlit UI
    url = st.text_input("Enter the Twitter Video URL")
    if st.button("Download Video"):
        if url:
            download_twitter_video(url)
        else:
            st.error("Please enter a valid Twitter video URL.")

with tab4:
    # Function to download YouTube video
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

    # Streamlit UI
    st.title('YouTube Video Downloader')

    # Input for YouTube URL
    url = st.text_input('Enter YouTube URL:', '')
    download_type = st.radio('Select Download Type:', ('Video (mp4)', 'Audio (mp3)'))
    # Button to
