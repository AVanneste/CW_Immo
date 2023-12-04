import folium

def create_map(data):
    map_df = data[['property.location.latitude', 'property.location.longitude']]
    map_df = data.loc[data['property.location.latitude'].notna()]
    if map_df.empty:
        return None
    else:
        map_df.rename(columns={'property.location.latitude':'lat', 'property.location.longitude':'lon'}, inplace=True)
        # print(map_df)
        m = folium.Map(location=[map_df['lat'].mean(),map_df['lon'].mean()], zoom_start=13)
        for i, row in map_df.iterrows():
            folium.Marker([row['lat'], row['lon']], 
                        popup=f"Link: <a href={row['url']} target='_blank'>Immoweb {row['id']}</a> \n Price/Rent: {row['price.mainValue']} \n Surface: {row['property.netHabitableSurface']} \n Address: {row['property.location.street']},{row['property.location.number']} \n {row['property.location.postalCode']},{row['property.location.locality']}",
                        tooltip=f"Price/Rent: {row['price.mainValue']} \n Additional costs: {row['price.additionalValue']} \n Type: {row['property.type']}").add_to(m)

        return m