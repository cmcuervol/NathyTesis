#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.cm as cm
import matplotlib.font_manager as fm
import math as m
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.transforms as transforms
import matplotlib.colors as colors
import os
id
import itertools
import datetime
from scipy.stats import ks_2samp
from datetime import datetime, timedelta
from scipy import ndimage

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Programa para la limpieza de cada una imagenes, entonces se entrega una set de
de imagenes limpias, es decir sin el ruido de puntos pequeño, el set es un nuevo
array.
"""

################################################################################################
## -------------------------------UMBRALES DE LAS REFLECTANCIAS------------------------------ ##
################################################################################################

df_UmbralH_Nube_348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_348_Nuba.csv',  sep=',', index_col =0,  header = None)
df_UmbralH_Nube_350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_350_Nuba.csv',  sep=',', index_col =0,  header = None)
df_UmbralH_Nube_975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_975_Nuba.csv',  sep=',', index_col =0,  header = None)

df_UmbralH_Nube = pd.concat([df_UmbralH_Nube_348, df_UmbralH_Nube_350, df_UmbralH_Nube_975], axis=1)
df_UmbralH_Nube = df_UmbralH_Nube.mean(axis = 1, skipna = True)
df_UmbralH_Nube = pd.DataFrame(df_UmbralH_Nube, columns=['Umbral'])

####################################################################################
## ----------------LECTURA DE LOS DATOS DE GOES CH2 MALLA GENERAL---------------- ##
####################################################################################

Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_Malla.npy')

fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Malla.npy')
fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')

#########################################################################
## -------------------ENMASCARAMIENTO DE LAS IMAGENES------------------##
#########################################################################

Rad_bina = []
Rad_mask = []
fechas_horas_new = []
for i in range (len(fechas_horas)):
    for j in range(len(df_UmbralH_Nube.Umbral.index)):
        if df_UmbralH_Nube.Umbral.index[j] == fechas_horas[i].hour:
            umbral = df_UmbralH_Nube.Umbral[j+6]
            rad = Rad[i, :, :]
            radbi = (rad > umbral).astype(int)
            rad[rad<umbral]=np.nan
            #radm = rad
            Rad_bina.append(radbi)
            Rad_mask.append(rad)
            fechas_horas_new.append(fechas_horas[i])
            print('yes')
        else:
            pass

Rad_bina = np.array(Rad_bina)
Rad_mask = np.array(Rad_mask)

##############################################################################
## --------------LIMIEZA MORFOLOGICA POR EL METODO SELECCIONADO-------------##
##############################################################################

def Limpieza_Morfologica(metodo, array_binario):
    """
    Funcion q entrega un np.array binario producto de la limpieza morfológica.
    -metodo = str, como se hará la limpieza, puede ser: erosion, closing, opening
    -array_binario = 2D array aser limpiado
    -clean_array = 2D array resultante de la limpieza
    """
    if metodo == 'erosion':
        clean_array = ndimage.binary_erosion(array_binario).astype(array_binario.dtype)
    elif metodo == 'closing':
        clean_array = ndimage.binary_closing(array_binario, structure=np.ones((3,3))).astype(np.int)
    elif metodo == 'opening':
        clean_array = ndimage.binary_opening(array_binario, structure=np.ones((3,3))).astype(np.int)
    return clean_array

Rad_bina_clean =[]
for i in range (len(fechas_horas_new)):
    array_2d= Rad_bina[i, :, :]
    clean_array = Limpieza_Morfologica('closing', array_2d)
    Rad_bina_clean.append(clean_array)

Rad_bina_clean = np.array(Rad_bina_clean)

#############################################################################
## --------------ESCOGIENDO LOS PIXELES A CORDE A LA LIMPIEZA -------------##
#############################################################################

Rad_final=[]
for g in range(len(fechas_horas_new)):
    fraccion = Rad_mask[g, :, :]
    fraccion[Rad_bina_clean[g, :, :] == 0] = np.nan
    Rad_final.append(fraccion)
Rad_final=np.array(Rad_final)

##----------------------------------------------------------------------------------------##

fechas_horas_new = [fechas_horas_new[i].strftime('%Y-%m-%d %H:%M') for i in range(len(fechas_horas_new))]
fechas_horas_new = np.array(fechas_horas_new)

#################################################################################################
##----------------------------GUARDANDO LOS ARRAYS DE COORDENADAS -----------------------------##
#################################################################################################
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
np.save(Path_save[0:45]+'Array_Rad_Malla_MaskedClean', Rad_final)
np.save(Path_save[0:45]+'Array_FechasHoras_Malla_MaskedClean', fechas_horas_new)

print('Hemos terminado con exito')



# la = lat.shape[0]
# lo = lat.shape[1]
#
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
# elegido =  34225
# fig = plt.figure(figsize=[10, 8])
# cax1= plt.imshow(Rad_mask[elegido])
# fig.subplots_adjust(right=0.8)
# plt.title("elegido " + str(fechas_horas_new[elegido]))
# cbar_ax = fig.add_axes([0.85, 0.35, 0.05, 0.30])
# fig.colorbar(cax1, label = u"reflectancia", cax=cbar_ax)
# plt.subplots_adjust(wspace=0.3)
# plt.savefig('/home/nacorreasa/Escritorio/Figuras/PRUEBIIIS.png')
# plt.close('all')
# os.system('scp /home/nacorreasa/Escritorio/Figuras/PRUEBIIIS.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
#
# fig = plt.figure(figsize=[10, 8])
# cax1= plt.imshow(Rad_final[elegido])
# fig.subplots_adjust(right=0.8)
# plt.title("elegido " + str(fechas_horas_new[elegido]))
# cbar_ax = fig.add_axes([0.85, 0.35, 0.05, 0.30])
# fig.colorbar(cax1, label = u"reflectancia", cax=cbar_ax)
# plt.subplots_adjust(wspace=0.3)
# plt.savefig('/home/nacorreasa/Escritorio/Figuras/PRUEBIIIS_fraccion.png')
# plt.close('all')
# os.system('scp /home/nacorreasa/Escritorio/Figuras/PRUEBIIIS_fraccion.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
#
# fig = plt.figure(figsize=[10, 8])
# cax1= plt.imshow(ensa)
# fig.subplots_adjust(right=0.8)
# plt.title("elegido " + str(fechas_horas_new[elegido]))
# cbar_ax = fig.add_axes([0.85, 0.35, 0.05, 0.30])
# fig.colorbar(cax1, label = u"reflectancia", cax=cbar_ax)
# plt.subplots_adjust(wspace=0.3)
# plt.savefig('/home/nacorreasa/Escritorio/Figuras/PRUEBIIIS_Erosion.png')
# plt.close('all')
# os.system('scp /home/nacorreasa/Escritorio/Figuras/PRUEBIIIS_Erosion.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
#
#
# fig = plt.figure(figsize=[10, 8])
# cax1= plt.imshow(Rad_bina_clean[elegido])
# fig.subplots_adjust(right=0.8)
# plt.title("elegido " + str(fechas_horas_new[elegido]))
# cbar_ax = fig.add_axes([0.85, 0.35, 0.05, 0.30])
# fig.colorbar(cax1, label = u"reflectancia", cax=cbar_ax)
# plt.subplots_adjust(wspace=0.3)
# plt.savefig('/home/nacorreasa/Escritorio/Figuras/PRUEBIIIS_Closing.png')
# plt.close('all')
# os.system('scp /home/nacorreasa/Escritorio/Figuras/PRUEBIIIS_Closing.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
