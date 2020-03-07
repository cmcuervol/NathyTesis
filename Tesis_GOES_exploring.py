# -*- coding: utf-8 -*-
from numpy import *
import netCDF4 as nc
from netCDF4 import Dataset
import datetime
from pyproj import Proj
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')
from   pyPdf import PdfFileWriter, PdfFileReader
import os

##------------------------------- PARAMETROS INICIALES---------------------------- ##
# a =  Dataset('/media/nacorreasa/NATHALIACOR/GOES_nc_RECORTADOS_C01_2018/20180101_01'
#              '/OR_ABI-L1b-RadF-M3C01_G16_s20180011030390_e20180011041157_c20180011041200.nc')
a =  Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_RECORTADOS_C02_20180101_20180626'
             '/20180112_02/OR_ABI-L1b-RadF-M3C02_G16_s20180121600417_e20180121611184_c20180121611223.nc')

Path_Save =  '/home/nacorreasa/Maestria/Datos_Tesis/GOES/Graficas/'
path_directory = '/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_prueba/'
fec_ini = '2018-09-01'
fec_fin = '2018-09-01'


##------------------------------- DATOS DEL netCDF CREADO---------------------------- ##
def Explora_NetCDF(ruta):

    archivo = nc.Dataset(ruta)

    latitud = archivo.variables['lat'][:]
    longitud = archivo.variables['lon'][:]-360.0

    tiempo = archivo.variables['time']
    fechas = nc.num2date(tiempo[:],units=tiempo.units)
    for i in range(len(fechas)):
        fechas[i] = datetime.datetime.strftime(fechas[i], '%Y-%m-%d %H:%M')

    tiempo = fechas

    archivo.close()

    #print ("Las latitudes están acotades entre: {0} y {1}".format(str(min(latitud)),str(max(latitud))))
    #print ("Las longitudes están acotades entre: {0} y {1}".format(str(min(longitud)),str(max(longitud))))
    print ("El periodo de tiempo es el comprendido entre: {0} y {1}".format(tiempo[0],tiempo[-1]))

    return latitud, longitud, tiempo

Lat, Lon, Tiempo = Explora_NetCDF('/home/nacorreasa/Downloads/ENERO_PRUEBA.nc')

Tiempo = [w.replace(' ', '_') for w in Tiempo]
Tiempo = [w.replace(':', '-') for w in Tiempo]

##------------------------------- DATOS CRUDOS DE LA CARPETA DE ALMACENAMIENTO ---------------------------- ##
fi  = datetime.datetime.strptime(fec_ini, '%Y-%m-%d')
ff  = datetime.datetime.strptime(fec_fin, '%Y-%m-%d')

def retorna_fecha_hora_info(ruta):
    #try:
    #    fecha = ruta[ruta.find('c2019')+1:ruta.find('c2019')+12]
    #except:
    fecha = ruta[ruta.find('c2018')+1:ruta.find('c2018')+12]
    fecha = datetime.datetime.strptime(fecha, '%Y%j%H%M')
    fecha_utc = fecha.strftime('%Y/%m/%d/ %H:%M')
    fecha_local = fecha - datetime.timedelta(hours=5)
    fecha_local = fecha_local.strftime('%Y/%m/%d %H:%M')
    fecha_path = fecha.strftime('%Y%m%d')
    fecha = fecha.strftime('%Y%m%d%H%M')
    return fecha_utc, fecha_path, fecha , fecha_local

def Obtener_fecha_hora_de_Archvos (path_directory):
    local_hour = []
    local_date_str = []
    for filename in os.listdir(path_directory):
        if filename.endswith(".nc") :
            fecha_utc, fecha_path, fecha, fecha_local = retorna_fecha_hora_info(path_directory + filename)
            local_hour.append(datetime.datetime.strptime(fecha_local, '%Y/%m/%d %H:%M'))
            local_date_str.append(fecha_local)
    return local_date_str, local_hour

fechas, time = Obtener_fecha_hora_de_Archvos (path_directory)
fechas_dt = [datetime.datetime.strptime(date[0:10], '%Y/%m/%d') for date in fechas]

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

limzon = [5328, 5416, 4698, 4771]


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

def Obtener_fecha_hora_de_Archvos (path_directory, archivos):
    local_hour = []
    local_date_str = []
    for i in range(len(archivos)):
        fecha_utc, fecha_path, fecha, fecha_local = retorna_fecha_hora_info(path_directory + archivos[i])
        local_hour.append(datetime.datetime.strptime(fecha_local, '%Y/%m/%d %H:%M'))
        local_date_str.append(fecha_local)
    return local_date_str, local_hour

fechas, time = Obtener_fecha_hora_de_Archvos (path_directory, archivos)

##------------------------------- GRAFICAS---------------------------- ##

## Primero las del netcdf empaquetado


# SE PLOTEA EN VENTANAS DE 1 DÍA
output = PdfFileWriter()
for j in range(0, len(Tiempo)):
    try:
        if len(Tiempo[j]) == 0:
            pass
        else:
            fig = plt.figure(figsize=[10, 8])
            ax1 = fig.add_subplot(2, 1, 1)
            ax1.imshow(a.variables[u'Radiancias'][j])
            ax1.set_title(Tiempo[j], fontsize=13)

            lons, lats, Radiancias = Obtiene_Lon_Lat_Fr_Rad(path_directory + archivos[j], limzon)
            ax2 = fig.add_subplot(2, 1, 2)
            ax2.imshow(Radiancias)
            ax2.set_title(fechas[j], fontsize=13)

            plt.savefig(Path_Save + Tiempo[j] + '.pdf', format='pdf')

            plt.close('all')

            file_j = file(Path_Save + Tiempo[j] + '.pdf', 'rb')
            page_j = PdfFileReader(file_j).getPage(0)
            output.addPage(page_j)

            os.system('rm ' + Path_Save + Tiempo[j] + '.pdf')

        output.write(file(Path_Save + 'GOES_Data_Carpetas.pdf', 'w'))
    except KeyError:
        pass

