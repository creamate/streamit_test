import streamlit as st
import requests
from bs4 import BeautifulSoup

def get_page_title_and_divs(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        page_title = soup.title.string if soup.title else 'No Title Found'
        titles_urls_and_descs = []

        for div in soup.find_all("div", class_="topictitle"):
            a_tag = div.find('a')
            if a_tag:
                title = a_tag.text.strip()
                href = a_tag.get('href')
                full_url = f"https://news.hada.io/new{href}" if href.startswith('/') else href
                
                desc_div = div.find_next_sibling("div", class_="topicdesc")
                description = desc_div.text.strip() if desc_div else "No description available"
                
                titles_urls_and_descs.append((title, full_url, description))
                
        return page_title, titles_urls_and_descs 
    else:
        return "Error: Could not retrieve the website", []

def main():
    st.title('GeekNews Tracker')
    
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

    base_url = "https://news.hada.io/new"
    page_num = st.session_state.get('page_num', 1)
    
    # Update URL to use 'page' query parameter for pagination
    url = f"{base_url}?page={page_num}"

    page_title, titles_urls_and_descs = get_page_title_and_divs(url)

    st.header(f"{page_title}")

    if titles_urls_and_descs:
        for title, link, description in titles_urls_and_descs:
            st.markdown(f"""
            <div>
                <a href="{link}" target="_blank" style="font-size: 20px; text-decoration: none; color: inherit;">{title}</a>
                <div style="font-size: 16px; color: grey;">{description}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if page_num > 1 and st.button('Previous'):
            st.session_state.page_num -= 1
            st.experimental_rerun()
    with col2:
        if st.button('Next'):
            st.session_state.page_num += 1
            st.experimental_rerun()

    if not titles_urls_and_descs:
        st.write("No content found or unable to retrieve the website.")

if __name__ == "__main__":
    if 'page_num' not in st.session_state:
        st.session_state.page_num = 1
    main()
