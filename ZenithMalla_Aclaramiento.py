#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import netCDF4 as nc
from netCDF4 import Dataset
id
import datetime
import pytz
import pysolar
import scipy.interpolate as inter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

##................................................................................................##
####################################################################################################
##----------------------------------------SECCION 1-----------------------------------------------##
####################################################################################################
##................................................................................................##

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------


'Función para encontrar el ángulo zenital en cada punto geografico de la malla en cada hora.'
'Debido a que es un programa pesado, se hará para las longitudes y latitudes extremas de cada'
'hora y luego se interpolarán. O sea que se hace para los 4 puntos extremos. Requiere, la ruta'
'del archivo .nc que contiene la información de las latitudes y longitudes como un str, las'
'fechas iniciales y finales (sin hora) para las que se hará el cálculo horario, y una ruta'
'para guardar el array, las anteriores tambien en str.'

def HourlyZenith2018(Path_nc, fi, ff,Path_save):
    ds = Dataset(Path_nc)
    lat = ds.variables['lat'][:, :]
    lon = ds.variables['lon'][:, :]
    Rad = ds.variables['Radiancias'][:, :, :]
    tiempo = ds.variables['time']
    fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
    for i in range(len(fechas_horas)):
        fechas_horas[i] = fechas_horas[i].strftime('%Y-%m-%d %H:%M')
    fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')
    la = lat.shape[0]
    lo = lat.shape[1]
    Lat = lat[:, 0]
    Lon = lon[0,:]
    ###############################################################################################
    ## ----------------OBTENIENDO INCIDENCIA, AZIMUTH Y ZENITH PARA CADA PUNTO------------------ ##
    ###############################################################################################
    def daterange(start_date, end_date):
        'Ayuda a la abtencion de un rango de fechas. Revisar el parametro delta'
        import datetime
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        delta = timedelta(hours = 1)
        while start_date <= end_date:
            yield start_date
            start_date += delta

    date_range = []
    for i in daterange(fi, ff):
        date_range.append(i)

    timezone = pytz.timezone("America/Bogota")
    date_range_aware = [timezone.localize(date_range[i]) for i in range(len(date_range))]

    def Zenith_eachoCoord_Hourly(lat975, lon975, date):
        'Encuentra el ángulo zenital en un solo punto a una hora determinada'
        az,  al = pysolar.solar.get_position(lat975, lon975, date)
        azimuth975 = az
        altitude_deg975= al
        zenith975 = [90 - altitude_deg975]
        return zenith975
    ##-----------------------------------------------------------------------------------##
    Lon_west = np.nanmin(Lon)
    Lon_east = np.nanmax(Lon)
    Lat_North = np.nanmax(Lat)
    Lat_South = np.nanmin(Lat)

    Longitudes = [Lon_west,Lon_east ]
    Long_enX = Lon[1:-1].sort()
    Latitudes = [Lat_South,Lat_North]
    Lati_enX = Lat[1:-1].sort()
    ##-----------------------------------------------------------------------------------##
    Pos_Interpol = [0, -1]
    Zenith = list(np.empty(len(date_range_aware)))
    for i in range(len(date_range_aware)):
        # Zenith[i]=np.zeros((la,lo))
        # Zenith[i]=Zenith[i].reshape(la,lo)
        Z = np.zeros((len(Latitudes),len(Longitudes)))
        Z = Z.reshape(len(Latitudes),len(Longitudes))
        for j in Pos_Interpol:
        #for j in range(len(Lon)):
            for k in Pos_Interpol:
            #for k in range(len(Lat)):
                Z [k][j] = Zenith_eachoCoord_Hourly(Latitudes[k], Longitudes[j], date_range_aware[i])[0]
                #Zenith[i][k][j]= Zenith_eachoCoord_Hourly(Lat[k], Longitudes[j], date_range_aware[i])[0]
        vals = np.reshape(Z, (4))                                                        ## Porque se le están dando 4 valores
        pts = np.array([[i,j] for i in np.linspace(0,1,2) for j in np.linspace(0,1,2)] ) ## Coordenadas de aceurdo a la forma real, original, lo que ahy de la X y la Y respectivamente
        grid_x, grid_y = np.mgrid[0:1:145j, 0:1:174j]                                    ## Para una malla de 174 en X y 145 en Y, primero va lo de las Y y luego lo de las X
        grid_z = inter.griddata(pts, vals, (grid_x, grid_y), method='linear')
        Zenith[i] = grid_z
    Zenith = np.array(Zenith)
    date_range_aware = np.array(date_range_aware)
    np.save(Path_save, Zenith)
    np.save(Path_save[0:38]+'DatesZenith', date_range_aware)

    return Zenith, date_range_aware

Zenith, dates  = HourlyZenith2018('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C22018.nc', '2018-01-01', '2019-12-19', '/home/nacorreasa/Maestria/Datos_Tesis/hourlyZenith2018_2019')


##................................................................................................##
####################################################################################################
##----------------------------------------SECCION 2-----------------------------------------------##
####################################################################################################
##................................................................................................##

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

"Sección del código, destinada a la verificación y chequeo del funcionamiento del aclarado de imagenes"
"a partir de las gneración de unas imagenes de prueba para luego ser comparadas."


###############################################################################################
## ----------------------VERIFICACIÓN PARA EL ACLARAMIENTO DE IMAGENES---------------------- ##
###############################################################################################

ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C22018.nc')
lat = ds.variables['lat'][:, :]
lon = ds.variables['lon'][:, :]
Rad = ds.variables['Radiancias'][:, :, :]
tiempo = ds.variables['time']
fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
for i in range(len(fechas_horas)):
    fechas_horas[i] = fechas_horas[i].strftime('%Y-%m-%d %H:%M')
fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')
la = lat.shape[0]
lo = lat.shape[1]
Lat = lat[:, 0]
Lon = lon[0,:]


elegido=55
print(fechas_horas[elegido])

prueba = Rad[elegido, :, :]/np.cos(np.radians(Zenith[30, :, :]))

fig = plt.figure(figsize=[10, 8])
cax1= plt.imshow(Rad[elegido, :, :])
fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.85, 0.35, 0.05, 0.30])
fig.colorbar(cax1, label = u"Ref", cax=cbar_ax)
plt.subplots_adjust(wspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CompRadSINAclaramiento.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/CompRadSINAclaramiento.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')



fig = plt.figure(figsize=[10, 8])
cax1= plt.imshow(prueba)
fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.85, 0.35, 0.05, 0.30])
fig.colorbar(cax1, label = u"Ref_acla", cax=cbar_ax)
plt.subplots_adjust(wspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CompRadAclaramiento.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/CompRadAclaramiento.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


##................................................................................................##
####################################################################################################
##----------------------------------------SECCION 3-----------------------------------------------##
####################################################################################################
##................................................................................................##

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"Esta sección del codigo, pretende guardar los datos del netCDF4 de reflectancias de GOES como un .npy, luego"
"de que se le haga la aclaración."


Horizonte = 'Anio'    ##-->Para que tome datos desde el 2018 de GOES se pone 'Anio', para que tome solo lo del experimento se pone 'Exp'


################################################################################################
##-------------------INCORPORANDO EL ARRAY DEL ZENITH PARA CADA HORA--------------------------##
################################################################################################

def Aclarado_visible(Path_Zenith, Path_Fechas, Rad, fechas_horas):
    Z = np.load(Path_Zenith)
    Fechas_Z = np.load(Path_Fechas)

    daily_hours = np.arange(5, 19, 1)
    Zenith = []
    Fechas_Zenith = []
    for i in range(len(Fechas_Z)):
        if Fechas_Z[i].hour in daily_hours:
            Zenith.append(Z[i, :, :])
            Fechas_Zenith.append(Fechas_Z[i])
        elif Fechas_Z[i].hour not in daily_hours:
            pass
    Zenith = np.array(Zenith)

    Rad_clear = []
    for i in range(len(Fechas_Zenith)):
        for j in range(len(fechas_horas)):
            if Fechas_Zenith[i].hour ==  fechas_horas[j].hour and Fechas_Zenith[i].day ==  fechas_horas[j].day:
                Rad_clear.append(Rad[j, :, :]/np.cos(np.radians(Zenith[i, :, :])))
            else:
                pass
    Rad_clear = np.array(Rad_clear)
    return Rad

##---------------------------------------------------------------------------------------------------------##
#############################################################################################################
## -------------------------LECTURA DE LOS DATOS DE GOES CH2 DURANTE EL REGISTRO --------------------------##
#############################################################################################################
##---------------------------------------------------------------------------------------------------------##


if Horizonte == 'Anio' :
    ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C2_2018_2019.nc')
elif Horizonte == 'Exp' :
    ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C2_2019_0320_0822.nc')


lat = ds.variables['lat'][:, :]
lon = ds.variables['lon'][:, :]
Rad = ds.variables['Radiancias'][:, :, :]

tiempo = ds.variables['time']
fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
fechas_horas = pd.to_datetime(fechas_horas, errors='coerce')


def time_mod(time, delta, epoch=None):
    if epoch is None:
        epoch = datetime.datetime(1970, 1, 1, tzinfo=time.tzinfo)
    return (time - epoch) % delta

def time_round(time, delta, epoch=None):
    mod = time_mod(time, delta, epoch)
    if mod < (delta / 2):
       return time - mod
    return time + (delta - mod)

fechas_horas = [time_round(fechas_horas[i], datetime.timedelta(minutes=10)) for i in range(len(fechas_horas))]

if Horizonte == 'Anio' :

    ##-------------------INCORPORANDO EL ARRAY DEL ZENITH PARA CADA HORA PARA EL HORIZONTE ANUAL--------------------------##

    Rad_Z = Aclarado_visible('/home/nacorreasa/Maestria/Datos_Tesis/hourlyZenith2018.npy', '/home/nacorreasa/Maestria/Datos_Tesis/DatesZenith.npy', Rad, fechas_horas)
    del Rad

    Rad = Rad_Z

    nombre_rad ='Array_Rad2018CH2'
    Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
    nombre_lat = 'Array_Lat_CH2_2018_2019'
    nombre_lon = 'Array_Lon_CH2_2018_2019'
    nombre_fechas_horas = 'Array_FechasHoras_CH2_2018_2019'

    np.save(Path_save[0:45]+nombre_rad, Rad)
    np.save(Path_save[0:45]+nombre_lat, lat)
    np.save(Path_save[0:45]+nombre_lon, lon)
    np.save(Path_save[0:45]+nombre_fechas_horas, fechas_horas)

    # In [19]: np.shape(lat)
    # Out[19]: (145, 174)
    #
    # In [20]: np.shape(Rad)
    # Out[20]: (17404, 145, 174)
    #
    # In [22]: np.shape(lon)
    # Out[22]: (145, 174)
    #
    # In [25]: np.shape(fechas_horas)
    # Out[25]: (17404,)

elif Horizonte == 'Exp' :

    ##-------------------INCORPORANDO EL ARRAY DEL ZENITH PARA CADA HORA PARA EL HORIZONTE DEL EXPERIMENTO--------------------------##

    ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C2_2019_0320_0822.nc')
    lat = ds.variables['lat'][:, :]
    lon = ds.variables['lon'][:, :]
    Rad = ds.variables['Radiancias'][:, :, :]
    tiempo = ds.variables['time']
    fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
    for i in range(len(fechas_horas)):
        fechas_horas[i] = fechas_horas[i].strftime('%Y-%m-%d %H:%M')
    fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')

    Rad_Z = Aclarado_visible('/home/nacorreasa/Maestria/Datos_Tesis/hourlyZenith2018.npy', '/home/nacorreasa/Maestria/Datos_Tesis/DatesZenith.npy', Rad, fechas_horas)
    del Rad

    Rad = Rad_Z

    nombre_rad ='Array_RadCH2_2019_0320_0822'
    Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
    nombre_lat = 'Array_Lat_2019_0320_0822_CH2'
    nombre_lon = 'Array_Lon_2019_0320_0822_CH2'
    nombre_fechas_horas = 'Array_FechasHoras_2019_0320_0822_CH2'

    np.save(Path_save[0:45]+nombre_rad, Rad)
    np.save(Path_save[0:45]+nombre_lat, lat)
    np.save(Path_save[0:45]+nombre_lon, lon)
    np.save(Path_save[0:45]+nombre_fechas_horas, fechas_horas)
