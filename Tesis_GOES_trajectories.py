# -*- coding: utf-8 -*-
import numpy as np
import netCDF4 as nc
from pyproj import Proj
from matplotlib import pyplot as plt
from scipy import ndimage
from scipy.ndimage.measurements import center_of_mass
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
import ast

## LEER ARCHIVOS DE LAS BANDAS ##

#path_CH01 = '/media/cabonillao/Disco/SIATA/Datos/Netcdf_GOES/ABI_L1b/20180920/OR_ABI-L1b-RadF-M3C01_G16_s20182771915378_e20182771926144_c20182771926189.nc'
#path_CH02 = '/media/cabonillao/Disco/SIATA/Datos/Netcdf_GOES/ABI_L1b/20180920/OR_ABI-L1b-RadF-M3C02_G16_s20182771915378_e20182771926144_c20182771926187.nc'
#path_CH04 = '/media/cabonillao/Disco/SIATA/Datos/Netcdf_GOES/ABI_L1b/20180920/OR_ABI-L1b-RadF-M3C04_G16_s20182771915378_e20182771926144_c20182771926169.nc'

#path_CH01 =  "/home/nacorreasa/Maestria/Datos_Tesis/GOES/OR_ABI-L1b-RadF-M3C01_G16_s20183371445354_e20183371456120_c20183371456165.nc"
path_CH01 = "/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_semana/OR_ABI-L1b-RadF-M3C01_G16_s20182441100364_e20182441111131_c20182441111180.nc"
path_CH012 =  "/home/nacorreasa/Maestria/Datos_Tesis/GOES/OR_ABI-L1b-RadF-M3C01_G16_s20183371400354_e20183371411121_c20183371411170.nc"


## LEER SHAPE ##
shape = '/home/nacorreasa/Maestria/Semestre1/Analisis_Geoespacial/MuchosShapes/AMVA/'

## DEFINIENDO LAS FUNCIONES A UTILIZAR ##

def find_nearest(array, value):                          ## PARA ENCONTRAR LA CASILLA MAS CERCANA
    idx = (np.abs(array-value)).argmin()
    return array[idx], idx

def Posiciones(archivo, limites_zona):                   ## RELACIONAR ESAS CASILLAS CON LAS LATITUDES REQUERIDAS
    archivo = nc.Dataset(archivo)
    h = archivo.variables['goes_imager_projection'].perspective_point_height
    x = archivo.variables['x'][:]
    y = archivo.variables['y'][:]
    lon_0 = archivo.variables['goes_imager_projection'].longitude_of_projection_origin
    lat_0 = archivo.variables['goes_imager_projection'].latitude_of_projection_origin
    sat_sweep = archivo.variables['goes_imager_projection'].sweep_angle_axis
    archivo.close()
    x = x * h
    y = y * h
    p = Proj(proj='geos', h=h, lon_0=lon_0, swee=sat_sweep)
    xx, yy = np.meshgrid(x, y)
    print xx, yy

    lons, lats = p(xx[:, :], yy[:, :], inverse=True)
    lons = np.ma.array(lons)
    lons[lons == 1.00000000e+30] = np.ma.masked
    lats = np.ma.array(lats)
    lats[lats == 1.00000000e+30] = np.ma.masked

    mid = np.shape(lons)[0]/2
    lon_O = find_nearest(lons[mid, :], limites_zona[0])[1]
    lon_E = find_nearest(lons[mid, :], limites_zona[1])[1]
    lat_N = find_nearest(lats[:, mid], limites_zona[2])[1]
    lat_S = find_nearest(lats[:, mid], limites_zona[3])[1]
    return lons, lats, lon_O, lon_E, lat_N, lat_S

def Obtiene_Lon_Lat_Fr_Rad(ruta, dicc):                       ## PARA OBTENER LA INFORMACION ACOTADA A LA REGION DE INTERES
    limites_zona = dicc
    archivo = nc.Dataset(ruta)
    h = archivo.variables['goes_imager_projection'].perspective_point_height
    x = archivo.variables['x'][limites_zona[0]:limites_zona[1]]
    y = archivo.variables['y'][limites_zona[2]:limites_zona[3]]
    lon_0 = archivo.variables['goes_imager_projection'].longitude_of_projection_origin
    lat_0 = archivo.variables['goes_imager_projection'].latitude_of_projection_origin
    sat_sweep = archivo.variables['goes_imager_projection'].sweep_angle_axis
    d = (archivo.variables['earth_sun_distance_anomaly_in_AU'][:])**2
    esun = archivo.variables['esun'][:]

    rad = archivo.variables['Rad'][limites_zona[2]:limites_zona[3], limites_zona[0]:limites_zona[1]]
    fr = (rad*np.pi*d)/esun
    fr[fr[:, :] < 0] = 0
    fr[fr[:, :] > 1] = 1
    fr = np.sqrt(fr)
    fr = fr*100.0
    archivo.close()
    x = x * h
    y = y * h
    p = Proj(proj='geos', h=h, lon_0=lon_0, swee=sat_sweep)
    xx, yy = np.meshgrid(x,y)
    lons, lats = p(xx, yy, inverse=True)
    lons = np.ma.array(lons)
    lons[lons == 1.00000000e+30] = np.ma.masked
    lats = np.ma.array(lats)
    lats[lats == 1.00000000e+30] = np.ma.masked

    return lons, lats, rad

def MapaUnitario(data, lat, lon,  cmap, titulo):            ## PARA TENER UN SOLO MAPA DE LA REGION

    plt.close('all')
    fig = plt.figure(figsize=(22, 10))

    m = Basemap(projection='merc', llcrnrlat=np.min(lat), urcrnrlat=np.max(lat),
                llcrnrlon=np.min(lon), urcrnrlon=np.max(lon), resolution='i', lat_ts=20)
    m.readshapefile(shapefile=shape + 'AreaMetropolitana', name='AreaMetropolitana', color='k', linewidth=1.5)
    x, y = m(lon, lat)
    cs = m.contourf(x, y, data, cmap=cmap, alpha=0.5, edgecolors='none')

    parallels = np.arange(np.min(lat), np.max(lat) + 1, 0.3)
    m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
    meridians = np.arange(np.min(lon), np.max(lon) + 1, 0.3)
    m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)

    plt.subplots_adjust(wspace=0.3, hspace=1.1, left=0.1, bottom=0.085, right=0.92, top=0.95)

    cbar_ax = fig.add_axes([0.125, 0.03, 0.78, 0.015])
    cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal', format="%.2f")
    cbar.set_label(titulo, fontsize=14,  color='gray')
    cbar.outline.set_edgecolor('gray')

def MapaUnitarioCentroide(data,  lat, lon, titulo, Lo, La):            ## PARA TENER UN SOLO MAPA DE LA REGION CON SUS CENTROIDES Y CLUSTERS

    plt.close('all')
    fig = plt.figure(figsize=(10, 8))

    map =Basemap(projection='merc', llcrnrlat=np.min(lat), urcrnrlat=np.max(lat),
                llcrnrlon=np.min(lon), urcrnrlon=np.max(lon), resolution='i', lat_ts=20)
    parallels = np.arange(np.min(lat), np.max(lat) + 1, 0.3)
    map.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
    meridians = np.arange(np.min(lon), np.max(lon) + 1, 0.3)
    map.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)
    map.readshapefile(shapefile=shape + 'AreaMetropolitana', name='AreaMetropolitana', color='k', linewidth=1.5)

    x, y = map(lons, lats)
    cs = map.contourf(x, y, data, cmap='binary', alpha=0.5, edgecolors='none')
    lon_presa, lat_presa = map(Lo, La)
    map.plot(lon_presa, lat_presa, 'bo', markersize=6, color='r')

    cbar_ax = fig.add_axes([0.125, 0.03, 0.78, 0.015])
    cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal', format="%.2f")
    cbar.set_label(titulo, fontsize=14,  color='gray')
    cbar.outline.set_edgecolor('gray')

    plt.show()

def LimitesZonas(resolucion, zonas, path_CH):                                   ## PARA OBTENER LA LISTA CON LOS LIMITES DE LA ZONA

    if resolucion == 0.5:
        for i in zonas.keys():
            lons, lats, lon_O, lon_E, lat_N, lat_S = Posiciones(path_CH, zonas[i])
            print (u"Posiciones dada una resolución espacial de 0.5 km")
            print ("Para la zona " + i + '\n'
                   u"La posición para la longitud occidental es : " + str(lon_O-1) + '\n' +
                   u"La posición para la longitud oriental es : " + str(lon_E) + '\n' +
                   u"La posición para la latitud norte es : " + str(lat_N-1) + '\n' +
                   u"La posición para la latitud sur es : " + str(lat_S) +'\n' +
                   u"inclúyalas así en el diccionario de posiciones:"  + '\n'
                   u"[" + str(lon_O-1) + ',' + str(lon_E) + ',' + str(lat_N-1) + ',' + str(lat_S) + "]")
        DiccionarioPos =   u"[" + str(lon_O-1) + ',' + str(lon_E) + ',' + str(lat_N-1) + ',' + str(lat_S) + "]"
        DiccionarioPos = ast.literal_eval(DiccionarioPos)
    elif resolucion == 1:
        for i in zonas.keys():
            lons, lats, lon_O, lon_E, lat_N, lat_S = Posiciones(path_CH, zonas[i])
            print (u"Posiciones dada una resolución espacial de 1 km")
            print ("Para la zona " + i + '\n'
                                         u"La posición para la longitud occidental es : " + str(lon_O - 1) + '\n' +
                   u"La posición para la longitud oriental es : " + str(lon_E) + '\n' +
                   u"La posición para la latitud norte es : " + str(lat_N - 1) + '\n' +
                   u"La posición para la latitud sur es : " + str(lat_S) + '\n' +
                   u"inclúyalas así en el diccionario de posiciones:" + '\n'
                                                                        u"[" + str(lon_O - 1) + ',' + str(
                lon_E) + ',' + str(lat_N - 1) + ',' + str(lat_S) + "]")
        DiccionarioPos =   u"[" + str(lon_O-1) + ',' + str(lon_E) + ',' + str(lat_N-1) + ',' + str(lat_S) + "]"
        DiccionarioPos = ast.literal_eval(DiccionarioPos)
    elif resolucion == 2:
        for i in zonas.keys():
            lons, lats, lon_O, lon_E, lat_N, lat_S = Posiciones(path_CH, zonas[i])
            print (u"Posiciones dada una resolución espacial de 2 km")
            print ("Para la zona " + i + '\n'
                   u"La posición para la longitud occidental es : " + str(lon_O-1) + '\n' +
                   u"La posición para la longitud oriental es : " + str(lon_E) + '\n' +
                   u"La posición para la latitud norte es : " + str(lat_N-1) + '\n' +
                   u"La posición para la latitud sur es : " + str(lat_S) +'\n' +
                   u"inclúyalas así en el diccionario de posiciones:"  + '\n'
                   u"[" + str(lon_O-1) + ',' + str(lon_E) + ',' + str(lat_N-1) + ',' + str(lat_S) + "]")
        DiccionarioPos =   u"[" + str(lon_O-1) + ',' + str(lon_E) + ',' + str(lat_N-1) + ',' + str(lat_S) + "]"
        DiccionarioPos = ast.literal_eval(DiccionarioPos)
    return DiccionarioPos


## DELIMITAR LA ZONA  EN COORDENADAS CARTESIANAS ##

latu = 6.5900
latd = 5.9300
lono = -75.85
lone = -75.07

zonas = {'Valle_de_Aburra': [-75.85, -75.07, 6.5900,  5.9300]}
#,'TropicalVA':[-76.600373,-74.444992,7.2335,5.11830]}
# #,'Colombia':[-80,-65,14,-5],'Antioquia':[-77.9,-73,9.2,5],
# 'Valle_de_Aburra':[-76.600373,-74.444992,7.2335,5.11830]}
# 'Ituango':[-76.61578111504166, -74.44489614355325, 7.236707206816583, 5.123934256818043]

## DE ACUERDO AL CANAL, ESCOGER UNA ALTERNATIVA DE IMPRESION COMENTAR Y DESCOMENTAR (VERSION ORIGINAL, GUARDAR ESTE PEDAZO)##
for i in zonas.keys():
    # lons, lats, lon_O, lon_E, lat_N, lat_S = Posiciones(path_CH02, zonas[i])
    # print (u"Posiciones dada una resolución espacial de 0.5 km")
    # print ("Para la zona " + i + '\n'
    #        u"La posición para la longitud occidental es : " + str(lon_O-1) + '\n' +
    #        u"La posición para la longitud oriental es : " + str(lon_E) + '\n' +
    #        u"La posición para la latitud norte es : " + str(lat_N-1) + '\n' +
    #        u"La posición para la latitud sur es : " + str(lat_S) +'\n' +
    #        u"inclúyalas así en el diccionario de posiciones:"  + '\n'
    #        u"[" + str(lon_O-1) + ',' + str(lon_E) + ',' + str(lat_N-1) + ',' + str(lat_S) + "]")
    lons, lats, lon_O,lon_E,lat_N,lat_S = Posiciones(path_CH012, zonas[i])
    print (u"Posiciones dada una resolución espacial de 1 km")
    print ("Para la zona " + i + '\n'
           u"La posición para la longitud occidental es : " + str(lon_O-1) + '\n' +
           u"La posición para la longitud oriental es : " + str(lon_E) + '\n' +
           u"La posición para la latitud norte es : " + str(lat_N-1) + '\n' +
           u"La posición para la latitud sur es : " + str(lat_S) +'\n' +
           u"inclúyalas así en el diccionario de posiciones:"  + '\n'
           u"[" + str(lon_O-1) + ',' + str(lon_E) + ',' + str(lat_N-1) + ',' + str(lat_S) + "]")
    # lons, lats, lon_O, lon_E, lat_N, lat_S = Posiciones(path_CH04,zonas[i])
    # print (u"Posiciones dada una resolución espacial de 2 km")
    # print ("Para la zona " + i + '\n'
    #        u"La posición para la longitud occidental es : " + str(lon_O-1) + '\n' +
    #        u"La posición para la longitud oriental es : " + str(lon_E) + '\n' +
    #        u"La posición para la latitud norte es : " + str(lat_N-1) + '\n' +
    #        u"La posición para la latitud sur es : " + str(lat_S) +'\n' +
    #        u"inclúyalas así en el diccionario de posiciones:"  + '\n'
    #        u"[" + str(lon_O-1) + ',' + str(lon_E) + ',' + str(lat_N-1) + ',' + str(lat_S) + "]")

##------------------------------------------PRIMERA IMAGEN RESOLUCION DE 1 KM-----------------------------------------##

## EJECUTAR FUNCION PARA OBTENER LA BANDA ACOTADA A LA REGION DE INTERES ##
limzon = LimitesZonas(1, zonas, path_CH01)
lons, lats, rad = Obtiene_Lon_Lat_Fr_Rad(path_CH01, limzon)


## ENMASCARANDO LA RADIACION CON DETERMINADO UMBRAL Y OBTENIENDO UNA MATRIZ BINARIA##

umbral = 300                                       ## ESCOGER UN UMBRAL A DISCRECIÓN

radm = np.ma.masked_where(rad < umbral, rad)     ## ENMASCARADA

radbi = (rad > umbral).astype(int)               ## BINARIA

## PONIENDO UN MAPA A LA IMAGEN ##


c1 = plt.imshow(rad)
c2 = plt.imshow(radm)

MapaUnitario(radm, lats, lons,  'rainbow_r', "rad")
MapaUnitario(radbi, lats, lons,  'binary', "rad")


##APLICANDO EL CLUSTERING A LA PRIMERA IMAGEN YE ENCONTRANDO CENTROIDES Y AREAS##

labels, numobjects = ndimage.label(radbi)                                     ## CREA OBJETOS CON DIFERENTES LABEL

centers = center_of_mass(labels, labels=labels, index=range(1, numobjects+1)) ## OBTIENE LOS CENTROS DE MASA

surface_areas = np.bincount(labels.flat)[1:]                                  ## OBTIENE LAS ÁREAS EN TÉRMINOS DE CANT.PIXELES

dx = abs(lone - lono) / radbi.shape[1]
dy = abs(latu - latd) / radbi.shape[0]

centers = np.array(centers)

La = np.array(latu-(centers[:, 0]-0.5)*dy)
Lo = np.array(lono+(centers[:, 1]-0.5)*dx)


MapaUnitarioCentroide(radbi,  lats, lons, "rad-center", Lo, La)


plt.imshow(labels)
#plt.scatter(centers[:, 1], centers[:, 0], facecolor='w')
plt.scatter(Lo, La, facecolor='c')



##------------------------------------------SEGUNDA IMAGEN RESOLUCION DE 1 KM-----------------------------------------##

## EJECUTAR LAS FUNCIONES PARA OBTENER LA BANDA ACOTADA A LA REGION DE INTERES ##
limzon2 = LimitesZonas(1, zonas, path_CH012)

lons, lats, rad2 = Obtiene_Lon_Lat_Fr_Rad(path_CH012, limzon2)


## ENMASCARANDO LA RADIACION CON DETERMINADO UMBRAL Y OBTENIENDO UNA MATRIZ BINARIA##

umbral = 300                                       ## ESCOGER UN UMBRAL A DISCRECIÓN

radm2 = np.ma.masked_where(rad2 < umbral, rad2)     ## ENMASCARADA

radbi2 = (rad2 > umbral).astype(int)               ## BINARIA

## PONIENDO UN MAPA A LA IMAGEN ##

MapaUnitario(radm2, lats, lons,  'rainbow_r', "rad")
MapaUnitario(radbi2, lats, lons,  'binary', "rad")


##APLICANDO EL CLUSTERING A LA PRIMERA IMAGEN YE ENCONTRANDO CENTROIDES Y AREAS##

labels2, numobjects2 = ndimage.label(radbi2)                                     ## CREA OBJETOS CON DIFERENTES LABEL

centers2 = center_of_mass(labels2, labels=labels2, index=range(1, numobjects2+1))## OBTIENE LOS CENTROS DE MASA

surface_areas2 = np.bincount(labels2.flat)[1:]                                   ## OBTIENE LAS ÁREAS EN TÉRMINOS DE CANT.PIXELES

dx = abs(lone - lono) / radbi.shape[1]
dy = abs(latu - latd) / radbi.shape[0]

centers2 = np.array(centers2)

La = np.array(latu-(centers2[:, 0]-0.5)*dy)
Lo = np.array(lono+(centers2[:, 1]-0.5)*dx)

MapaUnitarioCentroide(radbi2,  lats, lons, "rad-center", Lo, La)

plt.imshow(labels2)
#plt.scatter(centers[:, 1], centers[:, 0], facecolor='w')
plt.scatter(Lo, La, facecolor ='c')

