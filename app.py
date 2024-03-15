import streamlit as st
import requests

# Set page config
st.set_page_config(
    page_icon="🌤️",
    page_title="Weather Dashboard",
    layout="wide",
)

# Cache the API requests to avoid unnecessary calls
@st.cache_data(ttl=600)
def get_weather_data(api_key, city):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # This will raise an exception for non-200 responses
    return response.json()

def display_temperature(temp):
    # Determine the color based on the temperature
    if temp <= 0:
        color = "#3498db"
    elif 0 < temp <= 15:
        color = "#2ecc71"
    elif 15 < temp <= 30:
        color = "#f39c12"
    else:
        color = "#e74c3c"
    
    # Use markdown to display the temperature in large, colored text
    st.markdown(f"<h1 style='text-align: center; color: {color};'>{temp} °C</h1>", unsafe_allow_html=True)

def main():
    st.title('🌤️ Weather Dashboard for Yangju-si')

    # Assuming the API key is stored in Streamlit's secrets
    api_key = st.secrets["temp"]["OPENWEATHER_API_KEY"]
    city = "Yangju-si, KR"

    with st.container():
        if st.button('Check Temperature'):
            try:
                weather_data = get_weather_data(api_key, city)
                temp = weather_data['main']['temp']
                
                # Display the temperature in large, clear text
                display_temperature(temp)

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()