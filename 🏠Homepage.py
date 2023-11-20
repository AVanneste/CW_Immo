import pandas as pd
import streamlit as st
from io import BytesIO
import immoweb_scraper
import immoweb_scraper_copy
from df_transform import df_transform

#TO DO: PAGES LIMIT 

# Home page display

st.set_page_config(layout="wide", page_title="Immoweb Scraper", page_icon = 'App_Icon.png')


# display of BeCode logo and center it (thus the colummns thing)
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

df_bel = pd.read_excel('Division geographique.xlsx')
df_bel = df_bel[['ZIP_code', 'Locality_Name_NL', 'Locality_Name_FR', 'District_Name_NL', 
                 'District_Name_FR', 'Region_Name_NL', 'Region_Name_FR', 'Arrondissement', 'Commune']]

df_bel['Commune'] = df_bel['Commune'] + '(Commune)'
df_bel['ZIP_code'] = df_bel['ZIP_code'].astype(str)

property_types_rent = ['apartment', 'house', 'garage', 'office', 'business', 'industry', 'land', 'other']
property_types_sale = ['apartment', 'house', 'new-real-estate-projects', 'garage', 'office', 'business', 'industry', 'land', 'tenement', 'other']

province_list = ['LIEGE','HAINAUT','LUXEMBOURG','FLEMISH_BRABANT','WALLOON_BRABANT','EAST_FLANDERS','WEST_FLANDERS','LIMBURG','ANTWERP']

dict_bel = {}
for column in df_bel.columns.to_list():
    values = sorted(list(df_bel[column].unique()))
    dict_bel[column] = values


#select boxes and display
sale_rent = st.selectbox('Buy or Rent?', ['for-sale', 'for-rent'], index=None, placeholder='Select For Sale or For Rent option')

if sale_rent:
    if sale_rent == 'for-rent':
        property_type = st.multiselect('Which type(s) of property for rent are you looking for? (leave empty if you want everything)', property_types_rent)
    else:
        property_type = st.multiselect('Which type(s) of property for sale are you looking for? (leave empty if you want everything)', property_types_sale)
    
    st.markdown('Where do you want to search?')
    zips = st.multiselect('Which zip code(s) do you want to search?', dict_bel['ZIP_code'])
    # localities = st.multiselect('Which locality.ies do you want to search?', dict_bel['Locality_Name_FR'] + dict_bel['Locality_Name_NL'])
    # communes = st.multiselect('Which commune(s) do you want to search?', dict_bel['Commune'])
    # districts = st.multiselect('Which district(s) do you want to search?', dict_bel['District_Name_NL'] + dict_bel['District_Name_FR'])
    # arrondissements = st.multiselect('Which arrondissement(s) do you want to search?', dict_bel['Arrondissement'])
    provinces = st.multiselect('Which province(s) do you want to search?', province_list)
    # regions = st.multiselect('Which region(s) do you want to search?', dict_bel['Region_Name_FR'] + dict_bel['Region_Name_NL'])

    if not property_type:
        if sale_rent == 'for-rent':
            property_type = property_types_rent
        else:
            property_type = property_types_sale

    for zip in zips:
        zip = 'BE-'+zip
    zips_str = ','.join(zips)

    provinces_str = ','.join(provinces)


    # Process and save results
    if st.button('Search'):
        
        # result = immoweb_scraper.run(sale_rent, property_type, provinces_str, zips_str)
        result = immoweb_scraper_copy.run_copy(sale_rent, property_type, provinces_str, zips_str)
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

# Hide the footer
hide_default_format = """
       <style>
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

