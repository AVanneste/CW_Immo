import functools
import itertools
import requests
import pandas as pd
from io import BytesIO
from tqdm.contrib.concurrent import thread_map


def get_data_from_search_results(i, property_type, rent_sale, provinces, zips, session):
    # https://www.immoweb.be/en/search/house/for-sale?countries=BE&provinces=EAST_FLANDERS,WEST_FLANDERS&districts=TOURNAI&postalCodes=BE-6700&page=1&orderBy=relevance
    api_url = f'https://www.immoweb.be/en/search-results/{property_type}/{rent_sale}?countries=BE&provinces={provinces}&page={i}&postalCodes={zips}&orderBy=newest'
    return pd.json_normalize(session.get(api_url).json()['results'])

def get_data_for_category(property_type, rent_sale, provinces, zips, session):
    return pd.concat(thread_map(functools.partial(get_data_from_search_results, property_type=property_type, rent_sale=rent_sale, provinces=provinces, zips=zips, session=session), range(1, 3)))

def get_property(id, session):
    property_url = f"https://www.immoweb.be/en/classified/{id}"
    # print(property_url)
    try:
        resp = session.get(property_url, timeout=5)
    except:
        print("resp problem")
        return
    try:
        tables = pd.read_html(resp.content)
    except:
        print("no html table found")
        return
    try:
        df = pd.concat(tables).set_index(0).T
        df['id'] = id
        df = df.set_index('id')
        return df.loc[:, ~df.columns.duplicated()]
    except:
        print("none")
        return None

def get_properties(ids, session, max_workers=64):
    return pd.concat(thread_map(functools.partial(get_property, session=session), ids, max_workers=max_workers))

def run(rent_sale, property_type_list, provinces, zips):
    prop_data = pd.DataFrame()
    # prop_data_rent = pd.DataFrame()
    # prop_data_sale = pd.DataFrame()
    with requests.Session() as session:
        
        # for rent_sale in ['for-sale', 'for-rent']:
        # if rent_sale == 'for-sale':
        for property_type in property_type_list:#['apartment', 'house', 'new-real-estate-projects', 'garage', 'office', 'business', 'industry', 'land', 'tenement', 'other']:
            prop_data = pd.concat([prop_data,get_data_for_category(property_type, rent_sale, provinces, zips, session)])
        #     ids = set(prop_data['id'].to_list())
        # ids = list(ids)
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
    

    return prop_data
    
    return  #, df_tot_sale

        
    # df_tot.to_excel('all_props_data.xlsx', index=False)
# run()