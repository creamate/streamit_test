import streamlit as st
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin

def get_page_title_and_divs(session, url):
    try:
        headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
        response = session.get(url,headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX, 5XX)

        soup = BeautifulSoup(response.text, 'html.parser')
        page_title = soup.title.string if soup.title else 'No Title Found'
        titles_and_urls = extract_titles_and_urls(soup)
        
        return page_title, titles_and_urls[2:]  # Skip the first two titles for some reason
    except (requests.exceptions.HTTPError, requests.exceptions.TooManyRedirects, requests.exceptions.RequestException) as e:
        st.error(f"Error retrieving data: {e}")
        return "Error: Could not retrieve the website", []

def extract_titles_and_urls(soup):
    titles_and_urls = []
    base_url = "https://www.clien.net"

    for div in soup.find_all("div", class_="list_title"):
        a_tag = div.find('a')
        if a_tag:
            clean_title = clean_title_element(a_tag)
            href = a_tag.get('href')
            full_url = urljoin(base_url, href)
            titles_and_urls.append((clean_title, full_url))
            
    return titles_and_urls

def clean_title_element(a_tag):
    for span in a_tag.find_all("span", class_="shortname fixed"):
        span.decompose()
    cleaned_title = ''.join(str(item) if not isinstance(item, NavigableString) else item for item in a_tag.contents).strip()
    return cleaned_title

def main():
    st.title('Clien Tracker')
    inject_custom_css()
    base_url = "https://www.clien.net/service/group/allreview"
    page_num = st.session_state.get('page_num', 1)
    url = f"{base_url}?&po={page_num - 1}"

    with requests.Session() as session:
        session.max_redirects = 5  # Set the maximum number of redirects
        page_title, titles_and_urls = get_page_title_and_divs(session, url)
        display_content(page_title, titles_and_urls)
        navigation_buttons(page_num)

def inject_custom_css():
    st.markdown("""
    <style>
    .stButton>button {
        font-size: 18px;
        border: 2px solid #4CAF50;
        border-radius: 5px;
        background-color: #4CAF50;
        color: white;
        padding: 15px 40px;
        cursor: pointer;
        margin: 10px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

def display_content(page_title, titles_and_urls):
    st.header(f"{page_title}")
    if titles_and_urls:
        for title, link in titles_and_urls:
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration: none; color: inherit;">{title}</a>', unsafe_allow_html=True)
    else:
        st.write("No content found or unable to retrieve the website.")

def navigation_buttons(page_num):
    col1, col2 = st.columns(2)
    with col1:
        if page_num > 1 and st.button('Previous'):
            st.session_state.page_num -= 1
            st.rerun()
    with col2:
        if st.button('Next'):
            st.session_state.page_num += 1
            st.rerun()

if __name__ == "__main__":
    if 'page_num' not in st.session_state:
        st.session_state.page_num = 1
    main()