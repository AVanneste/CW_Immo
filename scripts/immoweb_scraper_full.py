import functools
import requests
import itertools
import pandas as pd
import re
import json
import math
import time
import stqdm
import streamlit as st
# from bs4 import BeautifulSoup
from tqdm.contrib.concurrent import thread_map
import concurrent.futures

def get_ids_from_search_results(i, property_type, rent_sale, provinces, districts, zips, session):
    api_url = f'https://www.immoweb.be/en/search-results/{property_type}/{rent_sale}?countries=BE&provinces={provinces}&districts={districts}&postalCodes={zips}&page={i}&orderBy=newest'
    return [result['id'] for result in session.get(api_url).json()['results']]

def get_ids_for_category(property_type, rent_sale, provinces, districts, zips, session):
    api_url = f'https://www.immoweb.be/en/search-results/{property_type}/{rent_sale}?countries=BE&provinces={provinces}&districts={districts}&postalCodes={zips}&page=1&orderBy=newest'
    total_items = session.get(api_url).json()['totalItems']
    pages_limit = min(333, math.ceil(int(total_items) / 30))
    return set(itertools.chain.from_iterable(thread_map(functools.partial(get_ids_from_search_results, property_type=property_type, rent_sale=rent_sale, provinces=provinces, districts=districts, zips=zips, session=session), range(1, pages_limit + 1))))

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
        return []
    try:
        re_text = re.search(r"window.classified = (\{.*\})", resp.text).group(1)
        json_result = json.loads(re_text)
        json_keys = ['property', 'publication', 'transaction', 'price']
        json_dict = {key: json_result[key] for key in json_keys}
        prop_dict = {'id': id}
        prop_dict.update(json_dict)
        properties_list = [prop_dict]

        if json_result['property']['type'] in ['APARTMENT_GROUP', 'HOUSE_GROUP']:
            units_list = json_result['cluster']['units'][0]['items']
            for unit in units_list:
                cluster_dict = get_property(unit['id'], session)
                if cluster_dict:
                    cluster_dict[0]['cluster.projectInfo.groupId'] = id
                    properties_list.extend([cluster_dict[0]])
        
        return properties_list
    except:
        print("no html content found, id: ", id)
        return []

# def get_properties(ids, session, tqdm_obj, max_workers=64):
#     properties_list = []
#     properties_list.extend(thread_map(functools.partial(get_property, session=session), ids, max_workers=max_workers))
#     for item in properties_list:
#         tqdm_obj.update(1)
#     return [item for sublist in properties_list for item in sublist]

def run(rent_sale, property_type_list, provinces='', districts='', zips=''):
    ids = set()
    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
        for property_type in property_type_list:
            print('prop type: ', property_type)
            ids.update(get_ids_for_category(property_type, rent_sale, provinces, districts, zips, session))
        ids = list(ids)
        if ids:
            results = []
            with stqdm.stqdm(total=len(ids)) as tqdm_obj:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    for result in executor.map(lambda id: get_property(id, session), ids):
                        results.extend(result)
                        tqdm_obj.update(1)
                prop_data = pd.json_normalize(results)
        else:
            prop_data = pd.DataFrame()
        return prop_data