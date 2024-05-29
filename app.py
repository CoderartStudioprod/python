import instaloader
import streamlit as st
from instaloader import Post
import os
from urllib.parse import urlparse, parse_qs
import requests
import time
from streamlit_option_menu import option_menu
import re
import requests
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



st.set_page_config(page_title="Bit Link Downloader",
                    page_icon="😍",
                    )
# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
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
                    font-size:20px
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
        """, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: grey;'>Bit Link Downloader</h1>", unsafe_allow_html=True, )
st.markdown("<h6 style='text-align: center; color: #033333;'>Download videos from Instagram, Twitter, X, Terabos, YouTube, and more with our all-in-one solution. Easily save your favorite videos from multiple platforms using just a link.<h6>", unsafe_allow_html=True,)
st.subheader('The best place to download video via :blue[link] :sunglasses:')
tab1, tab2, tab4, tab3 = st.tabs([":dancers: Insta", ":bird: tweet","youtube"," :yum: Other"])



with tab1:
    st.header("Insta Downloader",divider="rainbow")
    st.write("Features of Bit Link downloader Instagram video Downloader: · Instagram video Download Fast, easy and safe. · No need to login to your Instagram account.")
    content_type = option_menu(
    menu_title="Select the type of content you want to download:",  # required
    options=["Image", "Video", "Reel", "Post"],  # required
    icons=["image", "image", "film", "list"],  # optional, add icons to the options
    menu_icon="cast",  # optional, the icon next to the menu title
    default_index=0,  # optional, the index of the default selected option
    orientation="horizontal",  # optional, can be "horizontal" or "vertical"
    styles={
        "container": {"padding": "2!important","align":"center"},
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
            else:
                st.error(f"Failed to download content: {media_path}")
        else:
            st.error("Please enter a valid URL.")




with tab2:
    st.header("Tweter Downloader",divider="rainbow")
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
    if st.button("Download vedio"):
        if url:
            download_twitter_video(url)
        else:
            st.error("Please enter a valid Twetter video URL.")

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
    # Button to download video
    if st.button('YT Download'):
       if url:
        st.write('Downloading...')
        file_path = download_youtube_video(url, download_type)
        if os.path.exists(file_path):
            st.success('Download completed!')
            file_name = os.path.basename(file_path)
            mime_type = 'video/mp4' if download_type == 'Video (mp4)' else 'audio/mp3'
            with open(file_path, 'rb') as file:
                btn = st.download_button(
                    label='Download File',
                    data=file,
                    file_name=file_name,
                    mime=mime_type
                )
        else:
            st.error(f'Error: {file_path}')
    else:
        st.error('Please enter a valid YouTube URL.')
with tab3:
    images = ["https://m.media-amazon.com/images/I/21M-N-rhZyL.jpg","https://img.freepik.com/premium-photo/youtube-logo-video-player-3d-design-video-media-player-interface_41204-12379.jpg","https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/LinkedIn_Logo.svg/1280px-LinkedIn_Logo.svg.png"]
    st.header("Dynamic Link Downloader",divider="rainbow")
 
    st.image(images,width=60,use_column_width=60,clamp="true")

    def parse_cookie_file(cookie_file):
        """
        Parse cookies from a file in Netscape format.

        Args:
            cookie_file (str): Path to the cookies file.

        Returns:
            dict: A dictionary containing cookies as key-value pairs.
        """
        cookies = {}
        with open(cookie_file, 'r') as fp:
            for line in fp:
                if not line.startswith('#'):
                    line_fields = line.strip().split('\t')
                    # Make sure the line has at least 7 fields, as per Netscape format
                    if len(line_fields) >= 7:
                        cookie_name = line_fields[5]
                        cookie_value = line_fields[6]
                        cookies[cookie_name] = cookie_value
        return cookies


    def extract_domain_and_surl(url):
        """
        Extracts the domain name and 'surl' value from a given URL.

        Args:
            url (str): The URL to extract domain name and 'surl' value from.

        Returns:
            tuple: A tuple containing the domain name and 'surl' value as (domain_name, surl_value).
        """
        parsed_url = urlparse(url)
        domain_name = parsed_url.netloc
        query_params = parse_qs(parsed_url.query)
        surl_value = query_params.get('surl', [''])[0]
        return domain_name, surl_value

    def download(url: str, max_retries: int = 3, backoff_factor: float = 0.3) -> str:
        
        """
        Downloads data from a given URL and returns the result.

        Args:
            url (str): The URL to download data from.
            max_retries (int): Maximum number of retries for connection errors.
            backoff_factor (float): Backoff factor for retry delays.

        Returns:
            str: The downloaded data or an error message.
        """
        session = requests.Session()

        # Load cookies from 'cookies.txt'
        cookies = parse_cookie_file('cookies.txt')
        session.cookies.update(cookies)

        for attempt in range(max_retries):
            try:
                # Get the response from the initial URL
                initial_response = session.get(url, timeout=10)
                domain, key = extract_domain_and_surl(initial_response.url)
                st.toast(domain + key)
                # Prepare headers for the next request
                headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': f'https://{domain}/sharing/link?surl={key}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
                }

                # Request the download link
                response = session.get(
                    f'https://www.1024tera.com/share/list?app_id=250528&shorturl={key}&root=1', headers=headers, timeout=10)

                try:
                    result = response.json()['list'][0]['dlink']
                except (KeyError, IndexError) as e:
                    return f"Failed to get download link: {e}"
                else:
                    return result

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor * (2 ** attempt)
                    time.sleep(sleep_time)
                    continue
                else:
                    return f"Failed to download data: {e}"
    url_input = st.text_input("Enter the URL:")
    if st.button("Download"):
        if url_input:
            download_link = download(url_input)
            st.write(f"Download link: {download_link}")
        else:
            st.write("Please enter a URL.")






# Streamlit UI




     



