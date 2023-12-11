import functools
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from tqdm.contrib.concurrent import thread_map

def get_data_from_search_results(i, rent_sale, property_type, zone, session):
    if property_type == '':
        url = f'https://www.athome.lu/en/srp/?tr={rent_sale}&q={zone}&sort=date_desc&page={i}'
    else:
        url = f'https://www.athome.lu/en/srp/?tr={rent_sale}&ptypes={property_type}&q={zone}&sort=date_desc&page={i}'
    r = session.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    try:
        results = soup.select("script")[5].contents[0].string
        athome = json.loads(results[32:-4])
        prop_list = []
        for item in athome['search']['list']:
            # item['hkey_L4'] = item['completeGeoInfos']['hkey'][1]
            # item['hkey_L7'] = item['completeGeoInfos']['hkey'][2]
            # item['hkey_L9'] = item['completeGeoInfos']['hkey'][3]
            # item['Name_L4'] = item['completeGeoInfos']['levels']['L4']
            # item['Name_L7'] = item['completeGeoInfos']['levels']['L7']
            # item['Name_L9'] = item['completeGeoInfos']['levels']['L9']
            # if len(item['completeGeoInfos']['hkey'])==5:
            #     item['hkey_L10'] = item['completeGeoInfos']['hkey'][4]
            #     item['Name_L10'] = item['completeGeoInfos']['levels']['L10']
            if item['has_children']==True:
                groupId = item['id']
                item['project.id'] = groupId
                prop_list.append(item)
                for child in item['children']['data']:
                    child['project.id'] = groupId
                    prop_list.append(child)
                    child['id'] = child['listing_id']
                    del child['listing_id']
            else:
                prop_list.append(item)
        return pd.json_normalize(prop_list)
    except:
        None

def get_data_for_category(rent_sale, property_type, zone, session):
    if property_type == '':
        url = f'https://www.athome.lu/en/srp/?tr={rent_sale}&q={zone}&sort=date_desc'
    else:
        url = f'https://www.athome.lu/en/srp/?tr={rent_sale}&ptypes={property_type}&q={zone}&sort=date_desc'
    print(url)
    r = session.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    try:
        results = soup.select("script")[5].contents[0].string
        athome = json.loads(results[32:-4])
        max_pages = athome['search']['paginator']['totalPages']
        if max_pages==0:
            return None
    except:
        max_pages = 1
    print("max search pages: ", max_pages)
    return pd.concat(thread_map(functools.partial(get_data_from_search_results, rent_sale=rent_sale, property_type=property_type, zone=zone, session=session), range(1, max_pages + 1)))


# def get_property(id, session):
#     property_url = f"https://www.immotop.lu/en/annonces/{id}"
#     try:
#         resp = session.get(property_url, timeout=5)
#     except:
#         print("resp problem")
#         return
#     try:
#         resp = requests.get(property_url)
#         soup = BeautifulSoup(resp.content, "html.parser")
#         results = soup.find(id="__NEXT_DATA__").text
#         json_data = json.loads(results)
#         return pd.json_normalize(json_data['props']['pageProps']['detailData']['realEstate']['properties'][0], max_level=3)
    
#     except:
#         print("no html content found")
#         return

# def get_properties(ids, session, max_workers=64):
#     return pd.concat(thread_map(functools.partial(get_property, session=session), ids, max_workers=max_workers))

def run(rent_sale, property_type, zone):
    prop_data = pd.DataFrame()
    with requests.Session() as session:
        
        # for property_type in property_type_list:
        print(property_type)
        prop_data = pd.concat([prop_data, get_data_for_category(rent_sale, property_type, zone, session)])
        # ids = list(ids)
        # if ids:
            
        #     prop_data = get_properties(ids, session)
        return prop_data
