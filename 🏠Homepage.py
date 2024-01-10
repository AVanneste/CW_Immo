import pandas as pd
import streamlit as st
from io import BytesIO
import scripts.immoweb_scraper
import scripts.immoweb_scraper_full
import json
from scripts.df_transform import df_transform, new_cols, annechien_results
from scripts.create_map import create_map
import folium
from streamlit_folium import folium_static

#TO DO: PAGES LIMIT 

# Home page display
st.set_page_config(layout="wide", page_title="Immoweb Scraper", page_icon = 'data/CW_icon.png')

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
    
    # localities = st.multiselect('Which locality.ies do you want to search?', dict_bel['Locality_Name_FR'] + dict_bel['Locality_Name_NL'])
    # communes = st.multiselect('Which commune(s) do you want to search?', dict_bel['Commune'])
    # arrondissements = st.multiselect('Which arrondissement(s) do you want to search?', dict_bel['Arrondissement'])
    # regions = st.multiselect('Which region(s) do you want to search?', region_list)

    if not property_type:
        if sale_rent == 'for-rent':
            property_type = search_data['property_types_rent']
        else:
            property_type = search_data['property_types_sale']

    zips_str = ','.join(zips)
    provinces_str = ','.join(provinces)
    districts_str = ','.join((districts))

    # Process and save results
    if st.button('Search'):

        with st.spinner('Wait for it...'):

            result = scripts.immoweb_scraper.run(sale_rent, property_type, provinces_str, districts_str, zips_str)
            if result.empty:
                st.markdown('No results found')
            else:
                result = new_cols(result)
                result = df_transform(result)

                st.dataframe(result, column_config={"url": st.column_config.LinkColumn("url")})
                
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    result.to_excel(writer, sheet_name='Results', index=False)
                    
                st.download_button(label='📥 Download Search Results',
                                                    data=output ,
                                                    file_name= 'immoweb.xlsx',
                                                    mime="application/vnd.ms-excel")

                with st.spinner('Map Loading...'):

                    my_map = create_map(result)

                # map_show = st.checkbox('Show map')
                # if map_show:
                    try:
                        folium_static(my_map, width=1500, height=800)
                    except:
                        st.markdown('No result to show on map')
    
    if st.button('Full Search (SLOW)'):

        with st.spinner('Wait for it...'):

            result = scripts.immoweb_scraper_full.run(sale_rent, property_type, provinces_str, districts_str, zips_str)
            if result.empty:
                st.markdown('No results found')
            else:
                result = new_cols(result)
                # result_annechien = result[['url', 'property.bedroomCount', 'property.location.locality', 'property.location.postalCode', 'property.location.street', 'property.location.number', 'property.location.floor',
                #                            'property.netHabitableSurface', 'property.building.condition', 'property.terraceSurface', 'transaction.certificates.epcScore', 'transaction.rental.monthlyRentalPrice']]
                result_annechien = annechien_results(result)
                st.dataframe(result, column_config={"url": st.column_config.LinkColumn("url")})
                st.markdown('Annechien Dataframe:')
                st.dataframe(result_annechien, column_config={"url": st.column_config.LinkColumn("url")})
                
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  
                    result.to_excel(writer, sheet_name='Results', index=False)
                    
                st.download_button(label='📥 Download Full Search Results',
                                                    data=output ,
                                                    file_name= 'immoweb_full.xlsx',
                                                    mime="application/vnd.ms-excel")
                
                output_annechien = BytesIO()
                with pd.ExcelWriter(output_annechien, engine='xlsxwriter') as writer_a:  
                    result_annechien.to_excel(writer_a, sheet_name='Results', index=False)
                    
                st.download_button(label='📥 Download Annechien Search Results',
                                                    data=output_annechien ,
                                                    file_name= 'immoweb_annechien.xlsx',
                                                    mime="application/vnd.ms-excel")
                
                with st.spinner('Map Loading...'):
                    my_map = create_map(result)

                # map_show = st.checkbox('Show map')
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