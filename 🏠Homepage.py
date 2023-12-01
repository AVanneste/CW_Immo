import pandas as pd
import streamlit as st
from io import BytesIO
import immoweb_scraper
import immoweb_scraper_full
import json
from df_transform import df_transform
import folium
from streamlit_folium import folium_static

#TO DO: PAGES LIMIT 

# Home page display
st.set_page_config(layout="wide", page_title="Immoweb Scraper", page_icon = 'App_Icon.png')

# display of CW logo and center it
col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')
with col2:
    st.image('CW.png', width=300)
with col3:
    st.write(' ')

# Title of the project
st.title('Immoweb Scraper')

#data selection and filters
with open('search_data.json') as json_file:
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

            result = immoweb_scraper.run(sale_rent, property_type, provinces_str, districts_str, zips_str)
            result = result.drop_duplicates(subset='id')
            result.insert(1, 'url', 'https://www.immoweb.be/en/classified/' + result['id'].astype(str))
            result = df_transform(result)
            
            if sale_rent=='for-sale':
                result['MainValue/Surface'] = result['price.mainValue'].astype('Int64')/result['property.netHabitableSurface'].astype('Int64')
            
        st.dataframe(result)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  
            result.to_excel(writer, sheet_name='Results', index=False)
            
        st.download_button(label='📥 Download Search Results',
                                            data=output ,
                                            file_name= 'immoweb.xlsx',
                                            mime="application/vnd.ms-excel")
        print('results length ', len(result))

        with st.spinner('Map Loading...'):
            map_df = result[['property.location.latitude', 'property.location.longitude']]
            map_df = result.loc[result['property.location.latitude'].notna()]
            map_df.rename(columns={'property.location.latitude':'lat', 'property.location.longitude':'lon'}, inplace=True)
            
            def create_map(data):
                m = folium.Map(location=[map_df['lat'].mean(),map_df['lon'].mean()], zoom_start=13)
                for i, row in data.iterrows():
                    folium.Marker([row['lat'], row['lon']], 
                                popup=f"Link: <a href={row['url']} target='_blank'>Immoweb {row['id']}</a> \n Price/Rent: {row['price.mainValue']} \n Surface: {row['property.netHabitableSurface']} \n Address: {row['property.location.street']},{row['property.location.number']} \n {row['property.location.postalCode']},{row['property.location.locality']}",
                                tooltip=f"Price/Rent: {row['price.mainValue']} \n Additional costs: {row['price.additionalValue']} \n Type: {row['property.type']}").add_to(m)

                return m

            
            my_map = create_map(map_df)

        # map_show = st.checkbox('Show map')
        # if map_show:
        
            folium_static(my_map, width=1500, height=800)
    
    if st.button('Full Search (SLOW)'):

        with st.spinner('Wait for it...'):

            result = immoweb_scraper_full.run(sale_rent, property_type, provinces_str, districts_str, zips_str)
            result = result.drop_duplicates(subset='id')
            result.insert(1, 'url', 'https://www.immoweb.be/en/classified/' + result['id'].astype(str))
            # result = df_transform(result)
            
            # if sale_rent=='for-sale':
            #     result['MainValue/Surface'] = result['price.mainValue'].astype('Int64')/result['property.netHabitableSurface'].astype('Int64')
            
        st.dataframe(result)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  
            result.to_excel(writer, sheet_name='Results', index=False)
            
        st.download_button(label='📥 Download Full Search Results',
                                            data=output ,
                                            file_name= 'immoweb_full.xlsx',
                                            mime="application/vnd.ms-excel")

# Hide the footer
hide_default_format = """
       <style>
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)