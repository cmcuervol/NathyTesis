#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

data_Liquid = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/Liquid-2019-03-20_2019-12-20.csv', sep=',')

data_Liquid.index = data_Liquid[u'Unnamed: 0'].values
data_Liquid = data_Liquid.drop([u'Unnamed: 0'], axis=1)

data_RelativeHumidity = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/RelativeHumidity-2019-03-20_2019-12-20.csv', sep=',')

data_RelativeHumidity.index = data_RelativeHumidity[u'Unnamed: 0'].values
data_RelativeHumidity = data_RelativeHumidity.drop([u'Unnamed: 0'], axis=1)

data_Temperature = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/Temperature-2019-03-20_2019-12-20.csv', sep=',')

data_Temperature.index = data_Temperature[u'Unnamed: 0'].values
data_Temperature = data_Temperature.drop([u'Unnamed: 0'], axis=1)

# data_VaporDensity = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/VaporDensity-2019-03-20_2019-12-20.csv', sep=',')
#
# data_VaporDensity.index = data_VaporDensity[u'Unnamed: 0'].values
# data_VaporDensity = data_VaporDensity.drop([u'Unnamed: 0'], axis=1)

data_VaporDensity = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/DatosNathy.csv', sep=',')
data_VaporDensity.index = data_VaporDensity[u'Unnamed: 0'].values
data_VaporDensity = data_VaporDensity.drop([u'Unnamed: 0'], axis=1)
# density = pd.read_npy('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/DatosNathy.npy')
# np.load('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/DatosNathy.npy').item()

## PARA INTEGRAR SOBRE LAS ALTURAS ##

x_Liquid = data_Liquid.columns.values.astype(float)

integrated_df_Liquid = []
for i in range(len(data_Liquid)):
    integrated_df_Liquid.append(np.trapz(data_Liquid.iloc[i].values, x_Liquid))

data_Liquid['Integrate'] = integrated_df_Liquid
data_Liquid.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/Integrated_Liquid_values.csv')

x_RelativeHumidity = data_RelativeHumidity.columns.values.astype(float)

integrated_df_RelativeHumidity = []
for i in range(len(data_RelativeHumidity)):
    integrated_df_RelativeHumidity.append(np.trapz(data_RelativeHumidity.iloc[i].values, x_RelativeHumidity))

data_RelativeHumidity['Integrate'] = integrated_df_RelativeHumidity
data_RelativeHumidity.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/Integrated_RelativeHumidity_values.csv')

x_Temperature = data_Temperature.columns.values.astype(float)

integrated_df_Temperature = []
for i in range(len(data_Temperature)):
    integrated_df_Temperature.append(np.trapz(data_Temperature.iloc[i].values, x_Temperature))

data_Temperature['Integrate'] = integrated_df_Temperature
data_Temperature.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/Integrated_Temperature_values.csv')

x_VaporDensity = data_VaporDensity.columns.values.astype(float)

integrated_df_VaporDensity = []
for i in range(len(data_VaporDensity)):
    integrated_df_VaporDensity.append(np.trapz(data_VaporDensity.iloc[i].values, x_VaporDensity))

data_VaporDensity['Integrate'] = integrated_df_VaporDensity
data_VaporDensity.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/Integrated_VaporDensity_values.csv')
