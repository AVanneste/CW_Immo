import requests
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import stqdm
import streamlit as st
import re
import json

def geocode_urls(df, url_column='URL', lat_column='Latitude', lng_column='Longitude', max_workers=12):
    """
    Geocode only rows with missing or zero latitude
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame with URLs to geocode
    url_column : str, optional
        Name of the column containing URLs (default: 'URL')
    lat_column : str, optional
        Name of the column storing latitude (default: 'Latitude')
    lng_column : str, optional
        Name of the column storing longitude (default: 'Longitude')
    max_workers : int, optional
        Maximum number of threads to use (default: 12)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with updated geocoding results
    """
    # Create a copy of the DataFrame
    df = df.copy()
    
    if lat_column not in df.columns:
        df['Latitude'] = ''
        df['Longitude'] = ''
    
    # Select only rows needing geocoding
    # to_geocode = df.loc[(df[lat_column].isin([0, np.nan, '']))]
    # to_geocode = df.loc[(df[lat_column]=='Error: None returned')]
    to_geocode = df.loc[(df[lat_column].isna())|(df[lat_column]=='')]
    st.write(f"Found {len(to_geocode)} addresses to geocode")
    
    def geocode_single_url(url):
        try:
            if pd.isna(url):
                return 'Missing URL', 'Missing URL'
                
            # st.write(f"Processing URL: {url}")  # Debug st.write
            response = requests.get(url)
            
            if response.status_code != 200:
                return f'HTTP Error: {response.status_code}', f'HTTP Error: {response.status_code}'
                
            j = response.json()
            if not j.get('results'):
                return ('No results in response', 'No results in response')
            dfj = pd.json_normalize(j['results'])
            # st.write(j['results'])
            if len(dfj) == 0:
                return 'Not found', 'Not found'
            elif len(dfj) == 1:
                return (dfj['geometry.location.lat'].values[0], 
                        dfj['geometry.location.lng'].values[0])
            elif len(dfj)==2:
                # st.write("length is 2")
                # if ("{:.3f}".format(dfj['geometry.location.lat'].values[0])=="{:.3f}".format(dfj['geometry.location.lat'].values[1]))&("{:.3f}".format(dfj['geometry.location.lng'].values[0])=="{:.3f}".format(dfj['geometry.location.lng'].values[1])):
                if (abs(dfj['geometry.location.lat'].values[0] - dfj['geometry.location.lat'].values[1]) <= 0.02)&(abs(dfj['geometry.location.lng'].values[0] - dfj['geometry.location.lng'].values[1]) <= 0.02):
                    return (dfj['geometry.location.lat'].values[0], 
                            dfj['geometry.location.lng'].values[0])
                try:
                    if int(re.search(r'(\d{4})',dfj['formatted_address'].values[0])[0]) != int(re.search(r'(\d{4})',dfj['formatted_address'].values[1])[0]):
                        list_pc = [int(re.search(r'(\d{4})',dfj['formatted_address'].values[0])[0]), int(re.search(r'(\d{4})',dfj['formatted_address'].values[1])[0])]
                        index_pc = list_pc.index(df['Postal_Code'].loc[df['URL']==url].values[0])
                        return (dfj['geometry.location.lat'].values[index_pc], 
                                dfj['geometry.location.lng'].values[index_pc])
                except:
                    return ('Partial match', 'Partial match')
            else:
                return ('Partial match', 'Partial match')
                
        except requests.exceptions.RequestException as e:
            return f'Request Error: {str(e)}', f'Request Error: {str(e)}'
        except json.JSONDecodeError:
            return ('Invalid JSON response', 'Invalid JSON response')
        except Exception as e:
            return f'Error: {str(e)}', f'Error: {str(e)}'
    
    # Process URLs with progress bar
    results = {}
    failed_urls = []
    
    for idx, row in stqdm.stqdm(to_geocode.iterrows(), total=len(to_geocode), desc="Geocoding"):
        url = row[url_column]
        try:
            result = geocode_single_url(url)
            if result is None:  # Safeguard against None returns
                result = ('Error: None returned', 'Error: None returned')
            results[idx] = result
        except Exception as e:
            st.write(f"\nError processing row {idx}: {str(e)}")
            failed_urls.append((idx, url))
            results[idx] = ('Error: Processing failed', 'Error: Processing failed')
    
    # Update original DataFrame
    for idx, (lat, lng) in results.items():
        df.loc[idx, lat_column] = lat
        df.loc[idx, lng_column] = lng
    
    # st.write summary
    st.write("\nGeocoding Summary:")
    st.write(f"Total processed: {len(results)}")
    success_count = sum(1 for lat, lng in results.values() 
                       if not isinstance(lat, str) and not isinstance(lng, str))
    st.write(f"Successfully geocoded: {success_count}")
    st.write(f"Failed: {len(results) - success_count}")
    
    if failed_urls:
        st.write("\nFailed URLs:")
        for idx, url in failed_urls[:5]:  # Show first 5 failed URLs
            st.write(f"Row {idx}: {url[:100]}...")  # Show first 100 chars of URL
    
    return df