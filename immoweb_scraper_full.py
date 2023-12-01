import functools
import requests
import itertools
import pandas as pd
import re
import json
from tqdm.contrib.concurrent import thread_map
from df_transform import copy_group_values

def get_ids_from_search_results(i, property_type, rent_sale, provinces, districts, zips, session):
    api_url = f'https://www.immoweb.be/en/search-results/{property_type}/{rent_sale}?countries=BE&provinces={provinces}&districts={districts}&postalCodes={zips}&page={i}&orderBy=newest'
    # return pd.json_normalize(session.get(api_url).json()['results'])
    return [result['id'] for result in session.get(api_url).json()['results']]

def get_ids_for_category(property_type, rent_sale, provinces, districts, zips, session):
    # return pd.concat(thread_map(functools.partial(get_ids_from_search_results, property_type=property_type, rent_sale=rent_sale, provinces=provinces, districts=districts, zips=zips, session=session), range(1, 100)))
    return set(itertools.chain.from_iterable(thread_map(functools.partial(get_ids_from_search_results, property_type=property_type, rent_sale=rent_sale, provinces=provinces, districts=districts, zips=zips, session=session), range(1, 100))))


def get_property(id, session):
    property_url = f"https://www.immoweb.be/en/classified/{id}"
    try:
        resp = session.get(property_url, timeout=5)
    except:
        print("resp problem")
        return
    # try:
    #     re_text =re.search(r"window.classified = (\{.*\})", resp.text).group(1)
    #     json_result = json.loads(re_text)
    #     group_id = json_result['id']
    #     try:
    #         energy_cons = json_result['transaction']['certificates']['primaryEnergyConsumptionPerSqm']
    #     except:
    #         energy_cons = None
    #     units_list = json_result['cluster']['units']
    #     items = []
    #     for unit in units_list:
    #         for item in unit['items']:
    #             item['cluster.projectInfo.groupId'] = group_id
    #             item['primaryEnergyConsumptionPerSqm'] = energy_cons
    #             items.append(item)
    #     return pd.DataFrame(items)        
    try:
        re_text =re.search(r"window.classified = (\{.*\})", resp.text).group(1)
        json_result = json.loads(re_text)
        # json_result['property']['id'] = id
        prop_dict = {'id':id}
        prop_dict.update(json_result['property'])
        # json_result['url'] = "https://www.immoweb.be/en/classified/"+str(id)
        return pd.json_normalize(prop_dict)
    
    
    
    
    except:
        print("no html content found")
        return

def get_properties(ids, session, max_workers=64):
    return pd.concat(thread_map(functools.partial(get_property, session=session), ids, max_workers=max_workers))

def run(rent_sale, property_type_list, provinces, districts, zips):
    prop_data = pd.DataFrame()
    ids = set()
    with requests.Session() as session:
        

        for property_type in property_type_list:
            
            ids.update(get_ids_for_category(property_type, rent_sale, provinces, districts, zips, session))
        
        ids = list(ids)
        if ids:
            
            get_prop_df = get_properties(ids, session)
                
            # get_prop_df.rename(columns={'subtype':'property.subtype', 'floor':'property.location.floor', 'price':'price.mainValue',
            #                             'bedroomCount': 'property.bedroomCount', 'surface': 'property.netHabitableSurface'}, inplace=True)
            # get_prop_df = get_prop_df.drop(['realEstateProjectPhase'], axis=1)
            prop_data = pd.concat([prop_data, get_prop_df], axis=0, ignore_index=True)
            # prop_data = copy_group_values(prop_data, get_prop_df)

        return prop_data
