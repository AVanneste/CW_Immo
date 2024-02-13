import functools
import requests
import itertools
import pandas as pd
import re
import json
from bs4 import BeautifulSoup
import math
from tqdm.contrib.concurrent import thread_map

def get_data_from_search_results(i, property_type, rent_sale, zone, session):
    if property_type == 'immobilier-neuf':
        api_url = f'https://www.immotop.lu/en/{property_type}/{zone}/?criterio=dataModifica&ordine=desc&pag={i}'
        resp = session.get(api_url, timeout=5)
        soup = BeautifulSoup(resp.content, "html.parser")
        results = soup.find(id="__NEXT_DATA__").text
        json_data = json.loads(results)
        proj_list = json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['results']
        proj_prop_list = []
        for i in proj_list:
            projectId = i['realEstate']['id']
            for j in i['realEstate']['properties']:
                j['project.id'] = projectId
                try:
                    id_extract = re.search(r"/annonces/([^/]+)/([^/]+)/", j['url'])
                    j['id'] = f"{id_extract.group(1)}/{id_extract.group(2)}"
                    del j['url']
                except:
                    j['id'] = projectId
                proj_prop_list.append(j)
        return pd.json_normalize(proj_prop_list)
    else:
        api_url = f'https://www.immotop.lu/en/{rent_sale}-{property_type}/{zone}/?criterio=dataModifica&ordine=desc&pag={i}'
        resp = session.get(api_url, timeout=5)
        soup = BeautifulSoup(resp.content, "html.parser")
        results = soup.find(id="__NEXT_DATA__").text
        json_data = json.loads(results)
        # prop_list = [x['realEstate']['properties'] for x in json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['pages'][0]['results']]
        prop_list = [dict(x['realEstate']['properties'][0], id=x['realEstate']['id']) for x in json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['results'] if x['realEstate']['typology']['name'] != 'Project']
        return pd.json_normalize(prop_list)

def get_data_for_category(property_type, rent_sale, zone, session):
    if property_type == 'immobilier-neuf':
        api_url = f'https://www.immotop.lu/en/{property_type}/{zone}/?criterio=dataModifica&ordine=desc&pag=1'
    else:
        api_url = f'https://www.immotop.lu/en/{rent_sale}-{property_type}/{zone}/?criterio=dataModifica&ordine=desc&pag=1'
    resp = session.get(api_url)
    pages_limit = math.ceil(int(re.search(r'"totalAds":\s*(\d+)', resp.text).group(1))/25)
    if pages_limit ==0:
        return None
    if pages_limit > 80:
        pages_limit = 80
    print('pages limit: ', pages_limit)
    return pd.concat(thread_map(functools.partial(get_data_from_search_results, property_type=property_type, rent_sale=rent_sale, zone=zone, session=session), range(1, pages_limit+1)))

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

def run(rent_sale, property_type_list, zone):
    prop_data = pd.DataFrame()
    with requests.Session() as session:
        
        for property_type in property_type_list:
            print('property type list : ', property_type_list)
            print(property_type)
            prop_data = pd.concat([prop_data, get_data_for_category(property_type, rent_sale, zone, session)])
        # ids = list(ids)
        # if ids:
            
        #     prop_data = get_properties(ids, session)
        return prop_data
