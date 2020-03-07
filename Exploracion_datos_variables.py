#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
from scipy import stats
# from mpl_toolkits.axes_grid1 import host_subplot
# import mpl_toolkits.axisartist as AA
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.cm as cm
import matplotlib.font_manager as fm
import math as m
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.transforms as transforms
import matplotlib.colors as colors
import netCDF4 as nc
from netCDF4 import Dataset
from pysolar.solar import *
import scipy.stats as st
import scipy.special as sp

## ----------------ACOTANDO LAS FECHAS POR DIA Y MES PARA TOMAR LOS DATOS---------------- ##
fi_m = 3
fi_d = 23
ff_m = 8
ff_d = 22
Anio_datosGOES = 2019
Latitudes = [6.259, 6.168, 6.255]        ## En orden: 6001, 6002, 6003
Longitudes = [-75.588, -75.644, -75.542] ## En orden: 6001, 6002, 6003
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

## ----------------LECTURA DE LOS DATOS DE LOS EXPERIMENTOS---------------- ##

df_P975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel975.txt',  sep=',', index_col =0)
df_P350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel350.txt',  sep=',', index_col =0)
df_P348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel348.txt',  sep=',', index_col =0)

def lectura_datos_piranometro(df):
    df['Fecha_hora'] = df.index
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
    ## -----------------ACOTANDO LOS DATOS A VALORES VÁLIDOS----------------- ##
    df = df[df['radiacion'] > 0]
    df = df[(df['NI'] >= 0) & (df['strength'] >= 0)]
    ## --------------------ACOTANDO LOS DATOS POR CALIDAD-------------------- ##
    if 'calidad' in df.columns:
        df = df[df['calidad']<100]
    ## ---------------------AGRUPANDO LOS DATOS A HORAS---------------------- ##
    df_h = df.groupby(pd.Grouper(freq="H")).mean()
    df_h = df_h.between_time('06:00', '17:00')
    return df_h, df

df_P975_h, df_P975 = lectura_datos_piranometro(df_P975)
df_P350_h, df_P350 = lectura_datos_piranometro(df_P350)
df_P348_h, df_P348 = lectura_datos_piranometro(df_P348)

df_P975_h = df_P975_h[(df_P975_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (df_P975_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]

df_P350_h = df_P350_h[(df_P350_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (df_P350_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]

df_P348_h = df_P348_h[(df_P348_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (df_P348_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]

# ## ----------------LECTURA DE LOS DATOS DE LAS METEOROLÓGICAS---------------- ##
#
# data_T_Torre = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Meteorologicas/Entrega_TH_CuRad1019.txt',  sep=',')
# data_T_Conse = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Meteorologicas/Entrega_TH_CuRad206.txt',  sep=',')
# data_T_Joaqu = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Meteorologicas/Entrega_TH_CuRad367.txt',  sep=',')
#
# def lectura_datos_meteorologica_dia(df):
#     df.index = df['fecha_hora']
#     df = df.drop(['fecha_hora'], axis=1)
#     df.index = pd.to_datetime(df.index)
#     df = df.between_time('06:00', '18:00')
#     ## ---------ACOTANDO LOS DATOS POR CALIDAD Y VALORES VÁLIDOS------------- ##                     ##--> Seleccionar solo los datos de horas del dia
#     df = df[df[u'calidad'] < 100]
#     df = df[df['T'] > 0]
#     ## ---------------------AGRUPANDO LOS DATOS A HORAS---------------------- ##
#     df_h = df.groupby(pd.Grouper(freq="H")).mean()
#     df_h = df_h.between_time('06:00', '18:00')
#     return df_h, df
#
# data_T_Torre_h, data_T_Torre = lectura_datos_meteorologica_dia(data_T_Torre)
# data_T_Conse_h, data_T_Conse = lectura_datos_meteorologica_dia(data_T_Conse)
# data_T_Joaqu_h, data_T_Joaqu = lectura_datos_meteorologica_dia(data_T_Joaqu)
#
# data_T_Torre_h = data_T_Torre_h[(data_T_Torre_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
#             +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (data_T_Torre_h.index
#             <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]
#
# data_T_Conse_h = data_T_Conse_h[(data_T_Conse_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
#             +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (data_T_Conse_h.index
#             <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]
#
# data_T_Joaqu_h = data_T_Joaqu_h[(data_T_Joaqu_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
#             +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (data_T_Joaqu_h.index
#             <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]
#
# ## ----------------LECTURA DE LOS DATOS DEL RADIOMETRO---------------- ##
#
# data_Radi_WV = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/Integrated_VaporDensity_values.csv',  sep=',')
#
# def lectura_datos_radiometro(df):
#     df.index = df[u'Unnamed: 0']
#     df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
#     df = df.between_time('06:00', '17:00')                      ##--> Seleccionar solo los datos de horas del dia
#     ## ---------------------AGRUPANDO LOS DATOS A HORAS---------------------- ##
#     df_h = df[u'Integrate'].groupby(pd.Grouper(freq="H")).mean()
#     return df_h, df
#
# data_Radi_WV_h, data_Radi_WV =  lectura_datos_radiometro(data_Radi_WV)
# data_Radi_WV_h = data_Radi_WV_h[(data_Radi_WV_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
#             +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (data_Radi_WV_h.index
#             <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]

## ----------------LECTURA DE LOS DATOS DE GOES CH2---------------- ##
# path_GOES = '/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C2_2019_0320_0822.nc'
#
# def lectura_datos_GOES(path):
#     ds = Dataset(path)
#     lat = ds.variables['lat'][:, :]
#     lon = ds.variables['lon'][:, :]
#     Rad = ds.variables['Radiancias'][:, :, :]
#     return ds, lat, lon, Rad
#
# ds, lat, lon, Rad = lectura_datos_GOES(path_GOES)
#
#                    ## -- Selección del pixel de la TS
# lat_index_975 = np.where((lat[:, 0] > 6.25) & (lat[:, 0] < 6.26))[0][0]
# lon_index_975 = np.where((lon[0, :] < -75.58) & (lon[0, :] > -75.59))[0][0]
# Rad_pixel_975 = Rad[:, lat_index_975, lon_index_975]
#
#                    ## -- Selección del pixel de la CI
# lat_index_350 = np.where((lat[:, 0] > 6.16) & (lat[:, 0] < 6.17))[0][0]
# lon_index_350 = np.where((lon[0, :] < -75.64) & (lon[0, :] > -75.65))[0][0]
# Rad_pixel_350 = Rad[:, lat_index_350, lon_index_350]
#
#                    ## -- Selección del pixel de la JV
# lat_index_348 = np.where((lat[:, 0] > 6.25) & (lat[:, 0] < 6.26))[0][0]
# lon_index_348 = np.where((lon[0, :] < -75.54) & (lon[0, :] > -75.55))[0][0]
# Rad_pixel_348 = Rad[:, lat_index_348, lon_index_348]
#
#                    ## -- Obtener el tiempo para cada valor
#
# tiempo = ds.variables['time']
# fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
# for i in range(len(fechas_horas)):
#     fechas_horas[i] = fechas_horas[i].strftime('%Y-%m-%d %H:%M')
#
#                     ## -- Creación de dataframe de radiancias
# Rad_df_975 = pd.DataFrame()
# Rad_df_975['Fecha_Hora'] = fechas_horas
# Rad_df_975['Radiacias'] = Rad_pixel_975
# Rad_df_975['Fecha_Hora'] = pd.to_datetime(Rad_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
# Rad_df_975.index = Rad_df_975['Fecha_Hora']
# Rad_df_975 = Rad_df_975.drop(['Fecha_Hora'], axis=1)
# Rad_df_975 = Rad_df_975.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
# Rad_df_975_h = Rad_df_975.groupby(pd.Grouper(freq="H")).mean()
#
# Rad_df_350 = pd.DataFrame()
# Rad_df_350['Fecha_Hora'] = fechas_horas
# Rad_df_350['Radiacias'] = Rad_pixel_350
# Rad_df_350['Fecha_Hora'] = pd.to_datetime(Rad_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
# Rad_df_350.index = Rad_df_350['Fecha_Hora']
# Rad_df_350 = Rad_df_350.drop(['Fecha_Hora'], axis=1)
# Rad_df_350 = Rad_df_350.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
# Rad_df_350_h = Rad_df_350.groupby(pd.Grouper(freq="H")).mean()
#
# Rad_df_348 = pd.DataFrame()
# Rad_df_348['Fecha_Hora'] = fechas_horas
# Rad_df_348['Radiacias'] = Rad_pixel_348
# Rad_df_348['Fecha_Hora'] = pd.to_datetime(Rad_df_348['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
# Rad_df_348.index = Rad_df_348['Fecha_Hora']
# Rad_df_348 = Rad_df_348.drop(['Fecha_Hora'], axis=1)
# Rad_df_348 = Rad_df_348.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
# Rad_df_348_h = Rad_df_348.groupby(pd.Grouper(freq="H")).mean()
#
# if Anio_datosGOES == 2018:
#     Rad_df_975_h = Rad_df_975_h[(Rad_df_975_h.index >= pd.to_datetime('2018-'+str(fi_m)+ '-'+str(fi_d), format="%Y-%m-%d"
#                    , errors='coerce')) & (Rad_df_975_h.index <= pd.to_datetime('2018-'+str(ff_m)+ '-'+str(ff_d),
#                    format="%Y-%m-%d", errors='coerce') )]
#
#     Rad_df_350_h = Rad_df_350_h[(Rad_df_350_h.index >= pd.to_datetime('2018-'+str(fi_m)+ '-'+str(fi_d), format="%Y-%m-%d"
#                    , errors='coerce')) & (Rad_df_350_h.index <= pd.to_datetime('2018-'+str(ff_m)+ '-'+str(ff_d),
#                    format="%Y-%m-%d", errors='coerce') )]
#
#     Rad_df_348_h = Rad_df_348_h[(Rad_df_348_h.index >= pd.to_datetime('2018-'+str(fi_m)+ '-'+str(fi_d), format="%Y-%m-%d"
#                    , errors='coerce')) & (Rad_df_348_h.index <= pd.to_datetime('2018-'+str(ff_m)+ '-'+str(ff_d),
#                    format="%Y-%m-%d", errors='coerce') )]
# else:
#     pass

## ----------------LECTURA DE LOS DATOS RADIAION TEORICA---------------- ##

Puntos_medicion = ['6001', '6002', '6003']
df_rad_teo = pd.DataFrame()
Theoric_rad_method = 'GIS_Model'  ##-->> PARA QUE USE EL MODELO DE Gis DEBE SER 'GIS_Model'
resolucion = 'horaria'             ##-->> LAS OPCIONES SON 'diaria' U 'horaria'

for i in range(len(Puntos_medicion)):
    Estacion = Puntos_medicion[i]

    ## ---CALCULO DE LA RADIACIÓN TEORICA--- ##
    import datetime
    def daterange(start_date, end_date):
        'Para el ajuste de las fechas en el modelo de Kumar cada 10 min. Las fechas final e inicial son en str: %Y-%m-%d'

        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        delta = timedelta(minutes=10)
        while start_date <= end_date:
            yield start_date
            start_date += delta


    def serie_Kumar_Model_hora(estacion):
        'Retorna un dataframe horario con la radiacion teórico con las recomendacione de Kumar elaborado por Gisel Guzmán ' \
        'para el AMVA y su tesis. El dataframe original se le ordenan los datos a  12 meses ascendentes (2018), aunque pueden ' \
        ' pertencer  a  años difernetes. El resultado es para el punto seleccionado y con el archivo de Total_Timeseries.csv'

        data_Model = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_nati/Total_Timeseries.csv',
                                 sep=',')

        fecha_hora = [pd.to_datetime(data_Model['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S")[i].to_pydatetime() for i in
                      range(len(data_Model['Unnamed: 0']))]

        data_Model.index = fecha_hora

        data_Model = data_Model.sort_index()

        data_Model['Month'] = np.array(data_Model.index.month)

        data_Model = data_Model.sort_values(by="Month")

        fechas = []
        for i in daterange('2018-01-01', '2019-01-01'):
            fechas.append(i)
        fechas = fechas[0:-1]

        if estacion == '6001':
            punto = data_Model['TS_kumar']
        elif estacion == '6002':
            punto = data_Model['CI_kumar']
        elif estacion == '6003':
            punto = data_Model['JV_kumar']

        Rad_teorica = []
        for i in range(len(fechas)):
            mes = fechas[i].month
            hora = fechas[i].hour
            mint = fechas[i].minute
            rad = \
            np.where((data_Model.index.month == mes) & (data_Model.index.hour == hora) & (data_Model.index.minute == mint))[
                0]

            if len(rad) == 0:
                Rad_teorica.append(np.nan)
            else:
                Rad_teorica.append(punto.iloc[rad].values[0])

        data_Theorical = pd.DataFrame()
        data_Theorical['fecha_hora'] = fechas
        data_Theorical['Radiacion'] = Rad_teorica

        data_Theorical.index = data_Theorical['fecha_hora']

        df_hourly_theoric = data_Theorical.groupby(pd.Grouper(freq="H")).mean()

        df_hourly_theoric = df_hourly_theoric[df_hourly_theoric['Radiacion'] > 0]

        return df_hourly_theoric


    def Elevation_RadiationTA(n, lat, lon, start):
        'Para obtener la radiación en W/m2 y el ángulo de elevación del sol en grados horariamente para un número "n" de ' \
        'días aun punto en una latitud y longitud determinada ( "lat-lon"como flotantes) a partir de una fecha de inicio ' \
        '"start" como por ejemplo datetime.datetime(2018, 1, 1, 8).'
        import pysolar
        import pytz
        import datetime

        timezone = pytz.timezone("America/Bogota")
        start_aware = timezone.localize(start)

        # Calculate radiation every hour for 365 days
        nhr = 24*n
        dates, altitudes_deg, radiations = list(), list(), list()
        for ihr in range(nhr):
            date = start_aware + datetime.timedelta(hours=ihr)
            altitude_deg = pysolar.solar.get_altitude(lat, lon, date)
            if altitude_deg <= 0:
                radiation = 0.
            else:
                radiation = pysolar.radiation.get_radiation_direct(date, altitude_deg)
            dates.append(date)
            altitudes_deg.append(altitude_deg)
            radiations.append(radiation)

        days = [ihr/24 for ihr in range(nhr)]

        return days, altitudes_deg, radiations


    if Theoric_rad_method != 'GIS_Model' and Estacion == '6001':
        days, altitudes_deg, Io_hora = Elevation_RadiationTA(365, Latitudes[0], Longitudes[0], datetime.datetime(2018, 1, 1, 0))
        print('Teorica con pysolar')
    elif Theoric_rad_method != 'GIS_Model' and Estacion == '6002':
        days, altitudes_deg, Io_hora = Elevation_RadiationTA(365, Latitudes[1], Longitudes[1], datetime.datetime(2018, 1, 1, 0))
        print('Teorica con pysolar')
    elif Theoric_rad_method != 'GIS_Model' and Estacion == '6003':
        days, altitudes_deg, Io_hora = Elevation_RadiationTA(365, Latitudes[2], Longitudes[2], datetime.datetime(2018, 1, 1, 0))
        print('Teorica con pysolar')
    elif Theoric_rad_method == 'GIS_Model':
        Io_hora = serie_Kumar_Model_hora(Estacion)
        print('Teorica con el modelo de KUMAR')

    df_rad_teo = pd.concat([df_rad_teo, Io_hora], axis=1, sort=False)

## ----------AJUSTANDO LOS DATOS DEL DATAFRAME CAMBIANDO AÑO, ENCABEZADOS Y DENTRO DE LAS FECHAS NECESITADAS---------- ##
df_rad_teo.columns = Puntos_medicion
df_rad_teo.index = [df_rad_teo.index[i].replace(year=2019) for i in range(len(df_rad_teo.index))]
df_rad_teo = df_rad_teo[(df_rad_teo.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (df_rad_teo.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce'))]
###############################################################################################################
##-----------------------------------------------------------------------------------------------------------##
##--------------------------------------EFICIENCIA TEORICA---------------------------------------------------##
##-----------------------------------------------------------------------------------------------------------##
###############################################################################################################

df_Total_Efinciency_h = df_rad_teo
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P975_h['radiacion']], axis=1, sort=False)
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P350_h['radiacion']], axis=1, sort=False)
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P348_h['radiacion']], axis=1, sort=False)
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P975_h['strength']], axis=1, sort=False)
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P350_h['strength']], axis=1, sort=False)
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P348_h['strength']], axis=1, sort=False)

df_Total_Efinciency_h.columns = ['Rad_teo_975','Rad_teo_350', 'Rad_teo_348','Rad_real_975','Rad_real_350', 'Rad_real_348', 'Strength_975', 'Strength_350', 'Strength_348']

df_Total_Efinciency_h['Efi_teo_975'] = df_Total_Efinciency_h['Rad_real_975']/df_Total_Efinciency_h['Rad_teo_975']
df_Total_Efinciency_h['Efi_teo_350'] = df_Total_Efinciency_h['Rad_real_350']/df_Total_Efinciency_h['Rad_teo_350']
df_Total_Efinciency_h['Efi_teo_348'] = df_Total_Efinciency_h['Rad_real_348']/df_Total_Efinciency_h['Rad_teo_348']

df_Total_Efinciency_h['Efi_real_975'] = df_Total_Efinciency_h['Strength_975']/df_Total_Efinciency_h['Rad_real_975']
df_Total_Efinciency_h['Efi_real_350'] = df_Total_Efinciency_h['Strength_350']/df_Total_Efinciency_h['Rad_real_350']
df_Total_Efinciency_h['Efi_real_348'] = df_Total_Efinciency_h['Strength_348']/df_Total_Efinciency_h['Rad_real_348']

"Seleccionando las regiones donde la eficiencia teorica supera el 1.0 por posible desajuste del modelo. Estos son:"

df_excedencia_teorica_975 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_teo_975'] > 1]
df_excedencia_teorica_350 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_teo_350'] > 1]
df_excedencia_teorica_348 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_teo_348'] > 1]

df_excedencia_teorica_348.groupby(by=[df_excedencia_teorica_348.index.hour]).count()
df_excedencia_teorica_350.groupby(by=[df_excedencia_teorica_350.index.hour]).count()
df_excedencia_teorica_975.groupby(by=[df_excedencia_teorica_975.index.hour]).count()
df_excedencia_teorica_348.groupby(by=[df_excedencia_teorica_348.index.day]).count()

"Seleccionando las regiones donde la eficiencia real supera el 1.0 , sin embargo nos se encontraron casos en los que"
"esto pudiera suceder. Fue un ejercicio de verificación y con el objetivo de encontrar los rangos maximos de los datos"

df_excedencia_real_975 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_real_975'] > 1]
df_excedencia_real_350 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_real_350'] > 1]
df_excedencia_real_348 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_real_348'] > 1]

"Si se desean filtrar los valores en los que la eficiencia teorica supera el 1.5  se utuliza esta conversión:"
df_Total_Efinciency_h = df_Total_Efinciency_h[(df_Total_Efinciency_h ['Efi_teo_975'] <= 1.5) & (df_Total_Efinciency_h ['Efi_teo_350'] <= 1.5)&(df_Total_Efinciency_h ['Efi_teo_348'] <= 1.5)]

#
# "A continuació se pretende emplear los métodos que permitan discernir si hay una diferencia significativa entre las"
# "pendientes de cada uno de los ajustes."
#
# def best_fit(X, Y):
#
#     "Función para encontrar, la función que mejor se ajuste a un cojunto de datos de dos puntos, convierte en listas"
#     "los array iniciales. Se realiza por medio del método de mínimos cuadrados, que parte de encontrar la pendiente"
#     "-b- para luego encontrar el intercepto -a- y la linea de ajuste -yfit-."
#
#     X = list(X)
#     Y = list(Y)
#
#     xbar = np.nansum(X)/len(X)
#     ybar = np.nansum(Y)/len(Y)
#     n = len(X) # or len(Y)
#
#     numer = float(np.nansum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar)
#     denum = float(np.nansum([xi**2 for xi in X]) - n * xbar**2)
#
#     b = numer / denum
#     a = ybar - b * xbar
#     yfit = [a + b * xi for xi in X]
#
#     print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))
#
#     return a, b, yfit
#
# "Método de ANCOVA para estimar la significancia de las diferencias entre las pendientes http://www.biostathandbook.com/ancova.html"
#
# a_975, b_975, yfit_975 = best_fit(df_Total_Efinciency_h['Efi_teo_975'].values, df_Total_Efinciency_h['Efi_real_975'].values)
# a_350, b_350, yfit_350 = best_fit(df_Total_Efinciency_h['Efi_teo_350'].values, df_Total_Efinciency_h['Efi_real_350'].values)
# a_348, b_348, yfit_348 = best_fit(df_Total_Efinciency_h['Efi_teo_348'].values, df_Total_Efinciency_h['Efi_real_348'].values)

xm_975 = np.ma.masked_array(list(df_Total_Efinciency_h['Efi_teo_975'].values),mask=np.isnan(list(df_Total_Efinciency_h['Efi_teo_975'].values))).compressed()
ym_975 = np.ma.masked_array( list(df_Total_Efinciency_h['Efi_real_975'].values),mask=np.isnan( list(df_Total_Efinciency_h['Efi_real_975'].values))).compressed()
slope_975, intercept_975, r_value, p_value, std_err_975 = stats.linregress(xm_975, ym_975)
yfit_975 = [intercept_975 + slope_975 * xi for xi in xm_975]

xm_350 = np.ma.masked_array(list(df_Total_Efinciency_h['Efi_teo_350'].values),mask=np.isnan(list(df_Total_Efinciency_h['Efi_teo_350'].values))).compressed()
ym_350 = np.ma.masked_array( list(df_Total_Efinciency_h['Efi_real_350'].values),mask=np.isnan( list(df_Total_Efinciency_h['Efi_real_350'].values))).compressed()
slope_350, intercept_350, r_value, p_value, std_err_350 = stats.linregress(xm_350, ym_350)
yfit_350 = [intercept_350 + slope_350 * xi for xi in xm_350]

xm_348 = np.ma.masked_array(list(df_Total_Efinciency_h['Efi_teo_348'].values),mask=np.isnan(list(df_Total_Efinciency_h['Efi_teo_348'].values))).compressed()
ym_348 = np.ma.masked_array( list(df_Total_Efinciency_h['Efi_real_348'].values),mask=np.isnan( list(df_Total_Efinciency_h['Efi_real_348'].values))).compressed()
slope_348, intercept_348, r_value, p_value, std_err_348 = stats.linregress(xm_348, ym_348)
yfit_348 = [intercept_348 + slope_348 * xi for xi in xm_348]

z_975_350 = (slope_975 - slope_350)/((std_err_975)**2+(std_err_350)**2)**(0.5)
z_975_348 = (slope_975 - slope_348)/((std_err_975)**2+(std_err_348)**2)**(0.5)
z_348_350 = (slope_348 - slope_350)/((std_err_348)**2+(std_err_350)**2)**(0.5)

pval_975_350 =  2 * (1 - st.norm.cdf(z_975_350))
pval_975_348 =  2 * (1 - st.norm.cdf(z_975_348))
pval_348_350 =  2 * (1 - st.norm.cdf(z_348_350))


fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(df_excedencia_teorica_350.index.hour, bins='auto', alpha = 0.5)
ax1.set_title(u'Horas de excedencia de \n eficiencia teorica en JV', fontproperties=prop, fontsize = 8)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Horas', fontproperties=prop_1)

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(df_excedencia_teorica_350.index.hour, bins='auto', alpha = 0.5)
ax2.set_title(u'Horas de excedencia de \n eficiencia teorica en CI', fontproperties=prop, fontsize = 8)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Horas', fontproperties=prop_1)

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(df_excedencia_teorica_975.index.hour, bins='auto', alpha = 0.5)
ax3.set_title(u'Horas de excedencia de \n eficiencia teorica en TS', fontproperties=prop, fontsize = 8)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Horas', fontproperties=prop_1)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistoHorasEkxedenciaRad.png')
plt.show()


fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(xm_975, ym_975, s=80, c='#2980B9', label='P_TS', alpha=0.5, marker = ".")
ax1. plot(xm_975, yfit_975)
ax1.set_ylabel(u"Efi real", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Efi teorica", fontsize=14, fontproperties=prop_1)
ax1.set_ylim(0, np.nanmax(yfit_348)+0.01)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter(xm_350, ym_350, s=80, c='#2980B9', label='P_CI', alpha=0.5, marker = ".")
ax2. plot(xm_350, yfit_350)
ax2.set_ylabel(u"Efi real", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Efi teorica", fontsize=14, fontproperties=prop_1)
ax2.set_ylim(0, np.nanmax(yfit_350)+0.01)
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter(xm_348, ym_348, s=80, c='#2980B9', label='P_JV', alpha=0.5, marker = ".")
ax3. plot(xm_348, yfit_348)
ax3.set_ylabel(u"W", fontsize=14, fontproperties=prop_1)
ax3.set_ylabel(u"Efi real", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Efi teorica", fontsize=14, fontproperties=prop_1)
ax3.set_ylim(0, np.nanmax(yfit_348)+0.01)
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax3.legend()

plt.savefig('/home/nacorreasa/Escritorio/Figuras/ScatterEficienciaTeo.png')
plt.subplots_adjust( wspace=0.3, hspace=0.3)
plt.title(u'Relación eficiencias teorica y real', fontsize=13,  fontweight = "bold",  fontproperties = prop)
plt.show()


fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
plt. plot(xm_975, yfit_975, color = 'orange', label = 'TS')
plt. plot(xm_350, yfit_350, color = 'green', label = 'CI')
plt. plot(xm_348, yfit_348, color = 'red', label = 'JV')
plt.ylabel(u"Ajuste Efi real", fontsize=20, fontproperties=prop_1)
plt.xlabel(u"Efi teorica", fontsize=20, fontproperties=prop_1)
plt.ylim(0, np.nanmax(yfit_975)+0.01 )
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()
plt.title(u' Lineas de ajuste de la relación \n eficiencias teorica y real', fontsize=13,  fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/AjusteLineas.png')
plt.show()
