#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.font_manager as fm
import math as m
import matplotlib.dates as mdates
id
import itertools
import datetime
import matplotlib.colors as colors
import matplotlib.cm as cm
import os
import statistics
import pysolar

#-----------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

'Codigo para la relación y análisis de los indices de cielo despejado (Kt*) y el indice de claridad (Kt).'
'Se incluye tambien un análisis de su tasa de cambio para evaluar su variabilidad y junto con la fracción'
'de cobertura de nubes. Se hace sobre los datos historicos porque se quiere analizar la variabilidad.'

Theoric_Model = 'GIS'   ##---> 'GIS' para que coja el de Gis o 'Piranometro' para que tome el de el piranometro

##############################################################################
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------
##############################################################################

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##########################################################################################################
##-----------------------------------LECTURA DE LOS DATOS  DE PIRANOMETRO-------------------------------##
##########################################################################################################

df_pira_TS = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60012018_2019.txt', parse_dates=[2])
df_pira_TS = df_pira_TS.set_index(["fecha_hora"])
df_pira_TS.index = df_pira_TS.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_TS.index = df_pira_TS.index.tz_localize(None)
df_pira_TS = df_pira_TS[df_pira_TS['radiacion'] >=0]

df_pira_CI = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60022018_2019.txt', parse_dates=[2])
df_pira_CI = df_pira_CI.set_index(["fecha_hora"])
df_pira_CI.index = df_pira_CI.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_CI.index = df_pira_CI.index.tz_localize(None)
df_pira_CI = df_pira_CI[df_pira_CI['radiacion'] >=0]

df_pira_JV = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60032018_2019.txt', parse_dates=[2])
df_pira_JV = df_pira_JV.set_index(["fecha_hora"])
df_pira_JV.index = df_pira_JV.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_JV.index = df_pira_JV.index.tz_localize(None)
df_pira_JV = df_pira_JV[df_pira_JV['radiacion'] >=0]

## ------------------------------------DATOS HORARIOS DE RADIACON----------------------------- ##

df_pira_JV_h =  df_pira_JV.groupby(pd.Grouper(freq="H")).mean()
df_pira_CI_h =  df_pira_CI.groupby(pd.Grouper(freq="H")).mean()
df_pira_TS_h =  df_pira_TS.groupby(pd.Grouper(freq="H")).mean()


df_pira_JV_h = df_pira_JV_h.between_time('06:00', '17:59')
df_pira_CI_h = df_pira_CI_h.between_time('06:00', '17:59')
df_pira_TS_h = df_pira_TS_h.between_time('06:00', '17:59')

##############################################################################
## ----------------LECTURA DE LOS DATOS DE RADIACION TEORICA--------------- ##
##############################################################################
import datetime

def daterange(start_date, end_date):
    'Para el ajuste de las fechas en el modelo de Kumar cada 10 min. Las fechas final e inicial son en str: %Y-%m-%d'

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    delta = timedelta(minutes=60)
    while start_date <= end_date:
        yield start_date
        start_date += delta

fechas = []
for i in daterange('2018-01-01', '2019-01-01'):
    fechas.append(i)
fechas = fechas[0:-1]

if Theoric_Model == 'Piranometro':
    df_Theoric = pd.read_csv("/home/nacorreasa/Maestria/Datos_Tesis/RadiacionTeorica_DataFrames/df_PIR.csv",  sep=',', index_col =0)
    df_Theoric.index = pd.to_datetime(df_Theoric.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')


elif Theoric_Model == 'GIS':
    df_Theoric = pd.read_csv("/home/nacorreasa/Maestria/Datos_Tesis/RadiacionTeorica_DataFrames/df_GIS.csv",  sep=',', index_col =0)
    df_Theoric.index = pd.to_datetime(df_Theoric.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')


fechas_new = [df_Theoric.index[i].replace(year = 2018) for i in range(len(df_Theoric.index))]
df_Theoric.index =  fechas_new
df_Theoric.index = pd.to_datetime(df_Theoric.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_Fechas = pd.DataFrame(fechas, index = fechas, columns = ['fechas'])
df_Theoric = pd.concat([df_Fechas,df_Theoric ], axis=1)
df_Theoric = df_Theoric.drop(['fechas' ], axis=1)

##-------------------------------------DUPLICANDO PARA Q SEAN DOS AÑOS-----------------------------##
df_Theoric_2 = df_Theoric.copy()
df_Theoric_2.index = [df_Theoric_2.index[i].replace(year=2019) for i in range(len(df_Theoric_2.index))]

df_result = pd.concat([df_Theoric, df_Theoric_2])

del df_Theoric_2, df_Theoric

df_Theoric = df_result

##############################################################################
## ---------------------------INDICE DE CLARIDAD--------------------------- ##
##############################################################################

# def Radiacion_Tope_Atmosfera(Latitud):
#     'Función para la estimación de la radiación al tope de la atmosfera a partir del lo explicado en el libro de Iqbal(1983), a ventana diaria'
#     '(Qd) y horaria (Io), en el que el parametro de entrada es la Latitud de la superficie horizontal, en coordenadas feográdicas, como float.'
#     'El tiempo solar está acotado apra el meridiano 75.'
#     ##---DECLINACION SOLAR---##
#     J = np.arange(1, 366, 1)
#     g = 2*m.pi*(J-1)/365
#     d = (0.006918 - 0.399912*np.cos(g) + 0.070257*np.sin(g) - 0.006758*np.cos(2*g) + 0.000907*np.sin(2*g) - 0.002697*np.cos(3*g) + 0.00148*np.sin(3*g)+ 0.000907*np.sin(2*g) - 0.002697*np.cos(3*g) + 0.00148*np.sin(3*g))
#
#     ##---LOCAL STANDART TIME---##
#     LT = np.arange(0, 24, 1)
#
#     ##---ECUACION DEL TIEMPO---##
#     B = 2*m.pi*(J-81)/365
#     ET = 9.87*np.sin(2*B)-7.53*np.cos(B)-1.5*np.cos(B)
#
#     ##---TIEMPO SOLAR---##
#     Ls = -75.                       #Meridiano estándar en grados decimales
#     # Ls = -75*m.pi/180.            #Meridiano estándar en radianes
#     Ll = -75.56359                  #Meridiano local en grados decimales
#     # Ll = -75.56359 *m.pi/180.     #Meridiano local en radianes
#     L = (Ls-Ll)/15
#     TS = []
#     for j in range(len(ET)):
#         for i in range(len(LT)):
#             TS.append(LT[i]+(ET[j]/60)+L)
#
#     ##----ANGULO HORARIO-----##
#     w = []
#     for i in range(len(TS)):
#         w.append(15*(12-TS[i]))       #En grados decimales
#
#     w = np.array(w)*m.pi/180          #En radianes
#
#     ##---EXCENTRICIDAD---##
#     Eo = 1+(0.0033*np.cos((2*np.pi*J)/365))
#
#     ##---CAMBIO A RESOLUCIÓN HORARIA---#
#     d_h = list(itertools.chain.from_iterable(itertools.repeat(x, 24) for x in list(d)))
#     Eo_h = list(itertools.chain.from_iterable(itertools.repeat(x, 24) for x in Eo))
#
#     ##---LATITUD DE UBICACIÓN---#
#     Lat = Latitud*m.pi/180.                             #En radianes
#
#     ##---DISTANCIA ENTRE LA TIERRA Y EL SOL---##
#     dist = 1 - 0.01672*(np.cos(0.985*(J-4)))
#     dist = dist*10E10
#     distM = 1.5*10E11                                # Verificar unidades
#     So = 1367                                        # W/m2
#
#     ##---ANGULOS HORARIOS DE AMANECIDA Y ATARDECIDA---##
#           ##---Ángulo horario por día (amanecer)---##
#     ho = np.arccos(-1*(np.tan(Lat)*np.tan(d)))      # En grados
#     ho = ho*180/np.pi
#            ##---Ángulo horario por día (atardecer)---##
#     hf = -1*ho                                       # En grados
#
#     ##---TIEMPOR DE AMANECIDA Y ATARDECIDA---##
#           ##---Tiempo en horas de amanecida a partir del ángulo horario---##
#     to = 12 - ho/15                                  # En horas decimales
#     to_m = np.mean(to)
#
#     time_o = []
#     for i in range(len(to)):
#         a = (str(datetime.timedelta(seconds = to[i]*3600))[0:7])
#         time_o.append(datetime.datetime.strptime(a, '%H:%M:%S').time())
#
#           ##---Tiempo en horas de atardecer a partir del ángulo horario---##
#     tf = 12 - hf/15                                  # En horas decimales
#     tf_m = np.mean(tf)
#
#     time_f = []
#     for i in range(len(tf)):
#         a = (str(datetime.timedelta(seconds = tf[i]*3600))[0:7])
#         time_f.append(datetime.datetime.strptime(a, '%H:%M:%S').time())
#
#     ##---INSOLACIÓN PROMEDIO DIARIA AL TOPE DE LA ATMOSFERA---##
#     Qd = So/np.pi*((distM/dist)**2)*(ho*np.sin(Lat)*np.sin(d) + np.cos(Lat)*np.cos(d)*np.sin(ho))
#
#     ##---RADIACIÓN HORARIA AL TOPE DE LA ATMOSFERA---##
#     Io = []
#     for i in range(len(d_h)):
#         Io.append(So*Eo_h[i]*(np.sin(d_h[i])*np.sin(Lat) + np.cos(d_h[i])*np.cos(Lat)*np.cos(w[i])))
#     return Io, Qd
#

#Ioh, Qd = Radiacion_Tope_Atmosfera(6.217)

import pvlib
Io_h = [pvlib.irradiance.get_extra_radiation(fechas[i], solar_constant=1366.1, method='spencer', epoch_year=2019) for i in range(len(fechas))] ## Wm2

df_Kt = pd.DataFrame(Io_h, index=fechas, columns = ['TAR'] )



df_Kt = pd.concat([df_Kt, df_pira_TS_h['radiacion']], axis=1).reindex(df_Kt.index)
df_Kt = pd.concat([df_Kt, df_pira_CI_h['radiacion']], axis=1).reindex(df_Kt.index)
df_Kt = pd.concat([df_Kt, df_pira_JV_h['radiacion']], axis=1).reindex(df_Kt.index)

df_Kt.columns = ['TAR', 'radiacion_975', 'radiacion_350', 'radiacion_348']

df_Kt['Kt_TS'] = df_Kt['radiacion_975']/df_Kt['TAR']
df_Kt['Kt_CI'] = df_Kt['radiacion_350']/df_Kt['TAR']
df_Kt['Kt_JV'] = df_Kt['radiacion_348']/df_Kt['TAR']


#####################################################################################
## ---------------------------INDICE DE CIELO DESPEJADO--------------------------- ##
#####################################################################################
if Theoric_Model == 'GIS':
    df_Kt['Kt*_TS'] =  df_Kt['radiacion_975']/ df_Theoric['Rad_teo_975']
    df_Kt['Kt*_CI'] =  df_Kt['radiacion_350']/ df_Theoric['Rad_teo_350']
    df_Kt['Kt*_JV'] =  df_Kt['radiacion_348']/ df_Theoric['Rad_teo_348']

elif Theoric_Model == 'Piranometro':
    df_Kt['Kt*_TS'] =  df_Kt['radiacion_975']/ df_Theoric['Io']
    df_Kt['Kt*_CI'] =  df_Kt['radiacion_350']/ df_Theoric['Io']
    df_Kt['Kt*_JV'] =  df_Kt['radiacion_348']/ df_Theoric['Io']

# df_Kt = df_Kt[(df_Kt['Kt*_TS']<=1)]
# df_Kt = df_Kt[(df_Kt['Kt*_CI']<=1)]
# df_Kt = df_Kt[(df_Kt['Kt*_JV']<=1)]

"El dataframe creado  esta a resolución de una hora"

# ########################################################################################################
# ## ---------------------------APLICANDO UNA ADICIONAL LIMPUEZA A LOS DATOS--------------------------- ##
# ########################################################################################################
#
# # df_Kt = df_Kt[(df_Kt['Kt*_TS']<=1)&(df_Kt['Kt*_CI']<=1)&(df_Kt['Kt*_JV']<=1)&(df_Kt['Kt_TS']<=1)&(df_Kt['Kt_CI']<=1)&(df_Kt['Kt_JV']<=1)]
# # df_Kt = df_Kt[(df_Kt['Kt*_TS']>=0)&(df_Kt['Kt*_CI']>=0)&(df_Kt['Kt*_JV']>=0)&(df_Kt['Kt_TS']>=0)&(df_Kt['Kt_CI']>=0)&(df_Kt['Kt_JV']>=0)]
#
# def normalize_df_column(dfcol):
#     x, y = np.nanmin(dfcol.values), np.nanmax(dfcol.values)
#     list = (dfcol-[x]).div(y-x)
#     dfcol = list
#     return dfcol
#
# normalize_df_column(df_Kt['Kt*_TS'])
# normalize_df_column(df_Kt['Kt*_CI'])
# normalize_df_column(df_Kt['Kt*_JV'])
# normalize_df_column(df_Kt['Kt_TS'])
# normalize_df_column(df_Kt['Kt_CI'])
# normalize_df_column(df_Kt['Kt_JV'])
#

######################################################################################
## ---------------------------CICLOS DIURNOS Y MENSUALES--------------------------- ##
######################################################################################
new_idx_CD = np.arange(6, 18, 1)
df_Kt_CD  = df_Kt.groupby(by=[df_Kt.index.hour]).mean()
df_Kt_CD  = df_Kt_CD.reindex(new_idx_CD)

new_idx_CA = np.arange(1, 13, 1)
df_Kt_CA = df_Kt.groupby([df_Kt.index.month, ]).mean()

months = ['Ene', 'Feb', 'Mar',  'Abr','May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
months = np.array(months)


##-------------------------------GRAFICA TODO JUNTO----------------------------##
plt.close("all")
fig = plt.figure(figsize=(10., 8.),facecolor='w',edgecolor='w')
ax1=fig.add_subplot(2,3,1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.bar(np.arange(len(df_Kt_CD)), df_Kt_CD['Kt_CI'].values, color='#8ABB73', align='center', alpha=0.5)
ax1.set_xlabel(u'Hour', fontproperties = prop_1)
ax1.set_ylabel(r"Kt", fontproperties = prop_1)
ax1.set_xticks(range(0,12), minor=False)
ax1.set_xticklabels(df_Kt_CD.index, minor=False, rotation = 20, fontsize = 9)
ax1.set_title(u'DC Kt index in the West point', loc = 'center', fontsize=9)

ax2=fig.add_subplot(2,3,2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.bar(np.arange(len(df_Kt_CD)), df_Kt_CD['Kt_TS'].values, color='#8ABB73', align='center', alpha=0.5)
ax2.set_xlabel(u'Hour', fontproperties = prop_1)
ax2.set_ylabel(r"Kt", fontproperties = prop_1)
ax2.set_xticks(range(0,12), minor=False)
ax2.set_xticklabels(df_Kt_CD.index, minor=False, rotation = 20)
ax2.set_title(u'DC Kt index in the West Center point', loc = 'center', fontsize=9)

ax3 = fig.add_subplot(2,3,3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.bar(np.arange(len(df_Kt_CD)), df_Kt_CD['Kt_JV'].values, color='#8ABB73', align='center', alpha=0.5)
ax3.set_xlabel(u'Hour', fontproperties = prop_1)
ax3.set_ylabel(r"Kt", fontproperties = prop_1)
ax3.set_xticks(range(0,12), minor=False)
ax3.set_xticklabels(df_Kt_CD.index, minor=False, rotation = 20)
ax3.set_title(u'DC Kt index in the East', loc = 'center', fontsize=9)


ax4 = fig.add_subplot(2,3,4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.bar(np.arange(len(df_Kt_CD)), df_Kt_CD['Kt*_CI'].values, color='#004D56', align='center', alpha=0.5)
ax4.set_xlabel(u'Hour', fontproperties = prop_1)
ax4.set_ylabel(r"Kt*", fontproperties = prop_1)
ax4.set_xticks(range(0,12), minor=False)
ax4.set_xticklabels(df_Kt_CD.index, minor=False, rotation = 20)
ax4.set_title(u'DC Kt* index in the West point', loc = 'center', fontsize=9)

ax5 = fig.add_subplot(2,3,5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.bar(np.arange(len(df_Kt_CD)), df_Kt_CD['Kt*_TS'].values, color='#004D56', align='center', alpha=0.5)
ax5.set_xlabel(u'Hour', fontproperties = prop_1)
ax5.set_ylabel(r"Kt*", fontproperties = prop_1)
ax5.set_xticks(range(0,12), minor=False)
ax5.set_xticklabels(df_Kt_CD.index, minor=False, rotation = 20)
ax5.set_title(u'DC Kt* index in the West Center point', loc = 'center', fontsize=9)

ax6 = fig.add_subplot(2,3,6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.bar(np.arange(len(df_Kt_CD)), df_Kt_CD['Kt*_JV'].values, color='#004D56', align='center', alpha=0.5)
ax6.set_xlabel(u'Hour', fontproperties = prop_1)
ax6.set_ylabel(r"Kt*", fontproperties = prop_1)
ax6.set_xticks(range(0,12), minor=False)
ax6.set_xticklabels(df_Kt_CD.index, minor=False, rotation = 20)
ax6.set_title(u'DC Kt* index in the East point', loc = 'center', fontsize=9)

plt.subplots_adjust(wspace=0.3, hspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CD_KtKt.pdf', format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/CD_KtKt.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')



plt.close("all")
fig = plt.figure(figsize=(10., 8.),facecolor='w',edgecolor='w')
ax1=fig.add_subplot(2,3,1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.bar(np.arange(len(df_Kt_CA)), df_Kt_CA['Kt_CI'].values, color='#8ABB73', align='center', alpha=0.5)
ax1.set_xlabel(u'Month', fontproperties = prop_1)
ax1.set_ylabel(r"Kt", fontproperties = prop_1)
ax1.set_xticks(range(0,12), minor=False)
ax1.set_xticklabels(months, minor=False,fontsize =8, rotation = 35)
ax1.set_title(u'AC Kt index in the West point', loc = 'center', fontsize=9)

ax2=fig.add_subplot(2,3,2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.bar(np.arange(len(df_Kt_CA)), df_Kt_CA['Kt_TS'].values, color='#8ABB73', align='center', alpha=0.5)
ax2.set_xlabel(u'Month', fontproperties = prop_1)
ax2.set_ylabel(r"Kt", fontproperties = prop_1)
ax2.set_xticks(range(0,12), minor=False)
ax2.set_xticklabels(months, minor=False,fontsize =8, rotation = 35)
ax2.set_title(u'AC Kt index in the West Center', loc = 'center', fontsize=9)

ax3 = fig.add_subplot(2,3,3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.bar(np.arange(len(df_Kt_CA)), df_Kt_CA['Kt_JV'].values, color='#8ABB73', align='center', alpha=0.5)
ax3.set_xlabel(u'Month', fontproperties = prop_1)
ax3.set_ylabel(r"Kt", fontproperties = prop_1)
ax3.set_xticks(range(0,12), minor=False)
ax3.set_xticklabels(months, minor=False,fontsize =8, rotation = 35)
ax3.set_title(u'AC Kt index in the East point', loc = 'center', fontsize=9)


ax4 = fig.add_subplot(2,3,4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.bar(np.arange(len(df_Kt_CA)), df_Kt_CA['Kt*_CI'].values, color='#004D56', align='center', alpha=0.5)
ax4.set_xlabel(u'Month', fontproperties = prop_1)
ax4.set_ylabel(r"Kt*", fontproperties = prop_1)
ax4.set_xticks(range(0,12), minor=False)
ax4.set_xticklabels(months, minor=False,fontsize =8, rotation = 35)
ax4.set_title(u'AC Kt* index in the West point', loc = 'center', fontsize=9)

ax5 = fig.add_subplot(2,3,5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.bar(np.arange(len(df_Kt_CA)), df_Kt_CA['Kt*_TS'].values, color='#004D56', align='center', alpha=0.5)
ax5.set_xlabel(u'Month', fontproperties = prop_1)
ax5.set_ylabel(r"Kt*", fontproperties = prop_1)
ax5.set_xticks(range(0,12), minor=False)
ax5.set_xticklabels(months, minor=False,fontsize =8, rotation = 35)
ax5.set_title(u'AC Kt* index in the West Center point', loc = 'center', fontsize=9)

ax6 = fig.add_subplot(2,3,6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.bar(np.arange(len(df_Kt_CA)), df_Kt_CA['Kt*_JV'].values, color='#004D56', align='center', alpha=0.5)
ax6.set_xlabel(u'Month', fontproperties = prop_1)
ax6.set_ylabel(r"Kt*", fontproperties = prop_1)
ax6.set_xticks(range(0,12), minor=False)
ax6.set_xticklabels(months, minor=False,fontsize =8, rotation = 35)
ax6.set_title(u'AC Kt* index in the East point', loc = 'center', fontsize=9)

plt.subplots_adjust(wspace=0.3, hspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CA_KtKt.pdf', format = 'pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/CA_KtKt.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


##-------------------------------GRAFICA CA Y CD DE KT----------------------------##
# """
# Inocente machetito, desde acá
# """
#
# df_Kt_CD.Kt_CI.loc[(df_Kt_CD.index==6)] = [[0.504532]]
# df_Kt_CD.Kt_TS.loc[(df_Kt_CD.index==6)] = [[0.530768]]



plt.close('all')
fig = plt.figure(figsize=(14,8))
ax1 = fig.add_subplot(1, 2, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(df_Kt_CA.index.values,  df_Kt_CA.Kt_CI.values, color = '#52C1BA', lw=1.5, label = 'Oeste')
ax1.scatter(df_Kt_CA.index.values,  df_Kt_CA.Kt_CI.values, marker='.', color = '#52C1BA', s=30)
ax1.plot(df_Kt_CA.index.values,  df_Kt_CA.Kt_TS.values, color = '#09202E', lw=1.5, label = 'Centro-Oeste')
ax1.scatter(df_Kt_CA.index.values,  df_Kt_CA.Kt_TS.values, marker='.', color = '#09202E', s=30)
ax1.plot(df_Kt_CA.index.values,  df_Kt_CA.Kt_JV.values, color = '#0b6623', lw=1.5, label = 'Este')
ax1.scatter(df_Kt_CA.index.values,  df_Kt_CA.Kt_JV.values, marker='.', color = '#0b6623', s=30)
ax1.set_xlabel('Meses', fontproperties = prop_1, fontsize=17)
ax1.set_ylabel(u"Kt", fontproperties = prop_1, fontsize=20)
ax1.set_xticks(range(1, 13), minor=False)
ax1.set_xticklabels(months, minor=False, rotation = 20, fontsize = 12)
ax1.set_yticks(np.arange(0, 1.2, 0.2), minor=False)
ax1.set_yticklabels([0, 0.2, 0.4, 0.6, 0.8, 1], fontsize = 15)
ax1.set_ylim(0, 1)
ymax = max(max(df_Kt_CA.Kt_CI.values),max(df_Kt_CA.Kt_TS.values), max(df_Kt_CA.Kt_JV.values))
xpos = list(df_Kt_CA.Kt_TS.values).index(ymax)
xmax = df_Kt_CA.index[xpos]
ax1.annotate(u'Máximo  en: '+  months[xpos] , xy=(xmax, ymax), xytext=(xmax, ymax+0.05),arrowprops=dict(facecolor='black', shrink=0.05), fontproperties = prop_1,fontsize = 12)
ymin = min(min(df_Kt_CA.Kt_CI.values),min(df_Kt_CA.Kt_TS.values), min(df_Kt_CA.Kt_JV.values))
xpos = list(df_Kt_CA.Kt_JV.values).index(ymin)
xmin = df_Kt_CA.index[xpos]
ax1.annotate(u'Mínimo  en: '+  months[xpos] , xy=(xmin, ymin), xytext=(xmin, ymin-0.063),arrowprops=dict(facecolor='black', shrink=0.05), fontproperties = prop_1,fontsize = 12)
ax1.set_title(u'Ciclo anual del índice de transparencia $Kt$ ', loc = 'center', fontproperties = prop, fontsize=17)
plt.legend()

ax2 = fig.add_subplot(1, 2, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(df_Kt_CD.index.values,  df_Kt_CD.Kt_CI.values, color = '#52C1BA', lw=1.5, label = 'Oeste')
ax2.scatter(df_Kt_CD.index.values,  df_Kt_CD.Kt_CI.values, marker='.', color = '#52C1BA', s=30)
ax2.plot(df_Kt_CD.index.values,  df_Kt_CD.Kt_TS.values, color = '#09202E', lw=1.5, label = 'Centro-Oeste')
ax2.scatter(df_Kt_CD.index.values,  df_Kt_CD.Kt_TS.values, marker='.', color = '#09202E', s=30)
ax2.plot(df_Kt_CD.index.values,  df_Kt_CD.Kt_JV.values, color = '#0b6623', lw=1.5, label = 'Este')
ax2.scatter(df_Kt_CD.index.values,  df_Kt_CD.Kt_JV.values, marker='.', color = '#0b6623', s=30)
ax2.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax2.set_ylabel(u"Kt", fontproperties = prop_1, fontsize=20)
ax2.set_xticks(range(6, 18), minor=False)
ax2.set_xticklabels(df_Kt_CD.index, minor=False, rotation = 20,fontsize = 12)
ax2.set_yticks(np.arange(0, 1.2, 0.2), minor=False)
ax2.set_yticklabels([0, 0.2, 0.4, 0.6,0.8, 1], fontsize = 15)
ax2.set_ylim(0, 1)
ymax = max(max(df_Kt_CD.Kt_CI.values),max(df_Kt_CD.Kt_TS.values), max(df_Kt_CD.Kt_JV.values))
xpos = list(df_Kt_CD.Kt_TS.values).index(ymax)
xmax = df_Kt_CD.index[xpos]
ax2.annotate(u'Máximo  a las: '+  str(df_Kt_CD.index[xpos])+'hrs' , xy=(xmax, ymax), xytext=(xmax, ymax+0.05),arrowprops=dict(facecolor='black', shrink=0.05), fontproperties = prop_1,fontsize = 12)
ax2.set_title(u'Ciclo diurno del índice de transparencia $Kt$ ', loc = 'center', fontproperties = prop, fontsize=17)
plt.legend()

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.2, hspace=0.25)
plt.show()


plt.savefig('/home/nacorreasa/Escritorio/Figuras/CD_CA_Kt.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/CD_CA_Kt.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

#################################################################################
## -------------------------------VARIANZAS DE KT---------------------------- ##
#################################################################################
new_idx_CD = np.arange(6, 18, 1)
df_Kt_VD  = df_Kt.groupby(by=[df_Kt.index.hour]).var()
df_Kt_VD  = df_Kt_VD.reindex(new_idx_CD)

new_idx_CA = np.arange(1, 13, 1)
df_Kt_VA = df_Kt.groupby([df_Kt.index.month, ]).var()


##-------------------------------GRAFICA CA Y CD DE KT----------------------------##

plt.close('all')
fig = plt.figure(figsize=(14,8))
ax1 = fig.add_subplot(1, 2, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(df_Kt_VA.index.values,  df_Kt_VA.Kt_CI.values, color = '#52C1BA', lw=1.5, label = 'Oeste')
ax1.scatter(df_Kt_VA.index.values,  df_Kt_VA.Kt_CI.values, marker='.', color = '#52C1BA', s=30)
ax1.plot(df_Kt_VA.index.values,  df_Kt_VA.Kt_TS.values, color = '#09202E', lw=1.5, label = 'Centro-Oeste')
ax1.scatter(df_Kt_VA.index.values,  df_Kt_VA.Kt_TS.values, marker='.', color = '#09202E', s=30)
ax1.plot(df_Kt_VA.index.values,  df_Kt_VA.Kt_JV.values, color = '#0b6623', lw=1.5, label = 'Este')
ax1.scatter(df_Kt_VA.index.values,  df_Kt_VA.Kt_JV.values, marker='.', color = '#0b6623', s=30)
ax1.set_xlabel('Meses', fontproperties = prop_1, fontsize=17)
ax1.set_ylabel(u"Kt", fontproperties = prop_1, fontsize=20)
ax1.set_xticks(range(1, 13), minor=False)
ax1.set_xticklabels(months, minor=False, rotation = 20, fontsize = 12)
ax1.set_yticks(np.arange(0, 0.3, 0.05), minor=False)
ax1.set_yticklabels([0.  , 0.05, 0.1 , 0.15, 0.2], fontsize = 15)
ax1.set_ylim(0, 0.2)
ymax = max(max(df_Kt_VA.Kt_CI.values),max(df_Kt_VA.Kt_TS.values), max(df_Kt_VA.Kt_JV.values))
xpos = list(df_Kt_VA.Kt_JV.values).index(ymax)
xmax = df_Kt_VA.index[xpos]
ax1.annotate(u'Máxima  en: '+  months[xpos] , xy=(xmax, ymax), xytext=(xmax, ymax+0.012),arrowprops=dict(facecolor='black', shrink=0.05), fontproperties = prop_1,fontsize = 12)
ymin = min(min(df_Kt_VA.Kt_CI.values),min(df_Kt_VA.Kt_TS.values), min(df_Kt_VA.Kt_JV.values))
xpos = list(df_Kt_VA.Kt_JV.values).index(ymin)
xmin = df_Kt_VA.index[xpos]
ax1.annotate(u'Mínima  en: '+  months[xpos] , xy=(xmin, ymin), xytext=(xmin, ymin-0.015),arrowprops=dict(facecolor='black', shrink=0.05), fontproperties = prop_1,fontsize = 12)
ax1.set_title(u'Varianza mensual del índice de transparencia $Kt$ ', loc = 'center', fontproperties = prop, fontsize=17)
plt.legend()

ax2 = fig.add_subplot(1, 2, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(df_Kt_VD.index.values,  df_Kt_VD.Kt_CI.values, color = '#52C1BA', lw=1.5, label = 'Oeste')
ax2.scatter(df_Kt_VD.index.values,  df_Kt_VD.Kt_CI.values, marker='.', color = '#52C1BA', s=30)
ax2.plot(df_Kt_VD.index.values,  df_Kt_VD.Kt_TS.values, color = '#09202E', lw=1.5, label = 'Centro-Oeste')
ax2.scatter(df_Kt_VD.index.values,  df_Kt_VD.Kt_TS.values, marker='.', color = '#09202E', s=30)
ax2.plot(df_Kt_VD.index.values,  df_Kt_VD.Kt_JV.values, color = '#0b6623', lw=1.5, label = 'Este')
ax2.scatter(df_Kt_VD.index.values,  df_Kt_VD.Kt_JV.values, marker='.', color = '#0b6623', s=30)
ax2.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax2.set_ylabel(u"Kt", fontproperties = prop_1, fontsize=20)
ax2.set_xticks(range(6, 18), minor=False)
ax2.set_xticklabels(df_Kt_VD.index, minor=False, rotation = 20,fontsize = 12)
ax2.set_yticks(np.arange(0, 0.3, 0.05), minor=False)
ax2.set_yticklabels([0.  , 0.05, 0.1 , 0.15, 0.2], fontsize = 15)
ax2.set_ylim(0, 0.2)
ymax = max(max(df_Kt_VD.Kt_CI.values),max(df_Kt_VD.Kt_TS.values), max(df_Kt_VD.Kt_JV.values))
xpos = list(df_Kt_VD.Kt_JV.values).index(ymax)
xmax = df_Kt_VD.index[xpos]
ax2.annotate(u'Máxima  a las: '+  str(df_Kt_VD.index[xpos])+'hrs' , xy=(xmax, ymax), xytext=(xmax, ymax+0.012),arrowprops=dict(facecolor='black', shrink=0.05), fontproperties = prop_1,fontsize = 12)
ax2.set_title(u'Varianza diurna del índice de transparencia $Kt$ ', loc = 'center', fontproperties = prop, fontsize=17)
plt.legend()

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.2, hspace=0.25)
plt.show()


plt.savefig('/home/nacorreasa/Escritorio/Figuras/VA_VD_Kt.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/VA_VD_Kt.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')






#################################################################################
## ---------------------------TASA DE CAMBIO DE KT*--------------------------- ##
#################################################################################
"En este caso la tasa de cambio es a una hora"
df_TasaCambio_1h = df_Kt.diff()
"En este caso la tasa de cambio es a 6 horas, ahora a las 6 hora, una diferencia rezagada"
df_TasaCambio_6h = df_Kt.diff(periods = 6)
"En este caso la tasa de cambio es a 6 horas, ahora a las 6 hora, una diferencia rezagada"
df_TasaCambio_11h = df_Kt.diff(periods = 11)


"Ciclo diurno de la tasa de cambio a una hora"
df_TasaCambio_1h_CD = df_TasaCambio_1h.groupby(by=[df_TasaCambio_1h.index.hour]).mean()

#################################################################################
## ------------------------COMULATIVE DENSITY FUNCTION------------------------ ##
#################################################################################


hist_1h_TS, bin_edges_1h_TS = np.histogram(df_TasaCambio_1h['Kt*_TS'][~np.isnan(df_TasaCambio_1h['Kt*_TS'])].values)
cum_1h_TS = np.cumsum(hist_1h_TS)
cum_1h_TS=(cum_1h_TS - cum_1h_TS.min()) / cum_1h_TS.ptp()

hist_6h_TS, bin_edges_6h_TS = np.histogram(df_TasaCambio_6h['Kt*_TS'][~np.isnan(df_TasaCambio_6h['Kt*_TS'])].values)
cum_6h_TS = np.cumsum(hist_6h_TS)
cum_6h_TS=(cum_6h_TS - cum_6h_TS.min()) / cum_6h_TS.ptp()

hist_11h_TS, bin_edges_11h_TS = np.histogram(df_TasaCambio_11h['Kt*_TS'][~np.isnan(df_TasaCambio_11h['Kt*_TS'])].values)
cum_11h_TS = np.cumsum(hist_11h_TS)
cum_11h_TS=(cum_11h_TS - cum_11h_TS.min()) / cum_11h_TS.ptp()


hist_1h_CI, bin_edges_1h_CI = np.histogram(df_TasaCambio_1h['Kt*_CI'][~np.isnan(df_TasaCambio_1h['Kt*_CI'])].values)
cum_1h_CI = np.cumsum(hist_1h_CI)
cum_1h_CI=(cum_1h_CI - cum_1h_CI.min()) / cum_1h_CI.ptp()

hist_6h_CI, bin_edges_6h_CI = np.histogram(df_TasaCambio_6h['Kt*_CI'][~np.isnan(df_TasaCambio_6h['Kt*_CI'])].values)
cum_6h_CI = np.cumsum(hist_6h_CI)
cum_6h_CI=(cum_6h_CI - cum_6h_CI.min()) / cum_6h_CI.ptp()

hist_11h_CI, bin_edges_11h_CI = np.histogram(df_TasaCambio_11h['Kt*_CI'][~np.isnan(df_TasaCambio_11h['Kt*_CI'])].values)
cum_11h_CI = np.cumsum(hist_11h_CI)
cum_11h_CI=(cum_11h_CI - cum_11h_CI.min()) / cum_11h_CI.ptp()


hist_1h_JV, bin_edges_1h_JV = np.histogram(df_TasaCambio_1h['Kt*_JV'][~np.isnan(df_TasaCambio_1h['Kt*_JV'])].values)
cum_1h_JV = np.cumsum(hist_1h_JV)
cum_1h_JV=(cum_1h_JV - cum_1h_JV.min()) / cum_1h_JV.ptp()

hist_6h_JV, bin_edges_6h_JV = np.histogram(df_TasaCambio_6h['Kt*_JV'][~np.isnan(df_TasaCambio_6h['Kt*_JV'])].values)
cum_6h_JV = np.cumsum(hist_6h_JV)
cum_6h_JV=(cum_6h_JV - cum_6h_JV.min()) / cum_6h_JV.ptp()

hist_11h_JV, bin_edges_11h_JV = np.histogram(df_TasaCambio_11h['Kt*_JV'][~np.isnan(df_TasaCambio_11h['Kt*_JV'])].values)
cum_11h_JV = np.cumsum(hist_11h_JV)
cum_11h_JV=(cum_11h_JV - cum_11h_JV.min()) / cum_11h_JV.ptp()



fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(bin_edges_1h_CI[1:], cum_1h_CI, color='#004D56', label = 'CDF 1h')
ax1.plot(bin_edges_6h_CI[1:], cum_6h_CI, color='#70AFBA', label = 'CDF 6h')
ax1.plot(bin_edges_11h_CI[1:], cum_11h_CI, color='#C7D15D', label = 'CDF 11h')
ax1.set_title(u'FDA de la tasa de cambio de Kt* \n  en el Oeste', fontproperties=prop, fontsize = 8)
ax1.set_ylabel(u'Probabilidad', fontproperties=prop_1)
ax1.set_xlabel(u'Tasa de cambio', fontproperties=prop_1)
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(bin_edges_1h_TS[1:], cum_1h_TS, color='#004D56', label = 'CDF 1h')
ax2.plot(bin_edges_6h_TS[1:], cum_6h_TS, color='#70AFBA', label = 'CDF 6h')
ax2.plot(bin_edges_11h_TS[1:], cum_11h_TS, color='#C7D15D', label = 'CDF 11h')
ax2.set_title(u'FDA de la tasa de cambio de Kt* \n  en el Centro-Oeste', fontproperties=prop, fontsize = 8)
ax2.set_ylabel(u'Probabilidad', fontproperties=prop_1)
ax2.set_xlabel(u'Tasa de cambio', fontproperties=prop_1)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.plot(bin_edges_1h_JV[1:], cum_1h_JV, color='#004D56', label = 'CDF 1h')
ax3.plot(bin_edges_6h_JV[1:], cum_6h_JV, color='#70AFBA', label = 'CDF 6h')
ax3.plot(bin_edges_11h_JV[1:], cum_11h_JV, color='#C7D15D', label = 'CDF 11h')
ax3.set_title(u'FDA de la tasa de cambio de Kt* \n  en el Este', fontproperties=prop, fontsize = 8)
ax3.set_ylabel(u'Probabilidad', fontproperties=prop_1)
ax3.set_xlabel(u'Tasa de cambio', fontproperties=prop_1)
ax3.legend()

plt.show()

plt.savefig('/home/nacorreasa/Escritorio/Figuras/CDF_Kt*Rates.pdf', format = 'pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/CDF_Kt*Rates.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
