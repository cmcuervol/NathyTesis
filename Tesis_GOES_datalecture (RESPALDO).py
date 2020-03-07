# -*- coding: utf-8 -*-
from numpy import *
import netCDF4 as nc
from pyproj import Proj
import ast
from netCDF4 import Dataset
from netcdftime import utime
from datetime import datetime, timedelta
import datetime as dt
import os

path_directory = "/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_semana/"
Borrar_Nocturnas = 'si'                ## NOTA IMPORTANTE:  Para borrarlas debe ser: 'no'

Name_nc = 'GOES_VA_normalizado'
atardecer = '18:00'
amanecer = '06:00'
Banda = 01
resolucion = '1 Km'
fec_ini = '2018-09-01'
fec_fin = '2018-09-02'



# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
                                        # No cambiar nada en adelante
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

fi  = dt.datetime.strptime(fec_ini, '%Y-%m-%d')
ff  = dt.datetime.strptime(fec_fin, '%Y-%m-%d')

def retorna_fecha_hora_info(ruta):
    #try:
    #    fecha = ruta[ruta.find('c2019')+1:ruta.find('c2019')+12]
    #except:
    fecha = ruta[ruta.find('c2018')+1:ruta.find('c2018')+12]
    fecha = dt.datetime.strptime(fecha, '%Y%j%H%M')
    fecha_utc = fecha.strftime('%Y/%m/%d/ %H:%M')
    fecha_local = fecha - dt.timedelta(hours=5)
    fecha_local = fecha_local.strftime('%Y/%m/%d %H:%M')
    fecha_path = fecha.strftime('%Y%m%d')
    fecha = fecha.strftime('%Y%m%d%H%M')
    return fecha_utc, fecha_path, fecha , fecha_local

def borrar_imagenes_nocturnas (path_directory, amanecer, atardecer):
    for filename in os.listdir(path_directory):
        if filename.endswith(".nc") :
            fecha_utc, fecha_path, fecha, fecha_local = retorna_fecha_hora_info(path_directory + filename)
            local_hour = dt.datetime.strptime(fecha_local[11:], '%H:%M').time()
            if local_hour > dt.datetime.strptime(atardecer, '%H:%M').time() or local_hour < dt.datetime.strptime(amanecer, '%H:%M').time():
                os.system('rm ' + path_directory + filename)
                print ('Borrando todos los archivos nocturnos')
            else:
                print ('No se econtraron archivos para borrar')

if Borrar_Nocturnas == 'no':
    borrar_imagenes_nocturnas(path_directory, amanecer, atardecer)    ## Ejecutando las dos funciones anteriores
else:
    pass

def daterange(start_date, end_date):                                  ## PARA LA SELECCION DE LAS CARPETAS DE INTERES
    delta = timedelta(days=1)
    while start_date <= end_date:
        yield start_date
        start_date += delta

Folders = []
for single_date in daterange(fi, ff):
    Folders.append(single_date.date().strftime('%Y%m%d'))

                                                                      ## DELIMITAR EL TIEMPO DE INTERES
def Obtener_fecha_hora_de_Archvos (path_directory):
    local_hour = []
    local_date_str = []
    for filename in os.listdir(path_directory):
        if filename.endswith(".nc") :
            fecha_utc, fecha_path, fecha, fecha_local = retorna_fecha_hora_info(path_directory + filename)
            local_hour.append(dt.datetime.strptime(fecha_local, '%Y/%m/%d %H:%M'))
            local_date_str.append(fecha_local)
    return local_date_str, local_hour

fechas, time = Obtener_fecha_hora_de_Archvos (path_directory)
fechas_dt = [dt.datetime.strptime(date[0:10], '%Y/%m/%d') for date in fechas]


def Listador(directorio, inicio, final):
    lf = []
    lista = os.listdir(directorio)
    for i in lista:
        if i.startswith(inicio) and i.endswith(final):
            lf.append(i)
    return lf

archivos_temp = Listador(path_directory, 'OR_ABI', '.nc')    ## Esto es una lista con nombre de archivos con los q se trabajara
archivos_temp.sort()

archivos = []                                                ## Se acotan los archivos dentro de la fi y la ff seleccionada

for i in range(len(fechas_dt)):
    if (fechas_dt[i] <= ff) and (fechas_dt[i] >= fi):
        archivos.append(archivos_temp[i])
    else:
        pass

def find_nearest(array, value):                              ## PARA ENCONTRAR LA CASILLA MAS CERCANA
    idx = (abs(array-value)).argmin()
    return array[idx], idx

def Posiciones(archivo, limites_zona):                        ## RELACIONAR ESAS CASILLAS CON LAS LATITUDES REQUERIDAS
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
    xx, yy = meshgrid(x, y)
    print xx, yy

    lons, lats = p(xx[:, :], yy[:, :], inverse=True)
    lons = ma.array(lons)
    lons[lons == 1.00000000e+30] = ma.masked
    lats = ma.array(lats)
    lats[lats == 1.00000000e+30] = ma.masked

    mid = shape(lons)[0]/2
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
    fr = (rad*pi*d)/esun
    fr[fr[:, :] < 0] = 0
    fr[fr[:, :] > 1] = 1
    fr = sqrt(fr)
    fr = fr*100.0
    archivo.close()
    x = x * h
    y = y * h
    p = Proj(proj='geos', h=h, lon_0=lon_0, swee=sat_sweep)
    xx, yy = meshgrid(x,y)
    lons, lats = p(xx, yy, inverse=True)
    lons = ma.array(lons)
    lons[lons == 1.00000000e+30] = ma.masked
    lats = ma.array(lats)
    lats[lats == 1.00000000e+30] = ma.masked

    return lons, lats, rad

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

limzon = [5328, 5416, 4698, 4771] # LimitesZonas(1, zonas, path_directory+archivos[0])       ## Ejecutar las funciones para tener la banda acotada a la región de interés y sus latitudes y longitudes
lons, lats, rad = Obtiene_Lon_Lat_Fr_Rad(path_directory+archivos[0], limzon)

## Iniciar variables
ntime    = len(archivos)
nlat     = shape(lats)[0]
nlon     = shape(lons)[1]
nrad     = shape(rad)

## Se crean matrices de ceros con forme a la forma  de cada variable
Radiancias  = zeros((len(archivos), shape(rad)[0], shape(rad)[1]))


def Obtener_fecha_hora_de_Archvos (path_directory, archivos):
    local_hour = []
    local_date_str = []
    for i in range(len(archivos)):
        fecha_utc, fecha_path, fecha, fecha_local = retorna_fecha_hora_info(path_directory + archivos[i])
        local_hour.append(dt.datetime.strptime(fecha_local, '%Y/%m/%d %H:%M'))
        local_date_str.append(fecha_local)
    return local_date_str, local_hour

fechas, time = Obtener_fecha_hora_de_Archvos (path_directory, archivos)

for i  in range(len(archivos)):
    ## Varibales temporales
    lons_temp, lats_temp, Radiancias_temp = Obtiene_Lon_Lat_Fr_Rad(path_directory + archivos[i], limzon)
    del lons_temp, lats_temp

    ## Asignar a variables finales
    Radiancias [i,:, :] = Radiancias_temp[:, :]

cdftime = utime('hours since 2018-01-01 00:00:0.0')
date    = [cdftime.date2num(i) for i in time]

def retorna_scalefactor_y_addoffset_latlon(dataset,bits):         ## Nor maliza los valores de las variables
    import numpy as np
    max_o = np.max(dataset)
    min_o = np.min(dataset)
    scale_factor = (max_o - min_o) / (2**bits)
    add_offset = min_o
    return scale_factor, add_offset

# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
                                        # Crear netCDF
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

## Crear el nuevo archivo nc
nw = Dataset(path_directory + Name_nc+'.nc', 'w', format='NETCDF4')

## Definir dimensiones locativas
ncdim_lat    = nw.createDimension('nlat',    nlat)
ncdim_lon    = nw.createDimension('nlon',    nlon)
ncdim_time   = nw.createDimension('ntime',   ntime)


# Crear variables locativas
ncvar_lat  = nw.createVariable('lat',  'f8', ('nlat','nlon'), zlib=True, complevel=9)
ncvar_lon  = nw.createVariable('lon',  'f8', ('nlat','nlon'), zlib=True, complevel=9)
ncvar_time = nw.createVariable('time', 'f8', ('ntime',))

ncvar_Radiancias = nw.createVariable('Radiancias', 'f8', ('ntime',  'nlat', 'nlon'), zlib=True, complevel=9)

print 'netCDF variables created'

## Agregar unidades a las variables
ncvar_lat .units = 'Degrees north'
ncvar_lon .units = 'Degrees east'
ncvar_time.units = 'Hours since 2018-01-01'

ncvar_Radiancias.units = 'W/ m 2 •sr• μm'

## Rangos validos de las variables

ncvar_lon.valid_range = [0, 2048]
ncvar_lon.FillValue   = 2049
ncvar_lat.valid_range = [0, 2048]
ncvar_lat.FillValue   = 2049
ncvar_Radiancias.valid_range = [0, 2048]
ncvar_Radiancias.fill_value  = 2049

## Factores de escala
ncvar_lon.scale_factor, ncvar_lon.add_offset = retorna_scalefactor_y_addoffset_latlon(lons, 11)
ncvar_lat.scale_factor, ncvar_lat.add_offset = retorna_scalefactor_y_addoffset_latlon(lats, 11)
ncvar_lat.scale_factor, ncvar_lat.add_offset = retorna_scalefactor_y_addoffset_latlon(Radiancias, 11)

## Agregar nombres largos
ncvar_lat .longname = 'Array of latitude values at the center of the grid box'
ncvar_lon .longname = 'Array of longitude values at the center of the grid box'
ncvar_time.longname = 'Hours since 2018-01-01'
ncvar_Radiancias.longname = 'Radiance'

nw.title =  'GOES para el Valle de Aburrá-Banda:' +str(Banda)

nw.spatial_resolution = resolucion

nw.metadatos =  "https://www.goes-r.gov/multimedia/dataAndImageryImagesGoes-16.html"

# Agregar los datos al archivo
ncvar_time[:] = date
ncvar_lat [:] = lats
ncvar_lon [:] = lons

print '******************************************'
print '    writing variables in netCDF file '
print '******************************************'
ncvar_Radiancias [:, :, :] = Radiancias

# Si no cierra el archivo es como dejar la BD abierta... se lo tira!
nw.close()

print 'Hemos terminado'
