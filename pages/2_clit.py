import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import json

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Constants
USER_AGENT = "Mozilla/5.0 ..."
BASE_URL = "https://www.clien.net/service/group/allreview"
MAX_REDIRECTS = 10

def clean_title(a_tag):
    """Cleans the title text by removing unwanted elements."""
    for span in a_tag.find_all("span", class_="shortname fixed"):
        span.decompose()
    return ' '.join(a_tag.stripped_strings)

def create_proxy_session():
    """Creates a session with proxy settings."""
    session = requests.Session()
    proxies = {
        'http': st.secrets["proxy"]["http_proxy"],
        'https': st.secrets["proxy"]["https_proxy"]
    }
    session.proxies.update(proxies)
    session.headers.update({'User-Agent': USER_AGENT})
    session.max_redirects = MAX_REDIRECTS
    return session

def fetch_page(session, url):
    """Fetches page content while handling errors."""
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching page: {e}")
        st.error("Failed to retrieve data.")
        return None

def parse_content(html_content):
    """Parses HTML content to extract titles and URLs."""
    soup = BeautifulSoup(html_content, 'html.parser')
    page_title = soup.title.string if soup.title else 'No Title Found'
    titles_and_urls = []

    for div in soup.find_all("div", class_="list_title"):
        a_tag = div.find('a')
        if a_tag:
            title = clean_title(a_tag)
            href = a_tag.get('href')
            full_url = urljoin(BASE_URL, href)
            titles_and_urls.append((title, full_url))

    return page_title, titles_and_urls[2:]

def summarize_content(content, client_id, client_secret):
    """Summarizes content using CLOVA SUMMARY API."""
    contents = []
    summarized_text = ""
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/json"
    }
    

    for i in range(0, len(content), 2000):
        contents.append(content[i:i+2000])
    # print(contents)
    for c in contents:
        print(c)
        data = {
            "document": {"content": c, "title": ""},
            "option": {"language": "ko", "model": "general", "tone": 3, "summaryCount": 3}
        }
        response = requests.post("https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize", headers=headers, data=json.dumps(data))
        print(response)
        summarized_text += response.json()["summary"]
    
    
    return summarized_text if response.status_code == 200 else "Summarization failed."

def inject_custom_css():
    """Injects custom CSS for button styling."""
    st.markdown("""
    <style>
    .stButton>button {...}
    </style>
    """, unsafe_allow_html=True)

def navigation_buttons(page_num):
    """Creates navigation buttons for moving between pages."""
    col1, col2 = st.columns(2)
    with col1:
        if page_num > 1 and st.button('Previous'):
            st.session_state.page_num -= 1
    with col2:
        if st.button('Next'):
            st.session_state.page_num += 1

def display_content(page_title, titles_and_urls):    
    """Displays content with a summarization option, using Streamlit's session state to manage summaries."""
    st.header(page_title)
    for index, (title, link) in enumerate(titles_and_urls):
        st.markdown(f'#### <a href="{link}" target="_blank" style="text-decoration: none; color: inherit;">{title}</a>', unsafe_allow_html=True)
        
        # Unique key for each button based on its index
        summary_key = f"summary_{index}"

        if st.button(f'Summarize "{title}"', key=f"btn_{index}"):
            # Fetch and summarize content only if the button is clicked and summary is not already in session state
            if summary_key not in st.session_state:
                article_response = requests.get(link)
                article_content = article_response.text
                soup = BeautifulSoup(article_content, 'html.parser')
                article_text = " ".join(p.get_text() for p in soup.find_all('p'))
                summary = summarize_content(article_text, st.secrets["naver_ai"]["client_id"], st.secrets["naver_ai"]["client_secret"])
                st.session_state[summary_key] = summary  # Store the summary in session state
            
            # Expand button clicked, display the summary
            st.write(st.session_state[summary_key])
        elif summary_key in st.session_state:
            # If summary is already fetched and stored, display it without needing to click the button again
            st.write(st.session_state[summary_key])
    navigation_buttons(st.session_state['page_num'])


def main():
    """Main function to orchestrate the app, using session state to manage page numbers."""
    st.title('Clien Tracker')
    inject_custom_css()

    if 'page_num' not in st.session_state:
        st.session_state['page_num'] = 1

    page_num = st.session_state['page_num']
    url = f"{BASE_URL}?&po={page_num - 1}"

    session = create_proxy_session()
    html_content = fetch_page(session, url)
    if html_content:
        page_title, titles_and_urls = parse_content(html_content)
        display_content(page_title, titles_and_urls)
        # navigation_buttons(page_num)

if __name__ == "__main__":
    main()
