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
Programa para el computo del efecto de las nubes a partir del forzamiento de nubes no lineal
sobre la radiacion solar en superficie, obtener los promedios mensuales y horarios y restarlo
del array de irradiancias en condiciones de cielo despejado, considerando las pendientes horarias
y estacionales.
"""
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

####################################################################################
## -----------LECTURA DE LOS DATOS DE GOES CH2 MALLA GENERAL ENMASCARADA--------- ##
####################################################################################

Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_Malla_MaskedClean.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Malla_MaskedClean.npy')

####################################################################################
## ---------LECTURA DE LOS DATOS DE IRRADIANCIA TEORICA E CIELO DESPEJADO-------- ##
####################################################################################

Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Irradiance_Interpolate.npy')
fechas_horas_Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_IrradianceInterpolate.npy')

####################################################################################
## ---------LECTURA DE LOS DATOS DE PENDIENTE Y CORRELACION IRRAD-RELFECT-------- ##
####################################################################################

df_Relaciones_348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/_DF_SlopeStd_348.csv',  sep=',', index_col =0)
df_Relaciones_350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/_DF_SlopeStd_350.csv',  sep=',', index_col =0)
df_Relaciones_975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/_DF_SlopeStd_975.csv',  sep=',', index_col =0)

df_Relaciones = pd.concat([df_Relaciones_348, df_Relaciones_350, df_Relaciones_975], axis=1)
df_Relaciones_Corr = pd.concat([df_Relaciones_348['Corr'], df_Relaciones_350['Corr'], df_Relaciones_975['Corr']], axis=1)
df_Relaciones_Corr = df_Relaciones_Corr.mean(axis = 1, skipna = True)
df_Relaciones_Corr = pd.DataFrame(df_Relaciones_Corr, columns=['Corr'])
df_Relaciones_Corr['Mes'] = df_Relaciones_348['Mes']
df_Relaciones_Corr['Hora'] = df_Relaciones_348['Hora']

df_Relaciones_Std = pd.concat([df_Relaciones_348['Std'], df_Relaciones_350['Std'], df_Relaciones_975['Std']], axis=1)
df_Relaciones_Std = df_Relaciones_Std.mean(axis = 1, skipna = True)
df_Relaciones_Std = pd.DataFrame(df_Relaciones_Std, columns=['Std'])
df_Relaciones_Std['Mes'] = df_Relaciones_348['Mes']
df_Relaciones_Std['Hora'] = df_Relaciones_348['Hora']

df_Relaciones_Slope = pd.concat([df_Relaciones_348['Slope'], df_Relaciones_350['Slope'], df_Relaciones_975['Slope']], axis=1)
df_Relaciones_Slope = df_Relaciones_Slope.mean(axis = 1, skipna = True)
df_Relaciones_Slope = pd.DataFrame(df_Relaciones_Slope, columns=['Slope'])
df_Relaciones_Slope['Mes'] = df_Relaciones_348['Mes']
df_Relaciones_Slope['Hora'] = df_Relaciones_348['Hora']

###################################################################################
## ----------REMUESTREANDO LOS DATOS DE REFLECTANCIAS A HORARIO POR MES--------- ##
###################################################################################
Horas = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
Meses = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


mes_index = []
hora_index = []
for i in range(len(Meses)):
    for j in range(len(Horas)):
        mes_index.append(Meses[i])
        hora_index.append(Horas[j])

Read_Remues =[]
for g in range(len(mes_index)):
    for i in range(len(hora_index)):
        Temporal_Porc = np.zeros((la,lo))
        Temporal_Porc = Porc[i].reshape(la,lo)
        for j in range(0,lo,1):
            for k in range(0,la,1):
                temporal = pd.DataFrame(Rad[:,k, j], index = fechas_horas, columns=['FR'] )
                temporal_month = temporal[(temporal.index.month== mes_index[g]) & (temporal.index.hour == hora_index[i])]
                Temporal_Porc [k][j] = np.nanmean(temporal_month)
    Read_Remues.append(Temporal_Porc)
Read_Remues = np.array(Read_Remues)
























###################################################################################
## --------------ESCALAR LOS VALORES DE LA MATRIZ DE REFLECTANCIAS-------------- ##
###################################################################################
Read_Remues_Factor = Read_Remues/100

for i in range(len(df_Relaciones_Corr)):
    Read_Remues_Factor[i] = Read_Remues_Factor* df_Relaciones_Slope.Slope.values[i]


###################################################################################
## ---------------------GRAFICANDO LOS PROMEDIOS DE NUBES----------------------- ##
###################################################################################

##------------------------------------------------GRAFICA------------------------------------------------##

shape = '/home/nacorreasa/Maestria/Semestre1/Analisis_Geoespacial/MuchosShapes/AMVA/AreaMetropolitana'
Path_Save = '/home/nacorreasa/Escritorio/Figuras/'
nombre_lat = 'Array_Lat_IrradianceInterpolate.npy'
nombre_lon = 'Array_Lon_IrradianceInterpolate.npy'
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
lat = np.load(Path_save+nombre_lat)
lon = np.load(Path_save+nombre_lon)
Lat = lat[:, 0]
Lon = lon[0,:]
levels = np.linspace(0, 100, 20)
lat_down = np.nanmin(Lat)
lat_up = np.nanmax(Lat)
lon_left = np.nanmin(Lon)
long_right = np.nanmax(Lon)
times = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Agos', 'Sep', 'Oct', 'Nov','Dic'])

Path_Save_pdf = '/home/nacorreasa/Escritorio/Figuras/'
output = PdfFileWriter()
for j in range(0,len(Meses)):

    plt.close('all')
    fig = plt.figure(figsize=(14,18))

    for i in range(0, len(Horas)):
        ax = fig.add_subplot(4, 3, i+1)
        ax.set_title('Hora: '+str(Horas[i]), fontsize=18)
        m = Basemap(projection='merc', llcrnrlat=lat_down, urcrnrlat=lat_up,
                    llcrnrlon=lon_left, urcrnrlon=long_right, resolution='i', lat_ts=20)
        m.readshapefile(shape, name='AreaMetropolitana', color='k', linewidth=1.5)
        cs = m.imshow(Read_Remues[i], cmap ='rainbow', alpha = 0.5)
        parallels = np.arange(lat_down, lat_up+1, 0.3)
        m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
        meridians = np.arange(lon_left, long_right+1, 0.3)
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)

    plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.07)

    cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
    cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
    cbar.set_label('Irradiancias  durante: ' + meses[i],  fontproperties = prop, fontsize=20 )



    file_j = file(Path_Save_pdf + meses[i] '.pdf', 'rb')
    page_j = PdfFileReader(file_j).getPage(0)
    output.addPage(page_j)

    os.system('rm ' + Path_Save_pdf + meses[i] '.pdf')

output.write(file(Path_Save_pdf  + 'ReduccionRadiacionMesHora.pdf', 'w'))
os.system('scp '+ Path_Save_pdf +  'ReduccionRadiacionMesHora.pdf  nacorreasa@192.168.1.74:/var/www/nacorreasa/Calidad_Meteo/Vaisala')
os.system('rm '+ Path_Sal +  'ReduccionRadiacionMesHora.pdf')
