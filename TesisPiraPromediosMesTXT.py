# -*- coding: utf-8 -*-
import MySQLdb
import pandas as pd
import datetime

df1 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6001.txt', parse_dates=[2])
df1 = df1.set_index(["fecha_hora"])
df1.index = df1.index.tz_localize('UTC').tz_convert('America/Bogota')
df1.index = df1.index.tz_localize(None)

df2 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6002.txt', parse_dates=[2])
df2 = df2.set_index(["fecha_hora"])
df2.index = df2.index.tz_localize('UTC').tz_convert('America/Bogota')
df2.index = df2.index.tz_localize(None)

df3 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6003.txt', parse_dates=[2])
df3 = df3.set_index(["fecha_hora"])
df3.index = df3.index.tz_localize('UTC').tz_convert('America/Bogota')
df3.index = df3.index.tz_localize(None)

df4 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6004.txt', parse_dates=[2])
df4 = df4.set_index(["fecha_hora"])
df4.index = df4.index.tz_localize('UTC').tz_convert('America/Bogota')
df4.index = df4.index.tz_localize(None)

df5 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6005.txt', parse_dates=[2])
df5 = df5.set_index(["fecha_hora"])
df5.index = df5.index.tz_localize('UTC').tz_convert('America/Bogota')
df5.index = df5.index.tz_localize(None)

pira = '%pira%'
sentencia_coordenadas = "SELECT codigo, latitude, longitude  FROM estaciones WHERE nombreestacion LIKE '{}' ;".format(pira)

def ejecutar_consulta_sql(sentencia):
    db = MySQLdb.connect(host="192.168.1.74", user="siata_Calidad", passwd="si@t@0802_calidad", db="siata");
    cursor = db.cursor()
    cursor.execute(sentencia)
    resultado = cursor.fetchall()
    cursor.close()
    db.close()
    return resultado


coordenadas = ejecutar_consulta_sql(sentencia_coordenadas)

columnasC = ['Codigo', 'Latitud', 'Longitud' ]

df_coord = pd.DataFrame(list(coordenadas), columns = columnasC)


# Estableciendo las fechas a consultar de los datos de un año completo:
fec_ini = datetime.datetime.strptime('2017-10-01 00:00:00', "%Y-%m-%d %H:%M:%S")
fec_fin = datetime.datetime.strptime('2018-09-30 23:59:00', "%Y-%m-%d %H:%M:%S")
new_idx = pd.date_range(fec_ini.date(), fec_fin.date() + pd.Timedelta('1 day'), freq='T')

df1 = df1[fec_ini:fec_fin]
df2 = df2[fec_ini:fec_fin]
df3 = df3[fec_ini:fec_fin]
df4 = df4[fec_ini:fec_fin]
df5 = df5[fec_ini:fec_fin]

df1 = df1.reindex(new_idx)
df2 = df2.reindex(new_idx)
df3 = df3.reindex(new_idx)
df4 = df4.reindex(new_idx)
df5 = df5.reindex(new_idx)

df1 = df1.drop(df1.index[len(df1)-1])
df2 = df2.drop(df2.index[len(df2)-1])
df3 = df3.drop(df3.index[len(df3)-1])
df4 = df4.drop(df4.index[len(df4)-1])
df5 = df5.drop(df5.index[len(df5)-1])

df1_CA = df1.groupby(by=[df1.index.month]).mean()
df2_CA = df2.groupby(by=[df2.index.month]).mean()
df3_CA = df3.groupby(by=[df3.index.month]).mean()
df4_CA = df4.groupby(by=[df4.index.month]).mean()
df5_CA = df5.groupby(by=[df5.index.month]).mean()

Oct = []
Oct.append(round(df1_CA['radiacion'].values[0], 2))
Oct.append(round(df2_CA['radiacion'].values[0], 2))
Oct.append(round(df3_CA['radiacion'].values[0], 2))
Oct.append(round(df4_CA['radiacion'].values[0], 2))
Oct.append(round(df5_CA['radiacion'].values[0], 2))

Nov = []
Nov.append(round(df1_CA['radiacion'].values[1], 2))
Nov.append(round(df2_CA['radiacion'].values[1], 2))
Nov.append(round(df3_CA['radiacion'].values[1], 2))
Nov.append(round(df4_CA['radiacion'].values[1], 2))
Nov.append(round(df5_CA['radiacion'].values[1], 2))

Dic = []
Dic.append(round(df1_CA['radiacion'].values[2], 2))
Dic.append(round(df2_CA['radiacion'].values[2], 2))
Dic.append(round(df3_CA['radiacion'].values[2], 2))
Dic.append(round(df4_CA['radiacion'].values[2], 2))
Dic.append(round(df5_CA['radiacion'].values[2], 2))

Ene = []
Ene.append(round(df1_CA['radiacion'].values[3], 2))
Ene.append(round(df2_CA['radiacion'].values[3], 2))
Ene.append(round(df3_CA['radiacion'].values[3], 2))
Ene.append(round(df4_CA['radiacion'].values[3], 2))
Ene.append(round(df5_CA['radiacion'].values[3], 2))

Feb = []
Feb.append(round(df1_CA['radiacion'].values[4], 2))
Feb.append(round(df2_CA['radiacion'].values[4], 2))
Feb.append(round(df3_CA['radiacion'].values[4], 2))
Feb.append(round(df4_CA['radiacion'].values[4], 2))
Feb.append(round(df5_CA['radiacion'].values[4], 2))

Mar = []
Mar.append(round(df1_CA['radiacion'].values[5], 2))
Mar.append(round(df2_CA['radiacion'].values[5], 2))
Mar.append(round(df3_CA['radiacion'].values[5], 2))
Mar.append(round(df4_CA['radiacion'].values[5], 2))
Mar.append(round(df5_CA['radiacion'].values[5], 2))

Abr = []
Abr.append(round(df1_CA['radiacion'].values[6], 2))
Abr.append(round(df2_CA['radiacion'].values[6], 2))
Abr.append(round(df3_CA['radiacion'].values[6], 2))
Abr.append(round(df4_CA['radiacion'].values[6], 2))
Abr.append(round(df5_CA['radiacion'].values[6], 2))

May = []
May.append(round(df1_CA['radiacion'].values[7], 2))
May.append(round(df2_CA['radiacion'].values[7], 2))
May.append(round(df3_CA['radiacion'].values[7], 2))
May.append(round(df4_CA['radiacion'].values[7], 2))
May.append(round(df5_CA['radiacion'].values[7], 2))

Jun = []
Jun.append(round(df1_CA['radiacion'].values[8], 2))
Jun.append(round(df2_CA['radiacion'].values[8], 2))
Jun.append(round(df3_CA['radiacion'].values[8], 2))
Jun.append(round(df4_CA['radiacion'].values[8], 2))
Jun.append(round(df5_CA['radiacion'].values[8], 2))

Jul = []
Jul.append(round(df1_CA['radiacion'].values[9], 2))
Jul.append(round(df2_CA['radiacion'].values[9], 2))
Jul.append(round(df3_CA['radiacion'].values[9], 2))
Jul.append(round(df4_CA['radiacion'].values[9], 2))
Jul.append(round(df5_CA['radiacion'].values[9], 2))

Ago = []
Ago.append(round(df1_CA['radiacion'].values[10], 2))
Ago.append(round(df2_CA['radiacion'].values[10], 2))
Ago.append(round(df3_CA['radiacion'].values[10], 2))
Ago.append(round(df4_CA['radiacion'].values[10], 2))
Ago.append(round(df5_CA['radiacion'].values[10], 2))

Sep = []
Sep.append(round(df1_CA['radiacion'].values[11], 2))
Sep.append(round(df2_CA['radiacion'].values[11], 2))
Sep.append(round(df3_CA['radiacion'].values[11], 2))
Sep.append(round(df4_CA['radiacion'].values[11], 2))
Sep.append(round(df5_CA['radiacion'].values[11], 2))

df = pd.DataFrame()
df['Latitud'] = list(df_coord['Latitud'].values)
df['Longitud'] = list(df_coord['Longitud'].values)
df['Enero'] = Ene
df['Febrero'] = Feb
df['Marzo'] = Mar
df['Abril'] = Abr
df['Mayo'] = May
df['Junio'] = Jun
df['Julio'] = Jul
df['Agosto'] = Ago
df['Septiembre'] = Sep
df['Octubre'] = Oct
df['Noviembre'] = Nov
df['Diciembre']= Dic

df.to_csv(r"/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/CA_entre"+str(fec_fin.date())+"&"+str(fec_fin.date())+".txt", header=True, index=None, sep=' ', mode='a')


