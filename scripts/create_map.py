import folium

def create_map(data):
    map_df = data.loc[data['property.location.latitude'].notna()]
    if map_df.empty:
        return None
    else:
        map_df.rename(columns={'property.location.latitude':'lat', 'property.location.longitude':'lon'}, inplace=True)
        m = folium.Map(location=[map_df['lat'].mean(),map_df['lon'].mean()], zoom_start=13)
        for i, row in map_df.iterrows():
            folium.Marker([row['lat'], row['lon']], 
                        popup=f"Link: <a href={row['url']} target='_blank'>{row['id']}</a> \n Price/Rent: {row['price.mainValue']} \n Surface: {row['property.netHabitableSurface']} \n Address: {row['property.location.street']},{row['property.location.number']} \n {row['property.location.postalCode']},{row['property.location.locality']}",
                        tooltip=f"Price/Rent: {row['price.mainValue']} \n Additional costs: {row['price.additionalValue']} \n Type: {row['property.type']}").add_to(m)

        return m
    
def create_map_immotop(data):
    map_df = data.loc[data['location.latitude'].notna()]
    if map_df.empty:
        return None
    else:
        map_df.rename(columns={'location.latitude':'lat', 'location.longitude':'lon'}, inplace=True)
        m = folium.Map(location=[map_df['lat'].mean(),map_df['lon'].mean()], zoom_start=13)
        for i, row in map_df.iterrows():
            folium.Marker([row['lat'], row['lon']], 
                        popup=f"Link: <a href={row['url']} target='_blank'>{row['id']}</a> \n Price/Rent: {row['price.value']} \n Surface: {row['surface']} \n City: {row['location.city']}",
                        tooltip=f"Price/Rent: {row['price.value']} \n Type: {row['typologyValue']}").add_to(m)

        return m

def create_map_athome(data):
    map_df = data.loc[data['completeGeoInfos.pin.lat'].notna()]
    if map_df.empty:
        return None
    else:
        map_df.rename(columns={'completeGeoInfos.pin.lat':'lat', 'completeGeoInfos.pin.lon':'lon'}, inplace=True)
        m = folium.Map(location=[map_df['lat'].astype(float).mean(),map_df['lon'].astype(float).mean()], zoom_start=13)
        for i, row in map_df.iterrows():
            folium.Marker([row['lat'], row['lon']], 
                        popup=f"Link: <a href={row['url']} target='_blank'>{row['id']}</a> \n Price/Rent: {row['price']} \n Surface: {row['property.characteristic.property_surface']} \n City: {row['completeGeoInfos.levels.L9']}",
                        tooltip=f"Price/Rent: {row['price']} \n Type: {row['immotype']}").add_to(m)

        return m