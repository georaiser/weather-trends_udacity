#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 13:28:14 2020

@author: hellraiser
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 20:57:32 2020

@author: hellraiser
"""
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import preprocessing
import seaborn as sns
import numpy as np
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap
from itertools import chain

path=r''
cd=path+'csv/results-city_data.csv'
cds=path+'csv/results-city_data-Santiago.csv'
#cgd=path+'results-global_data.csv'

roll=20
res='10y'

#%% join Country & City
cityData=pd.read_csv(cd,sep=",")
cityData.dropna(inplace=True)

cityData["local"]=cityData['country']+[" "]+cityData['city']
cityData.sort_values("local", inplace = True) 
location=cityData.copy()
location=location.drop_duplicates(subset ="local", keep='first') 
location.reset_index(inplace = True, drop=True)
location.drop(['year', 'avg_temp'], axis=1, inplace = True)

#%% 
'''get Geo Localization'''
def geoloc(location):   
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="project1")
    
    lat=np.zeros(len(location), order='C')
    lon=np.zeros(len(location), order='C')
    for i in range(0, len(location)):
        try:
            locat=geolocator.geocode(list(location['local'].values)[i])
            lat[i]=locat.latitude
            lon[i]=locat.longitude
            print(i)
        except:
            lat[i]=np.nan
            lon[i]=np.nan
    location.drop(['city', 'country'], axis=1, inplace = True)        
    location['latitude']=lat
    location['longitude']=lon
    
    merged = pd.merge(location, cityData, on=['local'], how='inner')   
    merged.to_csv(path+'csv/results-city_data_location.csv', sep=" ", index=False)
    
#cityMerged=geoloc(location)
    
#%% 
cityData=pd.read_csv(path+'csv/results-city_data_location.csv',sep=" ")
cityData.dropna(inplace=True)
cityDataStgo=pd.read_csv(cds,sep=",")
#cityGlobalData=pd.read_csv(cgd,sep=",")

cityData["year"] = pd.to_datetime(cityData["year"], format="%Y")
cityData = cityData.set_index("year")
cityData=cityData.dropna(subset = ['avg_temp'])

cityDataStgo["year"] = pd.to_datetime(cityDataStgo["year"], format="%Y")
cityDataStgo = cityDataStgo.set_index("year")
cityDataStgo=cityDataStgo.dropna(subset = ['avg_temp'])

cityData["Year"] = cityData.index.year
cityDataStgo["Year"] = cityDataStgo.index.year
cityDataStgo['local']=cityDataStgo['country']+[" "]+cityDataStgo['city']
#%%
sns.set(rc={'figure.figsize':(12, 6)})
# locat instead location because deleting nan
## Histogram
pd.DataFrame(cityData, columns=['Year','local']).plot.hist(bins=25, alpha=0.5)  
#%%
def rollWin(Data, roll, res):

    slc1 =pd.DataFrame()
    slc2_roll =pd.DataFrame()
    locat=list(set(Data['local'].values))
    
    for l in locat:
        crit = Data['local'].map(lambda x: x==l)
        slc0=Data[crit]
        slc0=slc0.sort_values('Year') 
        slc=slc0.copy()['1860'::]
        slc['norm_temp']=(slc['avg_temp']-slc['avg_temp'].min())/(slc['avg_temp'].max()-slc['avg_temp'].min())
        #normalized_df=(df-df.mean())/df.std()
        # slc1 by locat
        slc1=slc1.append(slc)   
        
        slc2_year=slc[['avg_temp','norm_temp','Year']].resample("Y").mean()         
        slc2_year.dropna(inplace=True)
        
        slc2_year_roll = slc2_year.rolling(window = roll, center = True).mean()
        slc2_year_roll.dropna(inplace=True)
        
        try:
            slc2_year_roll["latitude"]=slc["latitude"][0]
            slc2_year_roll["longitude"]=slc["longitude"][0]
        except:
            pass
        
        slc2_roll=slc2_roll.append(slc2_year_roll)
          
    slc1_year=slc1[['avg_temp','norm_temp','Year']].resample("Y").mean()         
    slc1_year.dropna(inplace=True)
        
    slc1_year_roll = slc1_year.rolling(window = roll, center = True).mean()
    slc1_year_roll.dropna(inplace=True)
    
    slc1_year_roll_STD=slc1_year.rolling(window = roll, center = True).std()
    slc1_year_roll_STD.dropna(inplace=True)
    
    # Resample en time windows
    slc1_res=slc1[["avg_temp","norm_temp"]].resample(res).mean()
    
    return slc1, slc1_year, slc1_year_roll, slc1_year_roll_STD, slc1_res, slc2_roll

cityData, cityData_year, cityData_year_roll, cityData_year_roll_STD, cityData_res, cityData_roll = rollWin(cityData, roll, res) 
cityDataStgo, cityDataStgo_year, cityDataStgo_year_roll, cityDataStgo_year_roll_STD, cityDataStgo_res, cityDataStgo_roll = rollWin(cityDataStgo, roll, res) 

#%%
def figure1(data_year, data_year_roll, data_year_roll_STD):   
    fig, ax = plt.subplots()    
    ax.plot(data_year.index.year, data_year["avg_temp"], color='r', label='avg_temp')
    ax.plot(data_year_roll.index.year, data_year_roll["avg_temp"], color='b', label='avg_temp_roll')
    plt.fill_between(data_year_roll.index.year, (data_year_roll['avg_temp']-data_year_roll_STD['avg_temp']).values, 
                     (data_year_roll['avg_temp']+data_year_roll_STD['avg_temp']).values,alpha = 0.4, label='avg_temp_std')
    ax.set_xlabel('Year')
    ax.set_ylabel('Temperature')
    ax.set_title('Weather Trends - Rolling')
    plt.legend(loc=2)
    plt.show()
    
figure1(cityData_year, cityData_year_roll, cityData_year_roll_STD)
figure1(cityDataStgo_year, cityDataStgo_year_roll, cityDataStgo_year_roll_STD)

#%%
fig, ax = plt.subplots()    
ax.plot(cityData_year_roll.index.year, cityData_year_roll["norm_temp"], color='b', label='norm_temp_roll-Global')
ax.set_xlabel('Year')
ax.set_ylabel('Temperature Increase')
ax.set_title('Weather Trends - Global World - Rolling '+str(roll)+ ' years')
plt.legend(loc=2)

ax.plot(cityDataStgo_year_roll.index.year, cityDataStgo_year_roll["norm_temp"], color='r', label='norm_temp_roll-Santiago_Chile')
ax.set_xlabel('Year')
ax.set_ylabel('Temperature Increase')
#ax.set_title('Weather Trends - Santiago, Chile - Roll '+str(roll))
plt.legend(loc=2)
plt.show()
#%%
fig, ax = plt.subplots()    
ax.plot(cityData_year.index.year, cityData_year["norm_temp"], color='b', label='norm_temp-Global')
ax.set_xlabel('Year')
ax.set_ylabel('Temperature Increase')
ax.set_title('Weather Trends - Global World')
plt.legend(loc=2)

ax.plot(cityDataStgo_year.index.year, cityDataStgo_year["norm_temp"], color='r', label='norm_temp-Santiago_Chile')
ax.set_xlabel('Year')
ax.set_ylabel('Temperature Increase')
#ax.set_title('Weather Trends - Santiago, Chile - Roll '+str(roll))
plt.legend(loc=2)
plt.show()
#%%
fig, ax = plt.subplots()    
ax.plot(cityData_res.index.year, cityData_res["avg_temp"], color='b', label='avg_temp_res-Global')
ax.set_xlabel('Year')
ax.set_ylabel('Temperature')
ax.set_title('Weather Trends - Global World - Resample '+str(res)+ ' years')
plt.legend(loc=2)
  
ax.plot(cityDataStgo_res.index.year, cityDataStgo_res["avg_temp"], color='r', label='avg_temp_res-Santiago_Chile')
ax.set_xlabel('Year')
ax.set_ylabel('Temperature')
#ax.set_title('Weather Trends - Santiago, Chile - Resample '+str(res))
plt.legend(loc=2)
plt.show()

#%%
'''Basemap'''
def draw_map(m, scale=0.5):
    # draw a shaded-relief image
    m.shadedrelief(scale=scale)    
    # lats and longs are returned as a dictionary
    lats = m.drawparallels(np.linspace(-90, 90, 13))
    lons = m.drawmeridians(np.linspace(-180, 180, 13))
    # keys contain the plt.Line2D instances
    lat_lines = chain(*(tup[1][0] for tup in lats.items()))
    lon_lines = chain(*(tup[1][0] for tup in lons.items()))
    all_lines = chain(lat_lines, lon_lines)    
    # cycle through these lines and set the desired style
    for line in all_lines:
        line.set(linestyle='-', alpha=0.3, color='w')

#%%
year=cityData.loc['2013'][['latitude','longitude','avg_temp','local','norm_temp']]

fig = plt.figure(figsize=(14,6), edgecolor='w')
m = Basemap(projection='cyl', resolution=None,
            llcrnrlat=-90, urcrnrlat=90,
            llcrnrlon=-180, urcrnrlon=180, )

fig.suptitle('Global World Temperature Year '+ str(year.index.year[0]), fontsize=15)
plot = plt.scatter(year.longitude.values, year.latitude.values, c=year.norm_temp.values, s=70, cmap='YlOrBr')
fig.colorbar(plot)
#plt.xlim(year['longitude'].min()-25, year['longitude'].max()+25)
#plt.ylim(year['latitude'].min()-25, year['latitude'].max()+25)
plt.xlabel('Longitude',fontsize=10)
plt.ylabel('Latitude',fontsize=10)
draw_map(m)
plt.show()

#%%
'''video for each year'''
fig = plt.figure(figsize=(14,6))
m = Basemap(projection='cyl', resolution=None,
            llcrnrlat=-90, urcrnrlat=90,
            llcrnrlon=-180, urcrnrlon=180, )

y=list(cityData_roll.index.year.unique())
y.sort()
def animate(i):    
    data = cityData_roll.loc[str(y[i])][['latitude','longitude', "norm_temp"]] #select data range
    plot = plt.scatter(data=data, x="longitude", y="latitude", c="norm_temp", s=100, cmap='YlOrBr')
    plt.xlabel('Longitude',fontsize=10)
    plt.ylabel('Latitude',fontsize=10)
    plt.title('Normalized temperature increase - Rolling '+ str(roll) + ' Years '+ str(cityData_roll.index[i].year),fontsize=15) 
    print(y[i])
fig.colorbar(plot)
draw_map(m)
#ani = animation.FuncAnimation(fig, animate, frames=len(y), repeat=True)
#ani.save('Temperature.gif', writer='imagemagick')

#%%












