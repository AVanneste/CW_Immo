import pandas as pd
import streamlit as st
from io import BytesIO
# import pages.immotop_scraper
import scripts.immotop_scraper_full
import scripts.immotop_scraper
import json
from scripts.df_transform import transform_immotop
from scripts.create_map import create_map_immotop
import folium
from streamlit_folium import folium_static
from streamlit_sortables import sort_items

#TO DO: clean columns in results dfs
# Add added dates

# Home page display
st.set_page_config(layout="wide", page_title="Immotop Scraper", page_icon = 'data/CW_icon.png')

if "search_click" not in st.session_state:
    st.session_state['search_click'] = {'normal': False, 'full': False}
    st.session_state['original_dataframe'] = pd.DataFrame()
    st.session_state['dataframe'] = pd.DataFrame()
    st.session_state['columns'] = []

def reset_state(button1, button2):
    st.session_state['search_click'][button1] = True
    st.session_state['search_click'][button2] = False
    st.session_state['original_dataframe'] = pd.DataFrame()
    st.session_state['dataframe'] = pd.DataFrame()
    st.session_state['columns'] = []

# display of CW logo and center it
col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')
with col2:
    st.image('data/CW_banner1.png', width=600)
    # st.image('data/under_maint.jpg', width=600)
with col3:
    st.write(' ')

# Title of the project
st.title('Immotop Scraper')

#data selection and filters
with open('data/search_data_immotop.json') as json_file:
    search_data = json.load(json_file)

#select boxes and display
sale_rent = st.selectbox('Sale or Rent?', ['Sale', 'Rent'], index=None, placeholder='Select For Sale or For Rent option')

if sale_rent:
    if sale_rent == 'Rent':
        property_type = st.multiselect('Which type(s) of property for rent are you looking for?', search_data['property_types_rent'].keys(), placeholder='Select multiple, leave empty if you want everything')
        property_type = [search_data['property_types_rent'][x] for x in property_type]
    else:
        property_type = st.multiselect('Which type(s) of property for sale are you looking for?', search_data['property_types_sale'].keys(), placeholder='Select multiple, leave empty if you want everything')
        property_type = [search_data['property_types_sale'][x] for x in property_type]
    
    st.markdown('Where do you want to search?')
    zone = st.selectbox('Zone', options=list(search_data['zones'].keys()))
    zone = search_data['zones'][zone]
    
    if not property_type:
        if sale_rent == 'Rent':
            property_type = list(search_data['property_types_rent'].values())
        else:
            property_type = list(search_data['property_types_sale'].values())

    # Process and save results
    st.button('Search', on_click=reset_state, args=['normal', 'full'])
    
    if st.session_state['search_click']['normal'] == True:
        if st.session_state['original_dataframe'].empty:
            with st.spinner('Wait for it...'):

                result = scripts.immotop_scraper.run(search_data['sale_rent'][sale_rent], property_type, zone)
                if result.empty:
                    st.markdown('No results found')
                else:
                    result = transform_immotop(result)
                    
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
                                            file_name= 'immotop.xlsx',
                                            mime="application/vnd.ms-excel")

        with st.spinner('Map Loading...'):
            my_map = create_map_immotop(st.session_state['original_dataframe'])
    
    st.button('Full Search (VERY SLOW)', on_click=reset_state, args=['full', 'normal'])

    if st.session_state['search_click']['full'] == True:
        if st.session_state['original_dataframe'].empty:
            with st.spinner('Wait for it...'):

                result = scripts.immotop_scraper_full.run(search_data['sale_rent'][sale_rent], property_type, zone)
                if result.empty:
                    st.markdown('No results found')
                else:
                    result = transform_immotop(result)
                    # print(result.columns)
                    # colz = list(result.columns)
                    # newlist = [] # empty list to hold unique elements from the list
                    # duplist = [] # empty list to hold the duplicate elements from the list
                    # for i in colz:
                    #     if i not in newlist:
                    #         newlist.append(i)
                    #     else:
                    #         duplist.append(i)
                    # print(duplist)
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
                                            file_name= 'immotop_full.xlsx',
                                            mime="application/vnd.ms-excel")
        
        with st.spinner('Map Loading...'):
            my_map = create_map_immotop(st.session_state['original_dataframe'])

    if st.checkbox('Show map'):
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