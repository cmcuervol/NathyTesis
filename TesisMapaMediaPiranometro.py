#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gdal
import matplotlib
matplotlib.use('Agg')
# %matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import basemap

Path = '/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/'
Path_DEM = '/home/nacorreasa/Maestria/Datos_Tesis/DEMs/'
Path_Shape = '/home/nacorreasa/Maestria/Semestre1/Analisis_Geoespacial/MuchosShapes/AMVA/'
Path_Save = '/home/nacorreasa/Maestria/Semestre2/Semeniario_2/'


CA = np.genfromtxt(Path+'CA_entre2018-09-30&2018-09-30.txt', skip_header=1, dtype=float)

Lat75 = CA[:, 0]
Lon75 = CA[:, 1]

CA = CA[:, 2:]

def MapaBolas(data, name, Lat, Lon, titulo, cmap):
    t = [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    mes = ['Dic', 'Ene', 'Feb', 'Mar', 'Abr', 'May','Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov']

    if np.max(data[:, :]) > 300:
        factor = 0.5
    elif np.max(data[:, :]) > 100 and np.max(data[:, :]) < 300:
        factor = 1.5
    elif np.max(data[:, :]) < 100:
        factor = 5

    DataSet = gdal.Open(Path_DEM + 'DEM30mAMVAclip.tif')
    GeoTransform = DataSet.GetGeoTransform()
    xOrigin = GeoTransform[0]
    yOrigin = GeoTransform[3]
    pixelWidth = GeoTransform[1]
    pixelHeight = GeoTransform[5]
    longitudes=np.array([GeoTransform[0]+0.5*GeoTransform[1]+i*GeoTransform[1] for i in range(DataSet.RasterXSize)])
    latitudes=np.array([GeoTransform[3]+0.5*GeoTransform[-1]+i*GeoTransform[-1] for i in range(DataSet.RasterYSize)])
    DEM=DataSet.ReadAsArray()
    DEM=DEM.astype(float)
    DEM[DEM==65535]= np.nan
    DEM[DEM == 0] = np.nan
    X,Y= np.meshgrid(longitudes,latitudes)

    plt.close('all')
    fig = plt.figure(figsize=(14,18))

    for i in range(0, 12):
        ax = fig.add_subplot(4, 3, i+1)
        ax.set_title(mes[i], fontsize=14)

        m=basemap.Basemap(llcrnrlat=np.min(latitudes),llcrnrlon=np.min(longitudes),urcrnrlat=np.max(latitudes),urcrnrlon=np.max(longitudes),resolution='c')
        r=m.readshapefile(shapefile=Path_Shape +'AreaMetropolitana',name='AreaMetropolitana',color='k', linewidth=1.5)
        Xm,Ym= m(X,Y)
        # cs=m.contourf(Xm,Ym,DEM,levels=np.linspace(1300,3401,101),cmap='Greys')
        cs=m.contourf(Xm, Ym, DEM, levels=np.linspace(0, 3501, 101), cmap='terrain')

        parallels = np.arange(np.min(latitudes).round(1), np.max(latitudes).round(1)+0.25, 0.25)
        m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=8, linewidth=0.1)
        # draw meridians
        meridians = np.arange(np.min(longitudes).round(1)+360, np.max(longitudes).round(1)+360+0.5, 0.5)
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=8, linewidth=0.1)

        # m.scatter(Lon, Lat, s=(data[:, t[i]])*factor, marker="o",alpha=0.7, c='k')

        sc = m.scatter(Lon, Lat, c=(data[:, t[i]])*factor, cmap=cmap,  marker="o",alpha=0.7, s=80)

        #sc = m.scatter(Lon, Lat, s=(data[:, t[i]])*0.8, marker="o",alpha=0.7, cmap ='gray')
        # plt.savefig(Path+'CA.png',dpi=300,bbox_inches='tight')


    plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.15, hspace=0.08)

    cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
    cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f" )
    cbar.set_label(u'Elevación m.s.n.m.')

    cbar2_ax = fig.add_axes([0.125, 0.99, 0.78, 0.015])
    cbar = fig.colorbar(sc, cax=cbar2_ax, orientation='horizontal', format="%.2f")

    cbar.set_label(titulo, fontsize=14)
    cbar.outline.set_edgecolor('gray')

    # bolas_ax = fig.add_axes([0.125, 0.99, 0.78, 0.015])
    # bolas_ax.axis('off')
    # bolas = np.percentile((data[:, t[i]])*factor, [0, 25, 50, 75, 100])
    # for area in bolas:
    #     plt.scatter([], [], c='k', alpha=0.7, s=area,
    #                 label=str(int(area)) + ' Percentil rad.Prom')
    # plt.legend(scatterpoints=1, frameon=False, labelspacing=1, title=r"Promedio de la radicion  $[W/m^{2}]$", loc = 'upper center', ncol=len(bolas))


    plt.savefig(Path_Save+name+'.png', format='png')
    # plt.show()


def MapaBolasTrimestre(data, name, Lat, Lon, titulo, cmap, trimestre):
    t = [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    mes = trimestre

    if np.max(data[:, :]) > 300:
        factor = 0.5
    elif np.max(data[:, :]) > 100 and np.max(data[:, :]) < 300:
        factor = 1.5
    elif np.max(data[:, :]) < 100:
        factor = 5

    DataSet = gdal.Open(Path_DEM + 'DEM30mAMVAclip.tif')
    GeoTransform = DataSet.GetGeoTransform()
    xOrigin = GeoTransform[0]
    yOrigin = GeoTransform[3]
    pixelWidth = GeoTransform[1]
    pixelHeight = GeoTransform[5]
    longitudes = np.array([GeoTransform[0]+0.5*GeoTransform[1]+i*GeoTransform[1] for i in range(DataSet.RasterXSize)])
    latitudes = np.array([GeoTransform[3]+0.5*GeoTransform[-1]+i*GeoTransform[-1] for i in range(DataSet.RasterYSize)])
    DEM=DataSet.ReadAsArray()
    DEM=DEM.astype(float)
    DEM[DEM == 65535] = np.nan
    DEM[DEM == 0] = np.nan
    X, Y = np.meshgrid(longitudes, latitudes)

    plt.close('all')
    fig = plt.figure(figsize=(10, 8))

    for i in range(0, 3):
        ax = fig.add_subplot(1, 3, i+1)
        ax.set_title(mes[i], fontsize=14)

        m = basemap.Basemap(llcrnrlat=np.min(latitudes),llcrnrlon=np.min(longitudes),urcrnrlat=np.max(latitudes), urcrnrlon=np.max(longitudes), resolution='c')
        r = m.readshapefile(shapefile=Path_Shape +'AreaMetropolitana',name='AreaMetropolitana',color='k', linewidth=1.5)
        Xm,Ym = m(X, Y)

        cs = m.contourf(Xm, Ym, DEM, levels=np.linspace(0, 3501, 101), cmap='terrain')

        parallels = np.arange(np.min(latitudes).round(1), np.max(latitudes).round(1)+0.25, 0.25)
        m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=8, linewidth=0.1)

        meridians = np.arange(np.min(longitudes).round(1)+360, np.max(longitudes).round(1)+360+0.5, 0.5)
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=8, linewidth=0.1)

        sc = m.scatter(Lon, Lat, c=(data[:, t[i]])*factor, cmap=cmap,  marker="o", alpha=0.7, s=80)

    plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.19, hspace=0.08)

    cbar_ax = fig.add_axes([0.125, 0.30, 0.78, 0.015])
    cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f" )
    cbar.set_label(u'Elevación m.s.n.m.')

    cbar2_ax = fig.add_axes([0.125, 0.80, 0.78, 0.015])
    cbar = fig.colorbar(sc, cax=cbar2_ax, orientation='horizontal', format="%.2f")

    cbar.set_label(titulo, fontsize=14)
    cbar.outline.set_edgecolor('gray')

    plt.savefig(Path_Save+name+'.png', format='png')

##EJECUTAR LAS FUNCIONES##

#MapaBolas(CA, 'CA_1', Lat75, Lon75, r"Promedio de la radicion  $[W/m^{2}]$", "cool")
print ('CA')

MapaBolasTrimestre(CA, 'Trimestre_1', Lat75, Lon75, r"Promedio de DEF de la radiacion  $[W/m^{2}]$", "cool", ['Dic', 'Ene', 'Feb'])

