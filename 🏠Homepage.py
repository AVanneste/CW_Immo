import pandas as pd
import streamlit as st
from io import BytesIO
import scripts.immoweb_scraper
import scripts.immoweb_scraper_full
import json
from scripts.df_transform import df_transform, new_cols
from scripts.create_map import create_map
from streamlit_folium import folium_static
from streamlit_sortables import sort_items

# Home page display
st.set_page_config(layout="wide", page_title="Immoweb Scraper", page_icon = 'data/CW_icon.png')

if "search_click" not in st.session_state:
    st.session_state['search_click'] = {'normal': False, 'full': False}
    st.session_state['original_dataframe'] = pd.DataFrame()
    st.session_state['dataframe'] = pd.DataFrame()
    st.session_state['columns'] = []

# display of CW logo and center it
col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')
with col2:
    st.image('data/CW_banner1.png', width=600)
with col3:
    st.write(' ')

# Title of the project
st.title('Immoweb Scraper')

#data selection and filters
with open('data/search_data.json') as json_file:
    search_data = json.load(json_file)

def format_func(option):
    return search_data['search_fields'][option]

def reset_state(button1, button2):
    st.session_state['search_click'][button1] = True
    st.session_state['search_click'][button2] = False
    st.session_state['original_dataframe'] = pd.DataFrame()
    st.session_state['dataframe'] = pd.DataFrame()
    st.session_state['columns'] = []

#select boxes and display
sale_rent = st.selectbox('Buy or Rent?', ['for-sale', 'for-rent'], index=None, placeholder='Select For Sale or For Rent option')

if sale_rent:
    if sale_rent == 'for-rent':
        property_type = st.multiselect('Which type(s) of property for rent are you looking for? (leave empty if you want everything)', search_data['property_types_rent'])
    else:
        property_type = st.multiselect('Which type(s) of property for sale are you looking for? (leave empty if you want everything)', search_data['property_types_sale'])
    
    st.markdown('Where do you want to search?')
    zips = st.multiselect('Which zip code(s) or localitie(s) do you want to search?', options=list(search_data['search_fields'].keys()), format_func=lambda x: search_data['search_fields'].get(x))
    districts = st.multiselect('Which district(s) do you want to search?', sorted(search_data['districts']))
    provinces = st.multiselect('Which province(s)/region do you want to search?', sorted(search_data['provinces']))

    if not property_type:
        if sale_rent == 'for-rent':
            property_type = search_data['property_types_rent']
        else:
            property_type = search_data['property_types_sale']

    zips_str = ','.join(zips)
    provinces_str = ','.join(provinces)
    districts_str = ','.join((districts))

    # Process and save results
    st.button('Search', on_click=reset_state, args=['normal', 'full'])
    
    if st.session_state['search_click']['normal'] == True:
        if st.session_state['original_dataframe'].empty:
            with st.spinner('Wait for it...'):

                result = scripts.immoweb_scraper.run(sale_rent, property_type, provinces_str, districts_str, zips_str)
                if result.empty:
                    st.markdown('No results found')
                else:
                    result = new_cols(result)
                    result = df_transform(result)
                    
                    st.session_state['original_dataframe'] = result
        
        st.session_state['columns'] = list(st.session_state['original_dataframe'].columns)
        
        original_items = [{'header': 'Pick your columns and their order (drag and drop)',  'items': []}, {'header': 'Original columns', 'items': st.session_state['columns']}]
        
        sorted_items = sort_items(original_items, multi_containers=True)

        if sorted_items[0]['items'] == []:
            st.session_state['dataframe'] = st.session_state['original_dataframe'][sorted_items[1]['items']]
        else:
            st.session_state['dataframe'] = st.session_state['original_dataframe'][sorted_items[0]['items']]
        
        st.dataframe(st.session_state['dataframe'], column_config={"url": st.column_config.LinkColumn("url")})
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            st.session_state['dataframe'].to_excel(writer, sheet_name='Results', index=False)
            
        st.download_button(label='📥 Download Search Results',
                                            data=output ,
                                            file_name= 'immoweb.xlsx',
                                            mime="application/vnd.ms-excel")

        with st.spinner('Map Loading...'):

            my_map = create_map(st.session_state['original_dataframe'])
    
    st.button('Full Search (SLOW)', on_click=reset_state, args=['full', 'normal'])

    if st.session_state['search_click']['full'] == True:
        if st.session_state['original_dataframe'].empty:
            with st.spinner('Wait for it...'):

                result = scripts.immoweb_scraper_full.run(sale_rent, property_type, provinces_str, districts_str, zips_str)
                if result.empty:
                    st.markdown('No results found')
                else:
                    result = new_cols(result)

                    st.session_state['original_dataframe'] = result
        
        st.session_state['columns'] = list(st.session_state['original_dataframe'].columns)
        
        original_items = [{'header': 'Pick your columns and their order (drag and drop)',  'items': []}, {'header': 'Original columns', 'items': st.session_state['columns']}]
        
        sorted_items = sort_items(original_items, multi_containers=True)

        if sorted_items[0]['items'] == []:
            st.session_state['dataframe'] = st.session_state['original_dataframe'][sorted_items[1]['items']]
        else:
            st.session_state['dataframe'] = st.session_state['original_dataframe'][sorted_items[0]['items']]
        
        st.dataframe(st.session_state['dataframe'], column_config={"url": st.column_config.LinkColumn("url")})
                    
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  
            st.session_state['dataframe'].to_excel(writer, sheet_name='Results', index=False)
            
        st.download_button(label='📥 Download Full Search Results',
                                            data=output ,
                                            file_name= 'immoweb_full.xlsx',
                                            mime="application/vnd.ms-excel")
                    
        with st.spinner('Map Loading...'):
            my_map = create_map(st.session_state['original_dataframe'])

    if st.checkbox('Show map'):
    # if map_show:
        try:
            folium_static(my_map, width=1500, height=800)
        except:
            st.markdown('No result to show on map')

# Hide the footer
hide_default_format = """
       <style>
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)