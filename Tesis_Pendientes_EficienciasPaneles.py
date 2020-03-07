#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.font_manager as fm
import math as m
import matplotlib.dates as mdates
import netCDF4 as nc
from netCDF4 import Dataset
id
import itertools
import datetime
from scipy.stats import ks_2samp
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
import matplotlib.cm as cm
import os
import statistics
from pysolar.solar import *
from scipy.stats import pearsonr
from scipy import stats
import scipy.stats as st
import scipy.special as sp

"Programa desarrollado para el análisis de la eficiencia de los paneles en los 3 puntos de medición"
"durante sus periodos de registro. Tiene 2 opciones para la estimación de la radiación teorica, de "
"las cuales, la de PYS aun le falta cuadrar lo de las fechas. Se realizará acá el análisis de pendi"
"entes."

################################################################################
## ----------ACOTANDO LAS FECHAS POR DIA Y MES PARA TOMAR LOS DATOS---------- ##
################################################################################

fi_m = 3
fi_d = 23
ff_m = 12
ff_d = 20
Anio_datosGOES = 2019
Latitudes = [6.259, 6.168, 6.255]        ## En orden: 6001, 6002, 6003
Longitudes = [-75.588, -75.644, -75.542] ## En orden: 6001, 6002, 6003
Puntos_medicion = ['6001', '6002', '6003']
Theoric_Model = 'GIS'               ##---> 'GIS' para que coja el de Gis o 'Piranometro' para que tome el de el piranometro
resolucion = 'horaria'                   ##-->> Las opciones son 'diaria' U 'horaria', principamente si se va a hacer con el moedelo de Gis.

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

## ----------------CARACTERISTICAS DEL PANEL---------------- ##

Voc = 22.68    ## --> En V
Isc = 8.62     ## --> En A
Area_TS = 0.66    ## --> En m2
Area_Laderas = 0.60    ## --> En m2

##############################################################################
## ----------------LECTURA DE LOS DATOS DE LOS EXPERIMENTOS---------------- ##
##############################################################################

df_P975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel975.txt',  sep=',', index_col =0)
df_P350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel350.txt',  sep=',', index_col =0)
df_P348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel348.txt',  sep=',', index_col =0)

def lectura_datos_piranometro(df):
    df['Fecha_hora'] = df.index
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
    ## -----------------ACOTANDO LOS DATOS A VALORES VÁLIDOS----------------- ##
    df = df[df['radiacion'] > 0]
    df = df[(df['NI'] >= 0) & (df['strength'] >= 0)& (df['strength'] <= 100)]
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

df_P975_h = df_P975_h[(df_P975_h.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-' +str(fi_d)).date()) & (df_P975_h.index.date <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

df_P350_h = df_P350_h[(df_P350_h.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-' +str(fi_d)).date()) & (df_P350_h.index.date <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

df_P348_h = df_P348_h[(df_P348_h.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-' +str(fi_d)).date()) & (df_P348_h.index.date <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

###############################################################################
## ------------------LECTURA DE LOS DATOS RADIAION TEORICA------------------ ##
###############################################################################
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

df_rad_teo = df_Theoric

#########################################################################################################################
## ----------AJUSTANDO LOS DATOS DEL DATAFRAME CAMBIANDO AÑO, ENCABEZADOS Y DENTRO DE LAS FECHAS NECESITADAS---------- ##
#########################################################################################################################

df_rad_teo.columns = Puntos_medicion
df_rad_teo.index = [df_rad_teo.index[i].replace(year=2019) for i in range(len(df_rad_teo.index))]
df_rad_teo = df_rad_teo[(df_rad_teo.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-'+str(fi_d)).date()) & (df_rad_teo.index.date  <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

###############################################################################################################
##-----------------------------------------------------------------------------------------------------------##
##--------------------------------------EFICIENCIA TEORICA---------------------------------------------------##
##-----------------------------------------------------------------------------------------------------------##
###############################################################################################################

df_Total_Efinciency_h = df_rad_teo
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P975_h['radiacion']], axis=1)
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P350_h['radiacion']], axis=1)
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P348_h['radiacion']], axis=1)
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P975_h['strength']], axis=1)
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P350_h['strength']], axis=1)
df_Total_Efinciency_h = pd.concat([df_Total_Efinciency_h, df_P348_h['strength']], axis=1)

df_Total_Efinciency_h.columns = ['Rad_teo_975','Rad_teo_350', 'Rad_teo_348','Rad_real_975','Rad_real_350', 'Rad_real_348', 'Strength_975', 'Strength_350', 'Strength_348']

df_Total_Efinciency_h['Efi_teo_975'] = df_Total_Efinciency_h['Rad_real_975']/df_Total_Efinciency_h['Rad_teo_975']
df_Total_Efinciency_h['Efi_teo_350'] = df_Total_Efinciency_h['Rad_real_350']/df_Total_Efinciency_h['Rad_teo_350']
df_Total_Efinciency_h['Efi_teo_348'] = df_Total_Efinciency_h['Rad_real_348']/df_Total_Efinciency_h['Rad_teo_348']

"Para entregarlo en watios sobre metro cuadrado"

df_Total_Efinciency_h['Strength_975_Area'] = df_Total_Efinciency_h['Strength_975']/Area_TS
df_Total_Efinciency_h['Strength_350_Area'] = df_Total_Efinciency_h['Strength_350']/Area_Laderas
df_Total_Efinciency_h['Strength_348_Area'] = df_Total_Efinciency_h['Strength_348']/Area_Laderas

df_Total_Efinciency_h['Efi_real_975'] = df_Total_Efinciency_h['Strength_975_Area']/df_Total_Efinciency_h['Rad_real_975']
df_Total_Efinciency_h['Efi_real_350'] = df_Total_Efinciency_h['Strength_350_Area']/df_Total_Efinciency_h['Rad_real_350']
df_Total_Efinciency_h['Efi_real_348'] = df_Total_Efinciency_h['Strength_348_Area']/df_Total_Efinciency_h['Rad_real_348']

"Seleccionando las regiones donde la eficiencia teorica supera el 1.0 por posible desajuste del modelo. Estos son:"

df_excedencia_teorica_975 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_teo_975'] > 1]
df_excedencia_teorica_350 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_teo_350'] > 1]
df_excedencia_teorica_348 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_teo_348'] > 1]

"Seleccionando las regiones donde la eficiencia real supera el 1.0 , sin embargo nos se encontraron casos en los que"
"esto pudiera suceder. Fue un ejercicio de verificación y con el objetivo de encontrar los rangos maximos de los datos"

df_excedencia_real_975 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_real_975'] > 1]
df_excedencia_real_350 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_real_350'] > 1]
df_excedencia_real_348 = df_Total_Efinciency_h[df_Total_Efinciency_h ['Efi_real_348'] > 1]

################################################################################
## -----------------------------LIMPIEZA DE LOS DATOS------------------------ ##
################################################################################

"Se descartan los valores menores al 0.001 para mejorar las pendientes:"
df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_teo_975'] >= 0.001)]
df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_teo_350'] >= 0.001)]
df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_teo_348'] >= 0.001)]

df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_real_975'] >= 0.001)]
df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_real_350'] >= 0.001)]
df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_real_348'] >= 0.001)]

"Se descartan los valores de eficiencia real teorica mayores a 1"
df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_real_975'] <= 1)]
df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_real_348'] <= 1)]
df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_real_350'] <= 1)]

df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_teo_975'] <= 1)]
df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_teo_350'] <= 1)]
df_Total_Efinciency_h = df_Total_Efinciency_h.loc[(df_Total_Efinciency_h ['Efi_teo_348'] <= 1)]

"Limpieza adicional para mejorar la pendiente en TS, cuando es significativa ya se deberia reemplantear"
"Es decir que en unos pocos momentos el panel alcanza una efciencia mayor al 10 %"

df_Total_Efinciency_h = df_Total_Efinciency_h.loc[df_Total_Efinciency_h['Efi_real_975'] <= 0.100]
print('Cant. Horas que superan el 10 %: '+ str(len(df_Total_Efinciency_h[df_Total_Efinciency_h['Efi_real_975']>0.100])))

################################################################################
## --------------------------CALCULO DE LA PENDIENTE------------------------- ##
################################################################################

xm_975 = np.ma.masked_array(list(df_Total_Efinciency_h['Efi_teo_975'].values),mask=np.isnan(list(df_Total_Efinciency_h['Efi_teo_975'].values))).compressed()
ym_975 = np.ma.masked_array( list(df_Total_Efinciency_h['Efi_real_975'].values),mask=np.isnan( list(df_Total_Efinciency_h['Efi_real_975'].values))).compressed()
xm_975 =xm_975[np.where(ym_975<0.22)]
ym_975 = ym_975[ym_975<0.22]

slope_975, intercept_975, r_value, p_value, std_err_975 = stats.linregress(xm_975, ym_975)
yfit_975 = [intercept_975 + slope_975 * xi for xi in xm_975]
y_fake_975 = ym_975
x_fake_975 = xm_975

xm_350 = np.ma.masked_array(list(df_Total_Efinciency_h['Efi_teo_350'].values),mask=np.isnan(list(df_Total_Efinciency_h['Efi_teo_350'].values))).compressed()
ym_350 = np.ma.masked_array( list(df_Total_Efinciency_h['Efi_real_350'].values),mask=np.isnan( list(df_Total_Efinciency_h['Efi_real_350'].values))).compressed()
xm_350 =xm_350[np.where(ym_350<0.22)]
ym_350 = ym_350[ym_350<0.22]

slope_350, intercept_350, r_value, p_value, std_err_350 = stats.linregress(xm_350, ym_350)
yfit_350 = [intercept_350 + slope_350 * xi for xi in xm_350]
y_fake_350 = ym_350
x_fake_350 = xm_350

xm_348 = np.ma.masked_array(list(df_Total_Efinciency_h['Efi_teo_348'].values),mask=np.isnan(list(df_Total_Efinciency_h['Efi_teo_348'].values))).compressed()
ym_348 = np.ma.masked_array( list(df_Total_Efinciency_h['Efi_real_348'].values),mask=np.isnan( list(df_Total_Efinciency_h['Efi_real_348'].values))).compressed()
xm_348 =xm_348[np.where(ym_348<0.22)]
ym_348 =ym_348[ym_348<0.22]

slope_348, intercept_348, r_value, p_value, std_err_348 = stats.linregress(xm_348, ym_348)
yfit_348 = [intercept_348 + slope_348 * xi for xi in xm_348]
y_fake_348 = ym_348
x_fake_348 = xm_348

print('Pendiente TS: ' + str(slope_975))
print('Pendiente CI: ' + str(slope_350))
print('Pendiente JV: ' + str(slope_348))

################################################################################
## ----------------------DIFERENCIA ENTRE PENDIENTES------------------------- ##
################################################################################

z_975_350 = (slope_975 - slope_350)/((std_err_975)**2+(std_err_350)**2)**(0.5)
z_975_348 = (slope_975 - slope_348)/((std_err_975)**2+(std_err_348)**2)**(0.5)
z_348_350 = (slope_348 - slope_350)/((std_err_348)**2+(std_err_350)**2)**(0.5)

pval_975_350 =  2 * (1 - st.norm.cdf(z_975_350))
pval_975_348 =  2 * (1 - st.norm.cdf(z_975_348))
pval_348_350 =  2 * (1 - st.norm.cdf(z_348_350))

#####################################################################################
## ----------------------AJUSTE POR INTERVALOS Y MEDIANAS------------------------- ##
#####################################################################################
size = 101
xm_348.sort()
ym_348.sort()
median_xmsort_348 = []
median_ymsort_348 = []
for i in range(0, len(xm_348), size):
    print(i)
    median_xmsort_348.append(np.median(xm_348[i:i+size]))
    median_ymsort_348.append(np.median(ym_348[i:i+size]))

xm_350.sort()
ym_350.sort()
median_xmsort_350 = []
median_ymsort_350 = []
for i in range(0, len(xm_350), size):
    print(i)
    median_xmsort_350.append(np.median(xm_350[i:i+size]))
    median_ymsort_350.append(np.median(ym_350[i:i+size]))

xm_975.sort()
ym_975.sort()
median_xmsort_975 = []
median_ymsort_975 = []
for i in range(0, len(xm_975), size):
    print(i)
    median_xmsort_975.append(np.median(xm_975[i:i+size]))
    median_ymsort_975.append(np.median(ym_975[i:i+size]))

slope_median_348, intercept_median_348, r_median348_value, p_median348_value, std_err_median_348 = stats.linregress(median_xmsort_348 , median_ymsort_348 )
yfit_median_348 = [intercept_median_348 + slope_median_348 * xi for xi in median_xmsort_348 ]

slope_median_350, intercept_median_350, r_median350_value, p_median350_value, std_err_median_350 = stats.linregress(median_xmsort_350 , median_ymsort_350 )
yfit_median_350 = [intercept_median_350 + slope_median_350 * xi for xi in median_xmsort_350 ]

slope_median_975, intercept_median_975, r_median975_value, p_median975_value, std_err_median_975 = stats.linregress(median_xmsort_975 , median_ymsort_975 )
yfit_median_975 = [intercept_median_975 + slope_median_975 * xi for xi in median_xmsort_975 ]

##----------------------------------------------VOLVIENDO A CALCULAR EL AJUSTE INICIAL BAJO OTRO NOMBRE-------------------------------------##

x_fake_975 = np.ma.masked_array(list(df_Total_Efinciency_h['Efi_teo_975'].values),mask=np.isnan(list(df_Total_Efinciency_h['Efi_teo_975'].values))).compressed()
y_fake_975 = np.ma.masked_array( list(df_Total_Efinciency_h['Efi_real_975'].values),mask=np.isnan( list(df_Total_Efinciency_h['Efi_real_975'].values))).compressed()
x_fake_350 = np.ma.masked_array(list(df_Total_Efinciency_h['Efi_teo_350'].values),mask=np.isnan(list(df_Total_Efinciency_h['Efi_teo_350'].values))).compressed()
y_fake_350 = np.ma.masked_array( list(df_Total_Efinciency_h['Efi_real_350'].values),mask=np.isnan( list(df_Total_Efinciency_h['Efi_real_350'].values))).compressed()
x_fake_348 = np.ma.masked_array(list(df_Total_Efinciency_h['Efi_teo_348'].values),mask=np.isnan(list(df_Total_Efinciency_h['Efi_teo_348'].values))).compressed()
y_fake_348 = np.ma.masked_array( list(df_Total_Efinciency_h['Efi_real_348'].values),mask=np.isnan( list(df_Total_Efinciency_h['Efi_real_348'].values))).compressed()


#####################################################################################
## ------------------------------AJUSTE POR QQ PLOT------------------------------- ##
#####################################################################################


def qqplot(x, y, quantiles=None, interpolation='nearest', ax=None, rug=False,
           rug_length=0.05, rug_kwargs=None, **kwargs):
    """Draw a quantile-quantile plot for `x` versus `y`.

    Parameters
    ----------
    x, y : array-like
        One-dimensional numeric arrays.

    ax : matplotlib.axes.Axes, optional
        Axes on which to plot. If not provided, the current axes will be used.

    quantiles : int or array-like, optional
        Quantiles to include in the plot. This can be an array of quantiles, in
        which case only the specified quantiles of `x` and `y` will be plotted.
        If this is an int `n`, then the quantiles will be `n` evenly spaced
        points between 0 and 1. If this is None, then `min(len(x), len(y))`
        evenly spaced quantiles between 0 and 1 will be computed.

    interpolation : {‘linear’, ‘lower’, ‘higher’, ‘midpoint’, ‘nearest’}
        Specify the interpolation method used to find quantiles when `quantiles`
        is an int or None. See the documentation for numpy.quantile().

    rug : bool, optional
        If True, draw a rug plot representing both samples on the horizontal and
        vertical axes. If False, no rug plot is drawn.

    rug_length : float in [0, 1], optional
        Specifies the length of the rug plot lines as a fraction of the total
        vertical or horizontal length.

    rug_kwargs : dict of keyword arguments
        Keyword arguments to pass to matplotlib.axes.Axes.axvline() and
        matplotlib.axes.Axes.axhline() when drawing rug plots.

    kwargs : dict of keyword arguments
        Keyword arguments to pass to matplotlib.axes.Axes.scatter() when drawing
        the q-q plot.
    """
    # Get current axes if none are provided
    if ax is None:
        ax = plt.gca()

    if quantiles is None:
        quantiles = min(len(x), len(y))

    # Compute quantiles of the two samples
    if isinstance(quantiles, numbers.Integral):
        quantiles = np.linspace(start=0, stop=1, num=int(quantiles))
    else:
        quantiles = np.atleast_1d(np.sort(quantiles))
    x_quantiles = np.quantile(x, quantiles, interpolation=interpolation)
    y_quantiles = np.quantile(y, quantiles, interpolation=interpolation)

    # Draw the rug plots if requested
    if rug:
        # Default rug plot settings
        rug_x_params = dict(ymin=0, ymax=rug_length, c='gray', alpha=0.5)
        rug_y_params = dict(xmin=0, xmax=rug_length, c='gray', alpha=0.5)

        # Override default setting by any user-specified settings
        if rug_kwargs is not None:
            rug_x_params.update(rug_kwargs)
            rug_y_params.update(rug_kwargs)

        # Draw the rug plots
        for point in x:
            ax.axvline(point, **rug_x_params)
        for point in y:
            ax.axhline(point, **rug_y_params)

    # Draw the q-q plot
    ax.scatter(x_quantiles, y_quantiles, **kwargs)

################################################################################
## --------------------------------GRAFICAS---------------------------------- ##
################################################################################

x_lebels = ['0', '0.2', '0.4', '0.6', '0.8', '1']
fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(x_fake_350, y_fake_350, s=50, c='#70AFBA', alpha=0.5, marker = ".")
ax1.scatter(median_xmsort_350, median_ymsort_350, s=80, c='#004D56', label='Median interval',  marker = "o")
ax1. plot(median_xmsort_350, yfit_median_350,  color='#09202E', linewidth = 1.1, label = 'Adjustment line' )
ax1.text(0.01, 0.107, r'Slope: ' + str(slope_median_350.round(3))  , fontsize=10, fontproperties=prop_1)
ax1.set_ylabel(u"Eficiencia Real", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Índice de cielo despejado $Kt*$", fontsize=12, fontproperties=prop_1)
ax1.set_title(u'Relacion en el Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.set_xticks(np.arange(0,1.2, 0.2), minor=False)
ax1.set_xticklabels(np.array(x_lebels), minor=False, rotation = 20)
ax1.set_ylim(0, 0.12)
ax1.set_xlim(0, 1)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter(x_fake_975, y_fake_975, s=50, c='#70AFBA',  alpha=0.5, marker = ".")
ax2.scatter(median_xmsort_975, median_ymsort_975, s=80, c='#004D56', label='Median interval',  marker = "o")
ax2. plot(median_xmsort_975, yfit_median_975,  color='#09202E', linewidth = 1.1 , label = 'Adjustment line')
ax2.text(0.01, 0.107, r'Slope: ' + str(slope_median_975.round(3))  , fontsize=10, fontproperties=prop_1)
ax2.set_ylabel(u"Eficiencia Real", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Índice de cielo despejado $Kt*$", fontsize=12, fontproperties=prop_1)
ax2.set_title(u'Relacion en el Centro-Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax2.set_xticks(np.arange(0,1.2, 0.2), minor=False)
ax2.set_xticklabels(np.array(x_lebels), minor=False, rotation = 20)
ax2.set_ylim(0, 0.12)
ax2.set_xlim(0, 1)
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter(x_fake_348 , y_fake_348, s=50, c='#70AFBA',  alpha=0.5, marker = ".")
ax3.scatter(median_xmsort_348, median_ymsort_348, s=80, c='#004D56', label='Median interval',  marker = "o")
ax3. plot(median_xmsort_348, yfit_median_348,  color='#09202E', linewidth = 1.1, label = 'Adjustment line' )
ax3.text(0.01, 0.107, r'Slope: ' + str(slope_median_348.round(3))  , fontsize=10, fontproperties=prop_1)
ax3.set_ylabel(u"Eficiencia Real", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Índice de cielo despejado $Kt*$", fontsize=12, fontproperties=prop_1)
ax3.set_title(u'Relacion en el Este' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax3.set_xticks(np.arange(0,1.2, 0.2), minor=False)
ax3.set_xticklabels(np.array(x_lebels), minor=False, rotation = 20)
ax3.set_ylim(0, 0.12)
ax3.set_xlim(0, 1)
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax3.legend()

plt.subplots_adjust( wspace=0.4, hspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/ScatterEficienciaTeo' + Theoric_Model +'.pdf',  format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/ScatterEficienciaTeo' + Theoric_Model +'.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##---------------------------------------------------------------------------------------------------##

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(xm_350, ym_350, s=80, c='#004D56',  marker = "o")
ax1.plot( [0,1],[0,1], linestyle=':', linewidth=0.5, alpha=0.7 )
ax1.set_ylabel(u"Real efficiency", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Clear sky index $Kt*$", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'QQ Relationship in West point' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.set_xticks(np.arange(0,1.2, 0.2), minor=False)
ax1.set_xticklabels(np.arange(0, 1.2, 0.2), minor=False, rotation = 20)
ax1.set_ylim(0, 0.12)
ax1.set_xlim(0, 1)
#ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter(xm_975, ym_975, s=80, c='#004D56',  marker = "o")
ax2.plot( [0,1],[0,1], linestyle=':', linewidth=0.5, alpha=0.7 )
ax2.set_ylabel(u"Real efficiency", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Clear sky index $Kt*$", fontsize=14, fontproperties=prop_1)
ax2.set_title(u'QQ Relationship in West Center point' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax2.set_xticks(np.arange(0,1.2, 0.2), minor=False)
ax2.set_xticklabels(np.arange(0, 1.2, 0.2), minor=False, rotation = 20)
ax2.set_ylim(0, 0.12)
ax2.set_xlim(0, 1)
#ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter(xm_348, ym_348, s=80, c='#004D56',  marker = "o")
ax3.plot( [0,1],[0,1], linestyle=':', linewidth=0.5, alpha=0.7 )
ax3.set_ylabel(u"Real efficiency", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Clear sky index $Kt*$", fontsize=14, fontproperties=prop_1)
ax3.set_title(u'QQ Relationship in East point' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax3.set_xticks(np.arange(0,1.2, 0.2), minor=False)
ax3.set_xticklabels(np.arange(0, 1.2, 0.2), minor=False, rotation = 20)
ax3.set_ylim(0, 0.12)
ax3.set_xlim(0, 1)
#ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax3.legend()

plt.subplots_adjust( wspace=0.4, hspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/ScatterEficienciaQQPlot' + Theoric_Model +'.pdf',  format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/ScatterEficienciaQQPlot' + Theoric_Model +'.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


######################################################################################
## --------------------------CALCULO DEL PERFORMANCE RATIO------------------------- ##
######################################################################################
Pot_Instal_TS = 80
Pot_Instal_JVCI = 100

df_Total_Efinciency_h_Month = df_Total_Efinciency_h.groupby(pd.Grouper(freq="m")).mean()

suma_Total_Efinciency_h_Month = df_Total_Efinciency_h_Month.sum(axis = 0, skipna = True)

Yf_348 = suma_Total_Efinciency_h_Month['Strength_348']/Pot_Instal_JVCI
Yf_350 = suma_Total_Efinciency_h_Month['Strength_350']/Pot_Instal_JVCI
Yf_975 = suma_Total_Efinciency_h_Month['Strength_975']/Pot_Instal_TS

Yr_348 = suma_Total_Efinciency_h_Month['Rad_real_348']/1000
Yr_350 = suma_Total_Efinciency_h_Month['Rad_real_350']/1000
Yr_975 = suma_Total_Efinciency_h_Month['Rad_real_975']/1000

PR_348 = Yf_348/Yr_348
PR_350 = Yf_350/Yr_350
PR_975 = Yf_975/Yr_975
