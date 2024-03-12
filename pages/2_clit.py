import streamlit as st
import requests
from bs4 import BeautifulSoup, NavigableString

def get_page_title_and_divs(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        page_title = soup.title.string if soup.title else 'No Title Found'
        titles_and_urls = []

        for div in soup.find_all("div", class_="list_title"):
            a_tag = div.find('a')
            if a_tag:
                # Remove or ignore <span class="shortname fixed">
                for span in a_tag.find_all("span", class_="shortname fixed"):
                    span.decompose()  # This removes the span element from the tree

                # After removing the spans, extract the cleaned title
                title = ''.join([str(item) if not isinstance(item, NavigableString) else item for item in a_tag.contents]).strip()
                href = a_tag.get('href')
                full_url = f"https://www.clien.net{href}" if href.startswith('/') else href
                titles_and_urls.append((title, full_url))
                
        return page_title, titles_and_urls[2:]  # Skip the first two titles
    else:
        return "Error: Could not retrieve the website", []

def main():
    st.title('Clien Tracker')

    # Inject Custom CSS for button styling
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

    base_url = "https://www.clien.net/service/group/allreview"
    page_num = st.session_state.get('page_num', 1)
    
    url = f"{base_url}?&po={page_num - 1}"

    page_title, titles_and_urls = get_page_title_and_divs(url)

    st.header(f"{page_title}")

    if titles_and_urls:
        for title, link in titles_and_urls:
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration: none; color: inherit;">{title}', unsafe_allow_html=True)
    
    # Navigation buttons with custom styling applied globally
    col1, col2 = st.columns(2)
    with col1:
        if page_num > 1 and st.button('Previous'):
            st.session_state.page_num -= 1
            st.experimental_rerun()
    with col2:
        if st.button('Next'):
            st.session_state.page_num += 1
            st.experimental_rerun()

    if not titles_and_urls:
        st.write("No content found or unable to retrieve the website.")

if __name__ == "__main__":
    if 'page_num' not in st.session_state:
        st.session_state.page_num = 1
    main()
