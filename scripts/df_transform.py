import pandas as pd

def df_transform(df):

    df_cols = df.columns.to_list()
    
    drop_cols = ['customerLogoUrl', 'customerName', 'priceType', 'isBookmarked', 'has360Tour', 'hasVirtualTour', 
                  'advertisementId', 'cluster.projectInfo',  'flags.main', 'flags.secondary', 'flags.percentSold', 'media.pictures',
                  'property.location.distance', 'property.location.approximated', 'property.location.type',
                  'property.location.hasSeaView', 'property.location.pointsOfInterest', 'publication.publisherId', 'publication.visualisationOption',
                  'publication.size', 'transaction.certificateLogoUrl', 'transaction.rental', 'transaction.sale.lifeAnnuity', 'transaction.sale.publicSale',
                  'transaction.sale.toBuild', 'transaction.sale.isSubjectToVat', 'price.mainDisplayPrice', 'price.HTMLDisplayPrice',
                  'price.alternativeDisplayPrice', 'price.oldDisplayPrice', 'price.shortDisplayPrice', 'price.accessibilityPrice', 'price.label',
                  'price.date', 'price.language', 'cluster.projectInfo.constructor', 'cluster.projectInfo.phase', 'cluster.projectInfo.deliveryDate',
                  'cluster.projectInfo.unitsDisplayMode', 'transaction.sale.lifeAnnuity.estimatedPropertyValue', 'transaction.sale.lifeAnnuity.isIndexed',
                  'transaction.sale.lifeAnnuity.isJointAndSurvivorContract', 'transaction.sale.lifeAnnuity.isBareOwnership',
                  'transaction.sale.lifeAnnuity.contractMaximumDurationDescription', 'transaction.sale.lifeAnnuity.annuitantCount',
                  'transaction.sale.lifeAnnuity.annuitantAges', 'transaction.sale.publicSale.pendingOverbidAmount',
                  'transaction.sale.publicSale.isForcedSale', 'transaction.sale.publicSale.lastSessionReachedPrice', 'transaction.sale.publicSale.date']
    
    to_drop = [x for x in df_cols if x in drop_cols]

    df = df.drop(to_drop, axis=1)
    
    return df

def annechien_results(df):
    
    df_cols = df.columns.to_list()
    annechien_columns = ['url', 'property.bedroomCount', 'property.location.locality', 'property.location.postalCode', 'property.location.street', 'property.location.number', 'property.location.floor',
                                           'property.netHabitableSurface', 'property.building.condition', 'property.terraceSurface', 'transaction.certificates.epcScore', 'transaction.rental.monthlyRentalPrice']
    to_keep = [x for x in df_cols if x in annechien_columns]
    df = df[to_keep]
    
    return df

def copy_group_values(df_group, df_units):
    
    for id in df_units['cluster.projectInfo.groupId'].unique().tolist():

        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.country'] = df_group['property.location.country'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.region'] = df_group['property.location.region'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.province'] = df_group['property.location.province'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.district'] = df_group['property.location.district'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.locality'] = df_group['property.location.locality'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.postalCode'] = df_group['property.location.postalCode'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.street'] = df_group['property.location.street'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.number'] = df_group['property.location.number'].loc[df_group['id']==id].values[0]
        # df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.box'] = df_group['property.location.box'].loc[df_group['id']==id]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.propertyName'] = df_group['property.location.propertyName'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.latitude'] = df_group['property.location.latitude'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.longitude'] = df_group['property.location.longitude'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.regionCode'] = df_group['property.location.regionCode'].loc[df_group['id']==id].values[0]
        df_group.loc[df_group['cluster.projectInfo.groupId']==id, 'property.location.placeName'] = df_group['property.location.placeName'].loc[df_group['id']==id].values[0]
        
    return df_group

def new_cols(df):
    df = df.drop_duplicates(subset='id')
    df.insert(1, 'url', 'https://www.immoweb.be/en/classified/' + df['id'].astype(str))
    try:
        col = df.pop('cluster.projectInfo.groupId')
        df.insert(2, col.name, col)
        df.insert(3, 'MainValue/Surface', df['price.mainValue'].astype('Int64')/df['property.netHabitableSurface'].astype('Int64'))
    except:
        df.insert(2, 'MainValue/Surface', df['price.mainValue'].astype('Int64')/df['property.netHabitableSurface'].astype('Int64'))
    
    return df

def transform_immotop(df):
    try:
        df.rename(columns={'realEstate.id':'id'}, inplace=True)
    except:
        None
    try:
        df.rename(columns={'typology.name':'typologyValue'}, inplace=True)
        
    except:
        None
    df.insert(1, 'url', 'https://www.immotop.lu/en/annonces/' + df['id'].astype(str))
    return df

def transform_athome(df):
    df = df.drop_duplicates(subset='id')
    df.insert(1, 'url', 'https://www.athome.lu/id-' + df['id'].astype(str) + '.html')
    return df