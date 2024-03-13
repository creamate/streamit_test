from bs4 import BeautifulSoup
import requests
import streamlit as st

def get_page_title_and_divs(url):
    try:
        response = requests.get(url, timeout=5)  # Add timeout for better error handling
        response.raise_for_status()  # Check for HTTP errors
    except requests.RequestException as e:
        return f"Error: {e}", []

    base_url = "https://news.hada.io/"
    soup = BeautifulSoup(response.text, 'html.parser')
    page_title = soup.title.string if soup.title else 'No Title Found'
    titles_urls_descs_and_more = []

    for div in soup.select("div.topictitle"):  # Use CSS selectors for efficiency
        a_tag = div.find('a')
        if a_tag:
            title = a_tag.text.strip()
            href = a_tag.get('href', '#')
            href = href if href.startswith("http") else base_url + href

            description = div.find_next_sibling("div", class_="topicdesc")
            description = description.text.strip() if description else "No description available"

            more_div = div.find_next_sibling("div", class_="topicinfo")
            more_a_tag = more_div.find('a', class_="u") if more_div else None
            href2 = more_a_tag.get('href', '#') if more_a_tag else "#"
            href2 = href2 if href2.startswith("http") else base_url + href2

            titles_urls_descs_and_more.append((title, href, description, href2))

    return page_title, titles_urls_descs_and_more

def main():
    st.title('GeekNews Tracker')

    # Define custom styles for containers
    st.markdown("""
        <style>
            .container {
                border: 2px solid #d3d3d3;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
                box-shadow: 5px 5px 5px #d3d3d3;
            }
        </style>
        """, unsafe_allow_html=True)

    base_url = "https://news.hada.io/new"
    page_num = st.session_state.get('page_num', 1)
    url = f"{base_url}?page={page_num}"
    page_title, titles_urls_descs_and_more = get_page_title_and_divs(url)
    st.header(page_title)

    if titles_urls_descs_and_more:
        for title, link, description, link2 in titles_urls_descs_and_more:
            # Use a container to hold each section
            with st.container():
                col1, col2 = st.columns([3, 1])  # Adjust column ratio as needed
                with col1:
                    st.markdown(f"#### [{title}]({link})", unsafe_allow_html=True)  # Use markdown for clickable links
                with col2:
                    st.markdown(f"[More Info]({link2})", unsafe_allow_html=True)

                st.caption(description)  # Use caption for a more compact presentation
                st.markdown("---")  # Optional: add a divider within the container

    # Dynamic navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if page_num > 1 and st.button('Previous'):
            st.session_state.page_num -= 1
    with col3:
        if st.button('Next'):
            st.session_state.page_num += 1

    if not titles_urls_descs_and_more:
        st.error("No content found or unable to retrieve the website.")



if __name__ == "__main__":
    if 'page_num' not in st.session_state:
        st.session_state.page_num = 1
    main()
