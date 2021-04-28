# A simple folium map showing all the hospitals that with available beds information.
# The data is based on the Delhi COVID Beds Dashboard. Each hospital icon is color-coded to depict the availability of vacant beds.

import urllib
import json
import pandas as pd
import folium
url = "https://coronabeds.jantasamvad.org/covid-facilities.js"
testfile = urllib.request.URLopener()
testfile.retrieve(url, "./Data/covid-faclities.js")

# Parse JavaScript JSON 
with open('./Data/covid-faclities.js') as js_file:
    data = js_file.read()
    obj = data[data.find('{') : data.rfind('}')+1]
    jsonObj = json.loads(obj)

# Clean Data
df = pd.DataFrame(jsonObj).transpose()
df['Name'] = df.index
df = df[df.location != ''].dropna() # Get rid of invalid entries
df = df[df.Name != 'Nestiva Hospital']
# df.head()
df['Latitude'] = [float(val.split('@')[-1].split(',')[0]) for val in df.location]
df['Longitude'] = [float(val.split('@')[-1].split(',')[1]) for val in df.location]
# df.head()

# # Make a map of all COVID Hospitals in Delhi
# m = folium.Map(location=[28.65, 77.25], zoom_start=10.5)
# for name, lat, lon in zip(df.Name, df.Latitude, df.Longitude):
#     folium.Marker(
#         [lat,lon],
#         icon=folium.Icon(color='red',icon='medkit',prefix='fa'),
#         popup = folium.Popup(('Name: ' + str(name) + '<br>'
#                 'Latitude: ' + str(lat) + '<br>'
#                 'Longitude: ' + str(lon) + '<br>'), max_width=300, min_width=200)
#     ).add_to(m)
# m
# -------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------- #

# Retreive Beds Data
url = "https://coronabeds.jantasamvad.org/covid-info.js"
testfile = urllib.request.URLopener()
testfile.retrieve(url, "./Data/covid-beds-info.js")

# Parse JavaScript JSON 
with open('./Data/covid-beds-info.js') as js_file:
    data = js_file.read()
    obj = data[data.find('{') : data.rfind('}')+1]
    jsonObj = json.loads(obj)

beds_df = pd.DataFrame(jsonObj['beds']).transpose()
beds_df['Name'] = beds_df.index

# Merge Beds Data with Hospital Locations
df = pd.merge(beds_df, df, on='Name', how='right').dropna() # Dataframe containing details of all hospitals with beds information

# Assign a color based on the number of vacant beds
df['marker_color'] = pd.cut(df['vacant'].astype(int), bins=10, 
                              labels=['gray', 'darkred','red', 'lightred', 'orange', 'lightblue', 'blue', 'darkblue', 'lightgreen','green'])

m = folium.Map(location=[28.8, 77.75], zoom_start=10.5, tiles='Stamen Terrain')
for name, typ, total, occupied, vacant, last_updated, lat, lon, color in zip(df.Name, df.type_x, df.total, df.occupied, df.vacant, df.last_updated_at, df.Latitude, df.Longitude, df.marker_color):
    folium.Marker(
        [lat,lon],
        icon=folium.Icon(color=color,icon='medkit',prefix='fa'),
        popup = folium.Popup(('Name: ' + str(name) + '<br>'
                'Type: ' + str(typ) + '<br>'
                'Total Beds: ' + str(total) + '<br>'
                'Occupied Beds: ' + str(occupied) + '<br>'
                'Vacant Beds: ' + str(vacant) + '<br>'
                'Last Updated: ' + str(last_updated) + '<br>'), max_width=300, min_width=200)
    ).add_to(m)
m.save('index.html')
