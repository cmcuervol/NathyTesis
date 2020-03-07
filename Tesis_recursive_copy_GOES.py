# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import datetime as dt
import os

path_directory = "/home/nacorreasa/Maestria/Datos_Tesis/GOES/Ejemplos_Folders/"   ## Donde se van a consultar originalmente
path_copy = "/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_Copy/"              ## Donde quedará cada imagen copiada

Banda = '02'
fec_ini = '2018-01-01'
fec_fin = '2018-03-30'


# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
                                        # No cambiar nada en adelante
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

fi  = dt.datetime.strptime(fec_ini, '%Y-%m-%d')
ff  = dt.datetime.strptime(fec_fin, '%Y-%m-%d')


def daterange(start_date, end_date):                                  ## PARA LA SELECCION DE LAS CARPETAS DE INTERES
    delta = timedelta(days=1)
    while start_date <= end_date:
        yield start_date
        start_date += delta

Folders_Range = []
for single_date in daterange(fi, ff):
    Folders_Range.append(single_date.date().strftime('%Y%m%d'))

Storinator_Foders = [name for name in os.listdir(path_directory)]
Storinator_Foders = [name[0:8] for name in Storinator_Foders]

Folders = [i for i in Folders_Range if i in Storinator_Foders ]
Folders = sorted(Folders, key=lambda x: datetime.strptime(x, '%Y%m%d'))

def Copy_full_images (path_directory, path_copy):
    for filename in Folders:
        os.system('mkdir ' + path_copy + filename + '_' + Banda + '/')
        os.system('scp  ' + path_directory + filename + '/OR_ABI-L1b-RadF-M3C' + Banda + '* ' + path_copy + filename + '_' + Banda + '/' )
        print ('Archivos copiados de la banda ' + Banda)

Copy_full_images (path_directory, path_copy)
