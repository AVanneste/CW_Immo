import pandas as pd
import streamlit as st
from io import BytesIO
# import scripts.athome_scraper_full
import scripts.athome_scraper
import json
from scripts.df_transform import transform_athome
from scripts.create_map import create_map_athome
import folium
from streamlit_folium import folium_static

#TO DO: clean columns in results dfs
# Add added dates

# Home page display
st.set_page_config(layout="wide", page_title="atHome Scraper", page_icon = 'data/CW_icon.png')

# display of CW logo and center it
col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')
with col2:
    st.image('data/CW_banner1.png', width=600)
    st.image('data/under_maint.png', width=600)
with col3:
    st.write(' ')

# Title of the project
st.title('atHome Scraper')

# #data selection and filters
# with open('data/search_data_athome.json') as json_file:
#     search_data = json.load(json_file)

# #select boxes and display
# sale_rent = st.selectbox('Sale or Rent?', ['Sale', 'Rent'], index=None, placeholder='Select For Sale or For Rent option')

# if sale_rent:
#     property_type_list = st.multiselect('Which type(s) of property are you looking for?', search_data['property_types'].keys(), placeholder='Select multiple, leave empty if you want to search everything')
#     property_type_list = [search_data['property_types'][x] for x in property_type_list]
#     if not property_type_list:
#         property_type_str = '' #list(search_data['property_types'].values())
#     else:
#         property_type_str = ','.join(property_type_list)

#     st.markdown('Where do you want to search?')
#     zones = st.multiselect('Zone', options=list(search_data['zones'].keys()), placeholder='Select multiple, leave empty if you want to search the whole country')
#     zones = [search_data['zones'][x] for x in zones]
    
#     if not zones:
#         zone_str = 'faee1a4a'
#     else:
#         zone_str = ','.join(zones)

#     # Process and save results
#     if st.button('Search'):

#         with st.spinner('Wait for it...'):

#             result = scripts.athome_scraper.run(search_data['sale_rent'][sale_rent], property_type_str, zone_str)
#             if result.empty:
#                 st.markdown('No results found')
#             else:
#                 result = transform_athome(result)

#                 st.dataframe(result, column_config={"url": st.column_config.LinkColumn("url")})
                
#                 output = BytesIO()
#                 with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#                     result.to_excel(writer, sheet_name='Results', index=False)
                    
#                 st.download_button(label='📥 Download Search Results',
#                                                     data=output ,
#                                                     file_name= 'athome.xlsx',
#                                                     mime="application/vnd.ms-excel")

#                 with st.spinner('Map Loading...'):

#                     my_map = create_map_athome(result)

#                 # map_show = st.checkbox('Show map')
#                 # if map_show:
#                     try:
#                         folium_static(my_map, width=1500, height=800)
#                     except:
#                         st.markdown('No result to show on map')
    
    # if st.button('Full Search (VERY SLOW)'):

    #     with st.spinner('Wait for it...'):

    #         result = scripts.athome_scraper_full.run(search_data['sale_rent'][sale_rent], property_type, zone)
    #         if result.empty:
    #             st.markdown('No results found')
    #         else:
    #             result = transform_athome(result)
                
    #             st.dataframe(result, column_config={"url": st.column_config.LinkColumn("url")})
                
    #             output = BytesIO()
    #             with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    #                 result.to_excel(writer, sheet_name='Results', index=False)
                    
    #             st.download_button(label='📥 Download Full Search Results',
    #                                                 data=output ,
    #                                                 file_name= 'athome_full.xlsx',
    #                                                 mime="application/vnd.ms-excel")
                
    #             with st.spinner('Map Loading...'):
    #                 my_map = create_map_athome(result)

    #             # map_show = st.checkbox('Show map')
    #             # if map_show:
    #                 try:
    #                     folium_static(my_map, width=1500, height=800)
    #                 except:
    #                     st.markdown('No result to show on map')

# Hide the footer
hide_default_format = """
       <style>
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)