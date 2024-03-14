import functools
import requests
import pandas as pd
import re
import json
import math
from tqdm.contrib.concurrent import thread_map
from scripts.df_transform import copy_group_values

def get_data_from_search_results(i, property_type, rent_sale, provinces, districts, zips, session):
    api_url = f'https://www.immoweb.be/en/search-results/{property_type}/{rent_sale}?countries=BE&provinces={provinces}&districts={districts}&postalCodes={zips}&page={i}&orderBy=newest'
    return pd.json_normalize(session.get(api_url).json()['results'])

def get_data_for_category(property_type, rent_sale, provinces, districts, zips, session):
    api_url = f'https://www.immoweb.be/en/search-results/{property_type}/{rent_sale}?countries=BE&provinces={provinces}&districts={districts}&postalCodes={zips}&page=1&orderBy=newest'
    total_items = session.get(api_url).json()['totalItems']
    if total_items == 0:
        return pd.DataFrame()
    pages_limit = math.ceil(int(total_items)/20)
    return pd.concat(thread_map(functools.partial(get_data_from_search_results, property_type=property_type, rent_sale=rent_sale, provinces=provinces, districts=districts, zips=zips, session=session), range(1, pages_limit+1)))

def get_property(id, session):
    property_url = f"https://www.immoweb.be/en/classified/{id}"
    try:
        resp = session.get(property_url, timeout=5)
    except:
        print("resp problem")
        return
    try:
        re_text =re.search(r"window.classified = (\{.*\})", resp.text).group(1)
        json_result = json.loads(re_text)
        group_id = json_result['id']
        try:
            energy_cons = json_result['transaction']['certificates']['primaryEnergyConsumptionPerSqm']
        except:
            energy_cons = None
        units_list = json_result['cluster']['units']
        items = []
        for unit in units_list:
            for item in unit['items']:
                item['cluster.projectInfo.groupId'] = group_id
                item['primaryEnergyConsumptionPerSqm'] = energy_cons
                items.append(item)
        return pd.DataFrame(items)
    except:
        print("no html content found")
        return

def get_properties(ids, session, max_workers=64):
    return pd.concat(thread_map(functools.partial(get_property, session=session), ids, max_workers=max_workers))

def run(rent_sale, property_type_list, provinces, districts, zips):
    prop_data = pd.DataFrame()

    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
        for property_type in property_type_list:
            
            prop_data = pd.concat([prop_data,get_data_for_category(property_type, rent_sale, provinces, districts, zips, session)])
        
        if not prop_data.empty:
            ids = set(prop_data['id'].loc[prop_data['price.type']=='group_sale'].to_list())
            ids = list(ids)
            if ids:
                get_prop_df = get_properties(ids, session)
                    
                get_prop_df.rename(columns={'subtype':'property.subtype', 'floor':'property.location.floor', 'price':'price.mainValue',
                                            'bedroomCount': 'property.bedroomCount', 'surface': 'property.netHabitableSurface'}, inplace=True)
                get_prop_df = get_prop_df.drop(['realEstateProjectPhase'], axis=1)
                prop_data = pd.concat([prop_data, get_prop_df], axis=0, ignore_index=True)
                prop_data = copy_group_values(prop_data, get_prop_df)
                
    return prop_data
