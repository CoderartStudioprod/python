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
    return str(Path.home() / "Downloads")

def download_instagram_content(url):
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
        file_path = os.path.join(media_path, file)
        if file.endswith(('.jpg', '.png')):
            st.image(file_path)
        elif file.endswith('.mp4'):
            st.video(file_path)
        st.download_button(label=f"Download {file}", data=open(file_path, "rb").read(), file_name=file)

def download_video(url, file_name):
    """Download a video from a URL into a filename."""
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
    """Extract the highest quality video URL to download into a file."""
    api_url = f"https://twitsave.com/info?url={url}"
    response = requests.get(api_url)
    data = bs4.BeautifulSoup(response.text, "html.parser")
    download_button = data.find_all("div", class_="origin-top-right")[0]
    quality_buttons = download_button.find_all("a")
    highest_quality_url = quality_buttons[0].get("href")  # Highest quality video URL
    
    file_name = data.find_all("div", class_="leading-tight")[0].find_all("p", class_="m-2")[0].text  # Video file name
    file_name = re.sub(r"[^a-zA-Z0-9]+", ' ', file_name).strip() + ".mp4"  # Remove special characters from file name
    
    download_video(highest_quality_url, file_name)

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

def parse_cookie_file(cookie_file):
    """Parse cookies from a file in Netscape format."""
    cookies = {}
    with open(cookie_file, 'r') as fp:
        for line in fp:
            if not line.startswith('#'):
                line_fields = line.strip().split('\t')
                if len(line_fields) >= 7:
                    cookie_name = line_fields[5]
                    cookie_value = line_fields[6]
                    cookies[cookie_name] = cookie_value
    return cookies

def extract_domain_and_surl(url):
    """Extracts the domain name and 'surl' value from a given URL."""
    parsed_url = urlparse(url)
    domain_name = parsed_url.netloc
    query_params = parse_qs(parsed_url.query)
    surl_value = query_params.get('surl', [''])[0]
    return domain_name, surl_value

def download_dynamic_link(url, max_retries=3, backoff_factor=0.3):
    """Downloads data from a given URL and returns the result."""
    session = requests.Session()
    cookies = parse_cookie_file('cookies.txt')
    session.cookies.update(cookies)

    for attempt in range(max_retries):
        try:
            initial_response = session.get(url, timeout=10)
            domain, key = extract_domain_and_surl(initial_response.url)
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': f'https://{domain}/sharing/link?surl={key}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
            }
            response = session.get(f'https://www.1024tera.com/share/list?app_id=250528&shorturl={key}&root=1', headers=headers, timeout=10)
            result = response.json()['list'][0]['dlink']
            return result
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))
                continue
            else:
                return f"Failed to download data: {e}"

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
    content_type = option_menu(
        menu_title="Select the type of content you want to download:",
        options=["Image", "Video", "Reel", "Post"],
        icons=["image", "image", "film", "list"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "2!important", "align": "center"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {"font-size": "13px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "green"},
        },
    )
    url = st.text_input("Enter the Instagram URL:")
    if st.button("Fetch"):
        if url:
            success
