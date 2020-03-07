#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
import pandas as pd
import datetime
import numpy as np

"Código para la consulta de datos de lluvia ya sea de la red pluviografica o meteorológica, la consulta se hace dentro de un intervalo de tiempo y para"
"las estaciones a consultar son defindas en el str de queryest y son sumado a una frecuencia especificada, apra ser guardados en el Path_Save. Ya se  "
"toman en cuenta los indicadores de calidad respectivo para la creación de los archivos."

Path_Save = '/home/nacorreasa/Maestria/Datos_Tesis/Pluvio'
fec_ini = '2018-01-01'
fec_fin = '2018-12-31'
queryest = "SELECT distinct codigo, nombreestacion, estado, red FROM  estaciones WHERE codigo IN ('211', '206', '201') AND estado <> 'I' ;"   ##--> query con el codigo de las estaciones deseadas a consultar
Frecuencia = "H"                                                                                                                              ##--> Str de la frecuencia diaria ("D"), horaria ("H"), mensual ("M") a la cual se acumularan los datos

####################################################
##---------NO CAMBIAR NADA EN ADELANTE------------##
####################################################

def ejecutar_consulta_sql(sentencia):
    db = pymysql.connect(host="192.168.1.100", user="siata_Calidad", passwd="si@t@0802_calidad", db="siata");
    cursor = db.cursor()
    cursor.execute(sentencia)
    resultado = cursor.fetchall()
    cursor.close()
    db.close()
    return resultado

estaciones0 = ejecutar_consulta_sql(queryest)

Datos_Acum = pd.DataFrame()
red = []
ad = []
for i in range(len(estaciones0)):
    ad.append(estaciones0[i][0])
    red.append(estaciones0[i][3])

for j in range(len(ad)):
    if red[j] == 'pluviografica':
        ##----CONSULTA DATOS----##
        sentencia_pluvio = "SELECT cliente,  CONCAT(DATE_FORMAT (CONCAT(fecha,' ' ,hora), '%Y-%m-%d %H:%i'), ':00') AS " \
                              "fecha_hora, (p1/1000),(p2/1000), calidad  FROM datos WHERE cliente = {}" \
                              " AND fecha BETWEEN '{}' AND '{}' ;".format( str(ad[j]), fec_ini, fec_fin)
        datos = ejecutar_consulta_sql(sentencia_pluvio)
        columnas = ['codigo', 'fecha_hora', 'P1', 'P2', 'calidad']

        if len(datos) > 0:
            df_datos = pd.DataFrame(list(datos), columns = columnas)
            del datos
            df_datos.index = df_datos['fecha_hora']
            df_datos.index = pd.to_datetime(df_datos.index , format="%Y-%m-%d %H:%M:%S", errors='coerce')
            df_datos = df_datos.drop('fecha_hora', axis=1)

        ##----FILTROS DE CALIDAD----##
            df_datos = df_datos[df_datos['calidad'] != 151]
            df_datos.loc[df_datos['calidad'] == 1511, 'P1'] = np.nan
            df_datos.loc[df_datos['calidad'] == 1512, 'P2'] = np.nan

        ##----ACUMULANDO AL PERIODO DE TIEMPO----##
            df_datos_d =  df_datos.groupby(pd.Grouper(freq=Frecuencia)).sum()
            df_datos_d = df_datos_d.drop('calidad', axis=1)

        ##----GUARDANDO EL ARCHIVO EN EL PATH_SAVE----##
            df_datos_d.to_csv(Path_Save +"/Acum"+Frecuencia +ad[j]+".csv", sep=',')

            del df_datos_d, df_datos

    elif red[j] == 'meteorologica':
        ##----CONSULTA DATOS----##
        sentencia_meteo = "SELECT cliente, DATE_FORMAT (concat(fecha,' ' ,hora), '%Y-%m-%d %H:%i:%s') AS fecha_hora, " \
                                "(rc/100), calidad  FROM vaisala WHERE cliente = {}" \
                              " AND fecha BETWEEN '{}' AND '{}'  AND calidad NOT IN (151, 251, 1511, 1513, 15134, 15135, " \
                              "15136, 151361, 151362, 15137, 151371, 151372, 1514, 15145, 15146, 151461, 151462, 15147, 151471," \
                              "151472, 1515, 15156, 151561, 151562, 15157, 151571, 151572, 1516, 15167, 151671, 151672, 15161," \
                              "151617, 1516171, 1516172, 15162, 151627, 1516271, 1516272, 1517, 15171, 15172, 2511, 2513, 25134," \
                              "25135, 25136, 251361, 251362, 25137, 251371, 251372, 2514, 25145, 25146, 251461, 251462, 25147," \
                              "251471, 251472, 2515, 25156, 251561, 251562, 25157, 251571, 251572, 2516, 25167, 251671, 251672," \
                              "25161, 251617, 2516171, 2516172, 25162, 251627, 2516271, 2516272, 2517, 25171, 25172);".format( str(ad[j]), fec_ini, fec_fin)
        datos = ejecutar_consulta_sql(sentencia_meteo)
        columnas = ['codigo', 'fecha_hora', 'Precip', 'calidad']

        if len(datos) > 0:
            df_datos = pd.DataFrame(list(datos), columns = columnas)
            del datos
            df_datos.index = df_datos['fecha_hora']
            df_datos.index = pd.to_datetime(df_datos.index , format="%Y-%m-%d %H:%M:%S", errors='coerce')
            df_datos = df_datos.drop('fecha_hora', axis=1)

        ##----FILTROS DE CALIDAD----##
            df_datos = df_datos[df_datos['calidad'] != 151]
            'Fueron implementados en la sentencia de MySQL, considerando que solo interesaban los de lluvia'

        ##----ACUMULANDO AL PERIODO DE TIEMPO----##
            df_datos_d =  df_datos.groupby(pd.Grouper(freq=Frecuencia)).sum()
            df_datos_d = df_datos_d.drop('calidad', axis=1)

        ##----GUARDANDO EL ARCHIVO EN EL PATH_SAVE----##
            df_datos_d.to_csv(Path_Save +"/Acum"+Frecuencia +ad[j]+".csv", sep=',')

            del df_datos_d, df_datos

    elif red[j] == 'meteorologica_thiess':
        ##----CONSULTA DATOS----##
        sentencia_meteo = "SELECT cliente,  DATE_FORMAT (concat(fecha,' ' ,hora), '%Y-%m-%d %H:%i:%s') AS fecha_hora," \
                               " p, calidad  FROM meteo_thiess WHERE cliente = {}" \
                              " AND fecha BETWEEN '{}' AND '{}'  AND calidad NOT IN (151, 251, 1511, 1513, 15134, 15135, " \
                              "15136, 151361, 151362, 15137, 151371, 151372, 1514, 15145, 15146, 151461, 151462, 15147, 151471," \
                              "151472, 1515, 15156, 151561, 151562, 15157, 151571, 151572, 1516, 15167, 151671, 151672, 15161," \
                              "151617, 1516171, 1516172, 15162, 151627, 1516271, 1516272, 1517, 15171, 15172, 2511, 2513, 25134," \
                              "25135, 25136, 251361, 251362, 25137, 251371, 251372, 2514, 25145, 25146, 251461, 251462, 25147," \
                              "251471, 251472, 2515, 25156, 251561, 251562, 25157, 251571, 251572, 2516, 25167, 251671, 251672," \
                              "25161, 251617, 2516171, 2516172, 25162, 251627, 2516271, 2516272, 2517, 25171, 25172);".format( str(ad[j]), fec_ini, fec_fin)
        datos = ejecutar_consulta_sql(sentencia_meteo)
        columnas = ['codigo', 'fecha_hora', 'Precip', 'calidad']

        if len(datos) > 0:
            df_datos = pd.DataFrame(list(datos), columns = columnas)
            del datos
            df_datos.index = df_datos['fecha_hora']
            df_datos.index = pd.to_datetime(df_datos.index , format="%Y-%m-%d %H:%M:%S", errors='coerce')
            df_datos = df_datos.drop('fecha_hora', axis=1)

        ##----FILTROS DE CALIDAD----##
            df_datos = df_datos[df_datos['calidad'] != 151]
            'Fueron implementados en la sentencia de MySQL, considerando que solo interesaban los de lluvia'

        ##----ACUMULANDO AL PERIODO DE TIEMPO----##
            df_datos_d =  df_datos.groupby(pd.Grouper(freq=Frecuencia)).sum()
            df_datos_d = df_datos_d.drop('calidad', axis=1)

        ##----GUARDANDO EL ARCHIVO EN EL PATH_SAVE----##
            df_datos_d.to_csv(Path_Save +"/Acum"+Frecuencia +ad[j]+".csv", sep=',')

            del df_datos_d, df_datos

print('Hemos terminado')
