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
from pydub import AudioSegment

# Initialize Instaloader
L = instaloader.Instaloader()

def get_download_path():
    """Return the default downloads path for the current OS."""
    if os.name == 'nt':
        return str(Path.home() / "Downloads")
    else:
        return str(Path.home() / "Downloads")

def download_instagram_content(url, content_type):
    try:
        download_folder = get_download_path()
        shortcode = url.split("/")[-2]
        post = Post.from_shortcode(L.context, shortcode)
        target_folder = os.path.join(download_folder, f"Instagram_{shortcode}")
        os.makedirs(target_folder, exist_ok=True)
        
        # Change working directory to target folder to download files there
        os.chdir(target_folder)
        L.download_post(post, target=target_folder)
        
        # Revert working directory
        os.chdir(download_folder)
        
        return True, target_folder
    except Exception as e:
        return False, str(e)

def display_media(media_path):
    media_files = os.listdir(media_path)
    for file in media_files:
        if file.endswith(('.jpg', '.png')):
            st.image(f"{media_path}/{file}")
        elif file.endswith('.mp4'):
            st.video(f"{media_path}/{file}")

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
    content_type = option_menu(
        menu_title="Select the type of content you want to download:",  # required
        options=["Image", "Video", "Reel", "Post"],  # required
        icons=["image", "image", "film", "list"],  # optional, add icons to the options
        menu_icon="cast",  # optional, the icon next to the menu title
        default_index=0,  # optional, the index of the default selected option
        orientation="horizontal",  # optional, can be "horizontal" or "vertical"
        styles={
            "container": {"padding": "2!important", "align": "center"},
            "icon": {"color": "orange", "font-size": "25px"},  # icon style
            "nav-link": {"font-size": "13px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "green"},
        },
    )
    # URL input field
    url = st.text_input("Enter the Instagram URL:")
    if st.button("Fetch"):
        if url:
            success, media_path = download_instagram_content(url, content_type)
            if success:
                st.success(f"Content downloaded successfully! Saved to {media_path}")
                if st.button("Show Preview"):
                    display_media(media_path)
                # Provide download link for mobile compatibility
                for file in os.listdir(media_path):
                    file_path = os.path.join(media_path, file)
                    with open(file_path, "rb") as f:
                        st.download_button(label="Download", data=f, file_name=file, mime="application/octet-stream")
            else:
                st.error(f"Failed to download content: {media_path}")
        else:
            st.error("Please enter a valid URL.")

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
