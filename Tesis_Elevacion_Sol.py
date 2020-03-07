#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from astropy.visualization import astropy_mpl_style
#plt.style.use(astropy_mpl_style)
import matplotlib.font_manager as fm
import datetime
import matplotlib.pyplot as plt
import pysolar
import pytz
# import astropy.units as u
# from astropy.time import Time
# from astropy.coordinates import SkyCoord, EarthLocation, AltAz
# from astropy.coordinates import get_sun

#---------------------------------------------------------------------------------
# Rutas para las fuentes ---------------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

#---------------------------------------------------------------------------------
## Con Astropy
medellin = EarthLocation(lat=6.259*u.deg, lon=-75.58*u.deg, height=1520*u.m)
utcoffset = -5*u.hour  # Eastern Daylight Time
time_pd = pd.date_range(start='2018-01-01 00:00', end='2018-12-31 23:00', freq='H')
time_str = [time_pd[i].strftime("%Y-%m-%d %H:%M:%S") for i in range(len(time_pd))]
time = [Time(time_str[i]) - utcoffset for i in range(len(time_str))]

frame_Medellin = [AltAz(obstime=time[i], location=medellin) for i in range(len(time_str))]
sunaltazs_Medellin = [get_sun(time[i]).transform_to(frame_Medellin[i]) for i in range(len(time_str))]

Alturas_Medellin = [sunaltazs_Medellin[i].alt for i in range(len(time_str))]   ## Alturas para cada hora del 2018

#---------------------------------------------------------------------------------


def Elevation_RadiationTA(n, lat, lon, start):
    'Para obtener la radiación en W/m2 y el ángulo de elevación del sol en grados horariamente para un número "n" de ' \
    'días aun punto en una latitud y longitud determinada ( "lat-lon"como flotantes) a partir de una fecha de inicio ' \
    '"start" como por ejemplo datetime.datetime(2018, 1, 1, 8).'
    lat, lon = 6.259, -75.58  # Medellin coloombia
    start = datetime.datetime(2018, 1, 1, 8)  # 1 Jan 2018, 0800 UTC

    timezone = pytz.timezone("America/Bogota")
    start_aware = timezone.localize(start)

    # Calculate radiation every hour for 365 days
    #nhr = 24*n
    nhr = 24 * 365
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

days, altitudes_deg, radiations = Elevation_RadiationTA(365, 6.259, -75.58, datetime.datetime(2018, 1, 1, 8))

# fig, axs = plt.subplots(nrows=2,ncols=1,sharex=True)
# axs[0].plot(days,altitudes_deg)
# axs[0].set_title('Solar altitude, degrees')
# axs[1].plot(days,radiations)
# axs[1].set_title('Solar radiation, W/m2')
# axs[1].set_xlabel('Days since ' + start_aware.strftime('%Y/%m/%d %H:%M UTC'))
#plt.savefig('/home/nacorreasa/Escritorio/pysolar.png')

fig, axs = plt.subplots(nrows=1,ncols=1,sharex=True)
axs[1].plot(days, radiations[0:48])
plt.savefig('/home/nacorreasa/Escritorio/pysolardia.png')

