#!/usr/bin/env python
# -- coding: utf-8 --
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import math as m
import numpy.ma as ma
#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Programa para la creación de un 3D array con la información de reflectancia incidente para cada pixeles
en cada paso de tiempo. El resultado será para cada de tiempo  de las imagenes de GOES.
"""
##############################################################################################
## ------------------LECTURA DE LOS DATOS PROVENIENTES DE LOS RASTERS---------------------- ##
##############################################################################################
fechas_horas_Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_IrradianceInterpolate.npy')
fechas_horas_Irra = pd.to_datetime(fechas_horas_Irra, format="%Y-%m-%d %H:%M", errors='coerce')

Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CH2__2018_2019.npy')
fechas_horas_GOES = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')

lat_index_o = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_index_Malla.npy')
lon_index_o = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_index_Malla.npy')

mx_lat_index = ma.masked_invalid(lat_index_o)
mx_lon_index = ma.masked_invalid(lon_index_o)

lat_index = mx_lat_index.astype('int')
lon_index = mx_lon_index.astype('int')

##############################################################################################
## ----------------DEFINICION DE LAS ACCIONES PARA LA SELECCION DE DATOS------------------- ##
##############################################################################################

R = np.zeros(Rad.shape, dtype=float)*np.nan
fechas_horas_new =[]
raros = []
blist = []
for g in range(len(fechas_horas_GOES)):
    try:
        a = np.where(fechas_horas_Irra.month   == fechas_horas_GOES[g].month)[0]
        b = np.where(fechas_horas_Irra[a].hour == fechas_horas_GOES[g].hour)[0][0]

        lat_index[b,:,:][lat_index[b,:,:]<0]=0
        lon_index[b,:,:][lon_index[b,:,:]<0]=0
        fraccion = Rad[g, lat_index[b,:,:], lon_index[b,:,:]]
        fraccion[np.isnan(lat_index_o[b])] = np.nan
        #fraccion[fraccion == fraccion[0][0]]  =np.nan
        R[g, :, :] = fraccion
        fechas_horas_new.append(fechas_horas_GOES[g])
        blist.append(b)
    except:
        raros.append(g)
        fechas_horas_new.append(fechas_horas_GOES[g])
    print(len(fechas_horas_GOES)-g)

fechas_horas_new = np.array(fechas_horas_new)



# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import matplotlib.ticker as tck
# import matplotlib.cm as cm
# import matplotlib.font_manager as fm
# import math as m
# import matplotlib.dates as mdates
# import matplotlib.ticker as ticker
# import matplotlib.transforms as transforms
# import matplotlib.colors as colors
# import os
# elegido =  344
# fig = plt.figure(figsize=[10, 8])
# cax1= plt.imshow(R[elegido])
# fig.subplots_adjust(right=0.8)
# plt.title("elegido " + str(fechas_horas_new[elegido]))
# cbar_ax = fig.add_axes([0.85, 0.35, 0.05, 0.30])
# fig.colorbar(cax1, label = u"reflectancia", cax=cbar_ax)
# plt.subplots_adjust(wspace=0.3)
# plt.savefig('/home/nacorreasa/Escritorio/Figuras/PRUEBIIIS.png')
# plt.close('all')
# os.system('scp /home/nacorreasa/Escritorio/Figuras/PRUEBIIIS.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

#################################################################################################
##---------------------------PROMEDIO DE CADA IMAGEN(VERIFICACION) ----------------------------##
#################################################################################################
R_mean =[np.nanmean(R[i]) for i in range(len(fechas_horas_GOES))]
R_mean_nan = np.where(np.isnan(R_mean))[0]
R_mean_100 = np.where(np.array(R_mean) == 100)[0]
Porcentaje_Datos_Malos = (float(len(R_mean_nan)+len(R_mean_100))/float (len(R)))*100
print('% de datos malos= '+ str(Porcentaje_Datos_Malos))
R[R_mean_100] = np.nan

##----------------------------------------------------------------------------------------##

fechas_horas_new = [fechas_horas_new[i].strftime('%Y-%m-%d %H:%M') for i in range(len(fechas_horas_new))]
fechas_horas_new = np.array(fechas_horas_new)

#################################################################################################
##----------------------------GUARDANDO LOS ARRAYS DE COORDENADAS -----------------------------##
#################################################################################################
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
np.save(Path_save[0:45]+'Array_Rad_Malla', R)
np.save(Path_save[0:45]+'Array_FechasHoras_Malla', fechas_horas_new)

print('Hemos terminado con exito')
