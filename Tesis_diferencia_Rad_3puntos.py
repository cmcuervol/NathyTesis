#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.font_manager as fm
import math as m
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.transforms as transforms
import datetime
import psycopg2

Estaciones = ['6001', '6002', '6003']

fec_ini = '2019-12-01'
fec_fin = '2019-12-01'
hora_ini = '00:00:00'
hora_fin = '23:59:59'

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

'Codigo en el que se grafican los datos de radiación de un dia despejado de los tres puntos de medición'
'con el propósito de observar las diferencias de radiación incidente entre cada uno de los puntos.'

#############################################
##-------NO CAMBIAR NADA EN ADELANTE-------##
#############################################

fi = datetime.datetime.strptime(fec_ini, '%Y-%m-%d')
ff = datetime.datetime.strptime(fec_fin, '%Y-%m-%d')
hi = datetime.datetime.strptime(hora_ini, '%H:%M:%S')
hf = datetime.datetime.strptime(hora_fin, '%H:%M:%S')

if (ff < fi) == True:
    sys.exit("Escriba bien las fechas care monda... porfa")
elif ff-fi == datetime.timedelta(days=0):
    time = 0
    if (hf < hi) == True:
        sys.exit("Copie bien las horas burro... porfa")
    else:
        pass
else:
    time = 1

#-----------------------------------------------------------------------------
# Rutas para guardar ---------------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##---------------------------------------------------------------------------------------------------------##

def ejecutar_consulta_sql(sentencia):
    db = pymysql.connect(host="192.168.1.100", user="siata_Calidad", passwd="si@t@0803_calidad", db="siata");
    cursor = db.cursor()
    cursor.execute(sentencia)
    resultado = cursor.fetchall()
    cursor.close()
    db.close()
    return resultado
##---------------------------------------------------------------------------------------------------------##

host   = "192.168.1.74"
user   = "siata_Calidad"
passwd = "si@t@0802_calidad"
dbname = "newsiata"
df_result = pd.DataFrame()
for i in range(len(Estaciones)):

    estacion = Estaciones[i]

    query1 = "SELECT idestacion, fecha_hora, radiacion, temperatura FROM dato_piranometro WHERE idestacion = "+estacion+" " \
         "AND fecha_hora BETWEEN '{} 00:00:00' AND '{} 23:59:00' ORDER BY idestacion, fecha_hora;".format(fec_ini, fec_fin)

    print (query1)

    conn_db = psycopg2.connect("dbname='" + dbname + "' user='" + user +"' host='" + host + "' password='" + passwd + "'")
    db_cursor = conn_db.cursor ()
    db_cursor.execute (query1)
    data_db = db_cursor.fetchall ()
    df_pira = pd.read_sql (query1, conn_db)
    conn_db.close()
    df_pira = df_pira.set_index(["fecha_hora"])
    df_pira.index = df_pira.index.tz_localize('UTC').tz_convert('America/Bogota')
    df_pira.index = df_pira.index.tz_localize(None)

    df_result = pd.concat([df_result, df_pira], axis=1, sort=False)
df_result.index = pd.to_datetime(df_result.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_result.columns = ['idestacion 6001', 'radiacion 6001', 'temperatura 6001', 'idestacion 6002', 'radiacion 6002', 'temperatura 6002', 'idestacion 6003', 'radiacion 6003', 'temperatura 6003' ]
df_result_h = df_result.groupby(pd.Grouper(freq="H")).mean()
df_result_h = df_result_h.between_time('06:00', '17:59')

#########################
##------GRAFICA--------##
#########################

x_pos = np.arange(len(df_result_h.index))
x_pos1 = np.arange(0.75, len(df_result_h.index) + 0.75, 1)

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax=fig.add_subplot()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.bar(np.arange(len(df_result_h.index.values))+0.5, np.array(df_result_h['radiacion 6001'].values), color= '#2ECC71', label='TS',  width = 0.25)
plt.bar(np.arange(len(df_result_h.index.values))+0.75, np.array(df_result_h['radiacion 6002'].values), color='#F7DC6F', label='CI',  width = 0.25)
plt.bar(np.arange(len(df_result_h.index.values))+1., np.array(df_result_h['radiacion 6003'].values), color='#F39C12', label='JV',  width = 0.25)
plt.xticks(x_pos1, (df_result_h.index.hour), fontsize=10, fontproperties=prop, rotation=20 )
plt.xlabel(u'Horas del dia', fontproperties=prop_1)
plt.ylabel(r"$[W/m^{2}]$", fontproperties=prop_1)
plt.title(u'Promedio horario de la radiación horizontal  \n de un día despejado en los tres puntos de medición el ' + fec_ini,   fontweight = "bold",  fontproperties = prop)
plt.legend()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Media_horaria_dia_desp'+ fec_ini+'.png')
plt.show()
