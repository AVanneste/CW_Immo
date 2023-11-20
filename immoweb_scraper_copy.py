import functools
import itertools
import requests
import pandas as pd
from io import BytesIO
import re
import json
from tqdm.contrib.concurrent import thread_map


def get_data_from_search_results(i, property_type, rent_sale, provinces, zips, session):
    # https://www.immoweb.be/en/search/house/for-sale?countries=BE&provinces=EAST_FLANDERS,WEST_FLANDERS&districts=TOURNAI&postalCodes=BE-6700&page=1&orderBy=relevance
    api_url = f'https://www.immoweb.be/en/search-results/{property_type}/{rent_sale}?countries=BE&provinces={provinces}&page={i}&postalCodes={zips}&orderBy=newest'
    return pd.json_normalize(session.get(api_url).json()['results'])

def get_data_for_category(property_type, rent_sale, provinces, zips, session):
    return pd.concat(thread_map(functools.partial(get_data_from_search_results, property_type=property_type, rent_sale=rent_sale, provinces=provinces, zips=zips, session=session), range(1, 10)))

def get_property(id, session):
    property_url = f"https://www.immoweb.be/en/classified/{id}"
    # print(property_url)
    try:
        print("it's trying response")
        resp = session.get(property_url, timeout=5)
        # print(resp.content)
    except:
        print("resp problem")
        return
    try:
        print("it's trying tables")
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
        # tables = pd.read_html(resp.content)
        
    except:
        print("no html content found")
        return
    # try:
    #     df = pd.concat(tables).set_index(0).T
    #     df['id'] = id
    #     df = df.set_index('id')
    #     return df.loc[:, ~df.columns.duplicated()]
    # except:
    #     print("none")
    #     return None

def get_properties(ids, session, max_workers=64):
    return pd.concat(thread_map(functools.partial(get_property, session=session), ids, max_workers=max_workers))

def run_copy(rent_sale, property_type_list, provinces, zips):
    prop_data = pd.DataFrame()
    # prop_data_rent = pd.DataFrame()
    # prop_data_sale = pd.DataFrame()
    with requests.Session() as session:
        
        # for rent_sale in ['for-sale', 'for-rent']:
        # if rent_sale == 'for-sale':
        for property_type in property_type_list:#['apartment', 'house', 'new-real-estate-projects', 'garage', 'office', 'business', 'industry', 'land', 'tenement', 'other']:
            
            prop_data = pd.concat([prop_data,get_data_for_category(property_type, rent_sale, provinces, zips, session)])
            ids = set(prop_data['id'].loc[prop_data['price.type']=='group_sale'].to_list())
        ids = list(ids)
        
        if ids:
            get_prop_df = pd.DataFrame()
            for id in ids:
                get_prop = get_property(id, session)
                get_prop_df = pd.concat([get_prop_df, get_prop])
                
            get_prop_df.rename(columns={'subtype':'property.subtype', 'floor':'property.location.floor', 'price':'price.mainValue',
                                        'bedroomCount': 'property.bedroomCount', 'surface': 'property.netHabitableSurface'}, inplace=True)
            get_prop_df = get_prop_df.drop(['realEstateProjectPhase'], axis=1)
            prop_data = pd.concat([prop_data, get_prop_df], axis=0, ignore_index=True)
        # else:
        #     for property_type in #['apartment', 'house', 'garage', 'office', 'business', 'industry', 'land', 'other']:
        #         prop_data_rent = pd.concat([prop_data_rent,get_data_for_category(property_type, rent_sale, session)])
        #         ids_rent = set(prop_data_rent['id'].to_list())
    # ids_rent = list(ids_rent)
    # ids_sale = list(ids_sale)
        # properties_rent = get_properties(ids_rent, session)
        # properties_sale = get_properties(ids_sale, session)

    # df_tot_rent = pd.merge(properties_rent, prop_data_rent, on='id')
    # df_tot_sale = pd.merge(properties_sale, prop_data_sale, on='id')
    

    return prop_data#, get_prop_df