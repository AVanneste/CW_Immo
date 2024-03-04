import functools
import requests
import itertools
import pandas as pd
import re
import json
import math
import time
from bs4 import BeautifulSoup
from tqdm.contrib.concurrent import thread_map

def get_ids_from_search_results(i, property_type, rent_sale, provinces, districts, zips, session):
    api_url = f'https://www.immoweb.be/en/search-results/{property_type}/{rent_sale}?countries=BE&provinces={provinces}&districts={districts}&postalCodes={zips}&page={i}&orderBy=newest'
    return [result['id'] for result in session.get(api_url).json()['results']]

def get_ids_for_category(property_type, rent_sale, provinces, districts, zips, session):
    api_url = f'https://www.immoweb.be/en/search-results/{property_type}/{rent_sale}?countries=BE&provinces={provinces}&districts={districts}&postalCodes={zips}&page=1&orderBy=newest'
    total_items = session.get(api_url).json()['totalItems']
    pages_limit = min(333,math.ceil(int(total_items)/30))
    return set(itertools.chain.from_iterable(thread_map(functools.partial(get_ids_from_search_results, property_type=property_type, rent_sale=rent_sale, provinces=provinces, districts=districts, zips=zips, session=session), range(1, pages_limit+1))))

def get_property(id, session):
    property_url = f"https://www.immoweb.be/en/classified/{id}"
    for attempt in range(3):
        try:
            resp = session.get(property_url, timeout=15)
            break
        except requests.exceptions.ChunkedEncodingError as e:
            time.sleep(1)
            print(e)
    else:
        print("resp problem, id : ", id)
        return
    try:
        re_text = re.search(r"window.classified = (\{.*\})", resp.text).group(1)
        # soup = BeautifulSoup(resp.content, "html.parser")
        # re_text = soup.find('script', type='text/javascript').contents[0][33:-10]
        json_result = json.loads(re_text)
        json_keys = ['property', 'publication', 'transaction', 'price']
        json_dict = {key: json_result[key] for key in json_keys}
        prop_dict = {'id':id}
        prop_dict.update(json_dict)
        prop_df = pd.json_normalize(prop_dict, max_level=2)
        
        if json_result['property']['type'] in ['APARTMENT_GROUP', 'HOUSE_GROUP']:
            prop_df.insert(1, 'cluster.projectInfo.groupId', id)
            units_list = json_result['cluster']['units'][0]['items']
            items_id = []
            for unit in units_list:
                items_id.append(unit['id'])
            cluster_df = pd.DataFrame()
            cluster_df = pd.concat([cluster_df, get_properties(items_id, session)])
            cluster_df['cluster.projectInfo.groupId'] = id
            prop_df = pd.concat([prop_df, cluster_df])
        return prop_df 
    except:
        print("no html content found, id: ", id)
        return

def get_properties(ids, session, max_workers=64):
    return pd.concat(thread_map(functools.partial(get_property, session=session), ids, max_workers=max_workers))

def run(rent_sale, property_type_list, provinces='', districts='', zips=''):
    ids = set()
    with requests.Session() as session:
        for property_type in property_type_list:
            print('prop type: ', property_type)
            ids.update(get_ids_for_category(property_type, rent_sale, provinces, districts, zips, session))
        ids = list(ids)
        if ids:
            prop_data = get_properties(ids, session)
        else:
            return pd.DataFrame()
        return prop_data