# A simple folium map showing all the hospitals that with available beds information.
# The data is based on the Delhi COVID Beds Dashboard. Each hospital icon is color-coded to depict the availability of vacant beds.
from flask import Flask
import urllib
import json
import pandas as pd
import folium

app = Flask(__name__)

@app.route('/')

def map_script():
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
    ndf = pd.merge(beds_df, df, on='Name', how='right').dropna() # Dataframe containing details of all hospitals with beds information

    # Assign a color based on the number of vacant beds
    ndf['marker_color'] = pd.cut(ndf['vacant'].astype(int), bins=10, 
                                  labels=['gray', 'darkred','red', 'lightred', 'orange', 'lightblue', 'blue', 'darkblue', 'lightgreen','green'])

    # m = folium.Map(location=[28.65, 77.05], zoom_start=10.5)
    m = folium.Map(location=[28.65, 77.05], zoom_start= 10.5, tiles=None)
    base_map = folium.FeatureGroup(name='Basemap', overlay=True, control=False)
    folium.TileLayer(tiles='OpenStreetMap').add_to(base_map)
    base_map.add_to(m)

    covid_beds = folium.FeatureGroup(name="COVID Beds", overlay=False)

    for name, typ, total, occupied, vacant, last_updated, lat, lon, color in zip(ndf.Name, ndf.type_x, ndf.total, ndf.occupied, ndf.vacant, ndf.last_updated_at, ndf.Latitude, ndf.Longitude, ndf.marker_color):
        folium.Marker(
            [lat,lon],
            icon=folium.Icon(color=color,icon='plus',prefix='fa'),
            popup = folium.Popup(('Name: ' + str(name) + '<br>'
                    'Type: ' + str(typ) + '<br>'
                    'Total: ' + str(total) + '<br>'
                    'Occupied: ' + str(occupied) + '<br>'
                    'Vacant: ' + str(vacant) + '<br>'
                    'Last Updated: ' + str(last_updated) + '<br>'), max_width=300, min_width=200)
        ).add_to(covid_beds)

    # m.save('index.html')

    ventilators_df = pd.DataFrame(jsonObj['ventilators']).transpose()
    ventilators_df['Name'] = ventilators_df.index

    # Merge Beds Data with Hospital Locations
    mdf = pd.merge(ventilators_df, df, on='Name', how='right').dropna() # Dataframe containing details of all hospitals with beds information

    # Assign a color based on the number of vacant beds
    mdf['marker_color'] = pd.cut(mdf['vacant'].astype(int), bins=2, 
                                  labels=['gray', 'green'])

    ventilators = folium.FeatureGroup(name="Ventilators", overlay=False)
    for name, typ, total, occupied, vacant, last_updated, lat, lon, color in zip(mdf.Name, mdf.type_x, mdf.total, mdf.occupied, mdf.vacant, mdf.last_updated_at, mdf.Latitude, mdf.Longitude, mdf.marker_color):
        folium.Marker(
            [lat,lon],
            icon=folium.Icon(color=color,icon='plus',prefix='fa'),
            popup = folium.Popup(('Name: ' + str(name) + '<br>'
                    'Type: ' + str(typ) + '<br>'
                    'Total: ' + str(total) + '<br>'
                    'Occupied: ' + str(occupied) + '<br>'
                    'Vacant: ' + str(vacant) + '<br>'
                    'Last Updated: ' + str(last_updated) + '<br>'), max_width=300, min_width=200)
        ).add_to(ventilators)

    icu_beds_df = pd.DataFrame(jsonObj['covid_icu_beds']).transpose()
    icu_beds_df['Name'] = icu_beds_df.index

    # Merge Beds Data with Hospital Locations
    mdf = pd.merge(icu_beds_df, df, on='Name', how='right').dropna() # Dataframe containing details of all hospitals with beds information

    # Assign a color based on the number of vacant beds
    mdf['marker_color'] = pd.cut(mdf['vacant'].astype(int), bins=10, 
                                  labels=['gray', 'darkred','red', 'lightred', 'orange', 'lightblue', 'blue', 'darkblue', 'lightgreen','green'])

    icu_beds = folium.FeatureGroup(name="COVID ICU Beds", overlay=False)
    for name, typ, total, occupied, vacant, last_updated, lat, lon, color in zip(mdf.Name, mdf.type_x, mdf.total, mdf.occupied, mdf.vacant, mdf.last_updated_at, mdf.Latitude, mdf.Longitude, mdf.marker_color):
        folium.Marker(
            [lat,lon],
            icon=folium.Icon(color=color,icon='plus',prefix='fa'),
            popup = folium.Popup(('Name: ' + str(name) + '<br>'
                    'Type: ' + str(typ) + '<br>'
                    'Total: ' + str(total) + '<br>'
                    'Occupied: ' + str(occupied) + '<br>'
                    'Vacant: ' + str(vacant) + '<br>'
                    'Last Updated: ' + str(last_updated) + '<br>'), max_width=300, min_width=200)
        ).add_to(icu_beds)


    icu_beds_noVent_df = pd.DataFrame(jsonObj['icu_beds_without_ventilator']).transpose()
    icu_beds_noVent_df['Name'] = icu_beds_noVent_df.index

    # Merge Beds Data with Hospital Locations
    mdf = pd.merge(icu_beds_noVent_df, df, on='Name', how='right').dropna() # Dataframe containing details of all hospitals with beds information

    # Assign a color based on the number of vacant beds
    mdf['marker_color'] = pd.cut(mdf['vacant'].astype(int), bins=10, 
                                  labels=['gray', 'darkred','red', 'lightred', 'orange', 'lightblue', 'blue', 'darkblue', 'lightgreen','green'])

    icu_beds_noVent = folium.FeatureGroup(name="ICU Beds w/o Ventilator", overlay=False)
    for name, typ, total, occupied, vacant, last_updated, lat, lon, color in zip(mdf.Name, mdf.type_x, mdf.total, mdf.occupied, mdf.vacant, mdf.last_updated_at, mdf.Latitude, mdf.Longitude, mdf.marker_color):
        folium.Marker(
            [lat,lon],
            icon=folium.Icon(color=color,icon='plus',prefix='fa'),
            popup = folium.Popup(('Name: ' + str(name) + '<br>'
                    'Type: ' + str(typ) + '<br>'
                    'Total: ' + str(total) + '<br>'
                    'Occupied: ' + str(occupied) + '<br>'
                    'Vacant: ' + str(vacant) + '<br>'
                    'Last Updated: ' + str(last_updated) + '<br>'), max_width=300, min_width=200)
        ).add_to(icu_beds_noVent)


    nonCOVID_icu_beds_df = pd.DataFrame(jsonObj['noncovid_icu_beds']).transpose()
    nonCOVID_icu_beds_df['Name'] = nonCOVID_icu_beds_df.index

    # Merge Beds Data with Hospital Locations
    mdf = pd.merge(nonCOVID_icu_beds_df, df, on='Name', how='right').dropna() # Dataframe containing details of all hospitals with beds information

    # Assign a color based on the number of vacant beds
    mdf['marker_color'] = pd.cut(mdf['vacant'].astype(int), bins=10, 
                                  labels=['gray', 'darkred','red', 'lightred', 'orange', 'lightblue', 'blue', 'darkblue', 'lightgreen','green'])

    nonCOVID_icu_beds = folium.FeatureGroup(name="Non-COVID ICU Beds", overlay=False)
    for name, typ, total, occupied, vacant, last_updated, lat, lon, color in zip(mdf.Name, mdf.type_x, mdf.total, mdf.occupied, mdf.vacant, mdf.last_updated_at, mdf.Latitude, mdf.Longitude, mdf.marker_color):
        folium.Marker(
            [lat,lon],
            icon=folium.Icon(color=color,icon='plus',prefix='fa'),
            popup = folium.Popup(('Name: ' + str(name) + '<br>'
                    'Type: ' + str(typ) + '<br>'
                    'Total: ' + str(total) + '<br>'
                    'Occupied: ' + str(occupied) + '<br>'
                    'Vacant: ' + str(vacant) + '<br>'
                    'Last Updated: ' + str(last_updated) + '<br>'), max_width=300, min_width=200)
        ).add_to(nonCOVID_icu_beds)

    #----------------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------------#
    covid_beds.add_to(m)
    icu_beds.add_to(m)
    ventilators.add_to(m)
    icu_beds_noVent.add_to(m)
    nonCOVID_icu_beds.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    return m._repr_html_()

if __name__ == '__main__':
    app.run(debug=True)
