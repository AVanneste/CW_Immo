import hmac
import streamlit as st
from pathlib import Path
import pandas as pd
from io import BytesIO
from scripts.geocode import geocode_urls

# display of CW logo and center it
col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')
with col2:
    st.image('data/CW_banner1.png', width=600)
with col3:
    st.write(' ')


def check_password(col=col2):
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    with col:
        # Show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        if "password_correct" in st.session_state:
            st.error("😕 Password incorrect")
        return False

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Main Streamlit app starts here
uploaded_file = st.file_uploader("Upload a CSV or XLSX file", type=["xlsx", "csv"])
st.write("Note: the geocoded GPS coordinates will be added to 'Latitude' and 'Longitude' columns. Those columns will be created if they don't exist already")
st.write("Existing coordinates won't be replaced, only empty values will be geocoded")

if uploaded_file is not None:
    st.write(uploaded_file.name)
    file_ext = Path(uploaded_file.name).suffix
    # st.write(f"File extension: {file_ext}")
    # st.write(file_ext)
    try:
        if file_ext == '.csv':
            df = pd.read_csv(uploaded_file,dtype=str)
        elif file_ext == '.xlsx':
            df = pd.read_excel(uploaded_file,dtype=str)
        st.write('Data uploaded successfully. These are the first 5 rows.')
        st.dataframe(df.head(5))

    except Exception as e:
        st.write(e)

    address_cols = st.multiselect('Which column(s) in your dataset are (part of) the address?', list(df.columns))
    
    country = st.text_input("[Optional] Enter the country here if you want to add it in the search (and if it's the same for all addresses)", "")
    
    api_url = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    
    if address_cols:
        df['URL'] = api_url
        for c in address_cols:
            df['URL'] += ' ' + df[c].astype(str)
        if country:
            df['URL'] += ' ' + country
        df['URL'] += f"&key={st.secrets['api_key_cw']}"
        
        search = st.button("Start Geocoding")
        
        if search:
            with st.spinner('Loading...'):
                geocoded_df = geocode_urls(df, url_column='URL', lat_column='Latitude', lng_column='Longitude')
                geocoded_df = geocoded_df.drop('URL', axis=1)
                
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  
                    geocoded_df.to_excel(writer, sheet_name='Geocoded Results', index=False)
                    
                st.download_button(label='📥 Download Geocoded Results',
                                                    data=output ,
                                                    file_name= uploaded_file.name.replace(file_ext, "")+ '_geocoded.xlsx',
                                                    mime="application/vnd.ms-excel")