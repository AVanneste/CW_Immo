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
    # try:
    results = soup.select("script")[6].contents[0]
    athome = json.loads(results[27:-1])
    prop_list = []
    for item in athome['search']['list']:
        [item.pop(key) for key in ["media", "meta", "depth", "publisher", "config", "others"]]
        if item['has_children']==True:
            groupId = item['id']
            item['project.id'] = groupId
            prop_list.append(item)
            for child in item['children']['data']:
                print(child.keys())
                # [child.pop(key) for key in ["media", "meta", "depth", "publisher", "config", "others"]]
                child['project.id'] = groupId
                prop_list.append(child)
                child['id'] = child['listing_id']
                del child['listing_id']
        else:
            prop_list.append(item)
    return pd.json_normalize(prop_list)
    # except:
    #     print("content not found")
    #     None

def get_data_for_category(rent_sale, property_type, zone, session):
    if property_type == '':
        url = f'https://www.athome.lu/en/srp/?tr={rent_sale}&q={zone}&sort=date_desc'
    else:
        url = f'https://www.athome.lu/en/srp/?tr={rent_sale}&ptypes={property_type}&q={zone}&sort=date_desc'
    print(url)
    r = session.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    try:
        results = soup.select("script")[6].contents[0]
        athome = json.loads(results[27:-1])
        max_pages = athome['search']['paginator']['totalPages']
        if max_pages==0:
            return None
    except:
        max_pages = 1
    print("max search pages: ", max_pages)
    return pd.concat(thread_map(functools.partial(get_data_from_search_results, rent_sale=rent_sale, property_type=property_type, zone=zone, session=session), range(1, max_pages + 1)))

def run(rent_sale, property_type, zone):
    prop_data = pd.DataFrame()
    with requests.Session() as session:
        prop_data = pd.concat([prop_data, get_data_for_category(rent_sale, property_type, zone, session)])
        return prop_data