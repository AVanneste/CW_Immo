import pandas as pd

def df_transform(df):
    
    # df['url'] = 'https://www.immoweb.be/en/classified/' + df['id'].astype(str)
    
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