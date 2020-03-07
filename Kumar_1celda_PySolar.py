# -*- coding: utf-8 -*-
"""
Created on Fri May 26 09:17:39 2017

@author: Asus
"""

'''Modelo de Radiación Kumar,1997 1 Celda
Filosofía:
La ROC que alcanza la tierra puede ser: directa, difusa o reflejada.

La radiación global de onda corta que recibe la tierra es casi proporcional a la
directa y varía con la geometría del terreno. la difusa responde más a variaciones
del gradiente del terreno. Para cielos despejados esta variación con respecto a la
topografía se comparte entre la difusa y la directa, lo cual hace que se conserve
la variabilidad espacial de la radiación percibida.

Radiación difusa:
    Isotropica: condiciones de cielo despejado
    Anisotropica: condiciones de cielo nublado o parcialmente nublado

Objetivo: Computing potential solar radiation (the amount of shortwave radiation
received under clear-sky conditions), over a large area using only digital elevation
and latitude data and to study the variation in radiation at different aspects and slopes.


El modelo calcula radiación de onda corta directa, sobre una superficie de la tierra
en un periodo de tiempo dado. Para un día dado, calcula los tiempos de amanecida y de 
atardecer, e integra la radiación solar desde el amanecer al atardecer de cada día.
Tiene en cuenta la radiación difusa de manera simplificada


PRIMER ENSAYO
Ensayo partiendo de que la pendiente = 0° y el aspecto es -1, por ser una celda plana

An understanding of the nature of extraterrestrial radiation, the effects of orientation
of a receiving surface, and the theoretically possible radiation at the earth’s surface is
important in understanding and using solar radiation data (libro de energía solar)

DUDAS:
Unidades del hillshade, Angulo Horario
Si tuvo en cuenta la radiación difusa
Solar time? 

- por el tiempo que hay.. la idea es hallar la irradiación en W/m2 y multiplicarla por el numero de
segundos que tiene el delta t...para integrarla y así hayar la irradiancia de ese delta t?

CONCEPTOS (solar Enginnering of thermal processes):
Irradiance, W/m2 The rate at which radiant energy is incident on a surface per unit
area of surface. The symbol G is used for solar irradiance, with appropriate subscripts for
beam, diffuse, or spectral radiation.

Irradiation or Radiant Exposure, J/m2 The incident energy per unit area on a
surface, found by integration of irradiance over a specified time, usually an hour or a day.
Insolation is a term applying specifically to solar energy irradiation. The symbol H is used
for insolation for a day. The symbol I is used for insolation for an hour (or other period if
specified).
....    
    '''

#paquetes requeridos
import numpy as np
import datetime as dt
import Pysolar.solar as ps
import pandas as pd
from dateutil.relativedelta import relativedelta
import pylab as plt

#==============================================================================
'''Inputs del modelo
OJO A LOS RADIANES'''
#==============================================================================

saved_kumar = {}
saved_python = {}

#Calculos diurnos:
#Declinación solar constante al día:
#    
#Calculos en cada delta t:
#Azimuth (en sentido horario con 0° en el sur (180°  ))
#Elevación
#

'''En este ensayo pondré todo en terminos de los angulos hallados con PySolar 0.6'''

def sun_elevation(latitude,longitude,date_time,elevacion_msnm):
    '''Altitude is reckoned with zero at the horizon. The altitude
is positive when the sun is above the horizon.'''
    #GetAltitude(latitude_deg, longitude_deg, utc_datetime, elevation = 0, temperature_celsius = 25, pressure_millibars = 1013.25)
    ele =  ps.GetAltitude(latitude,longitude,date_time,elevation = elevacion_msnm)
    return ele
    
def sun_azimuth(latitude,longitude,date_time,elevacion_msnm):
    '''Azimuth is reckoned with zero corresponding to south. Positive azimuth
estimates correspond to estimates east of south; negative estimates are west of south.'''
    azi = ps.GetAzimuth(latitude,longitude,date_time,elevation = elevacion_msnm)+360
    #GetAzimuth(latitude_deg, longitude_deg, utc_datetime, elevation = 0)
    return azi


def sunrise(Elevation_day,Azimuth_day):
    #Se define amanecer y atardecer cuando hay un cambio de signo en la elevación 
    aux = np.where(Elevation_day.values>0)
    #Amanecer
    e_sunrise = Elevation_day.ix[aux[0][0]]
    a_sunrise = Azimuth_day.ix[aux[0][0]]
    time_sunrise = Elevation_day.index[aux[0][0]]
    return  e_sunrise, a_sunrise, time_sunrise

def sunset(Elevation_day,Azimuth_day):
    #Se define amanecer y atardecer cuando hay un cambio de signo en la elevación 
    aux = np.where(Elevation_day.values>0)
    #Atardecer    
    e_sunset = Elevation_day.ix[aux[0][-1]]
    a_sunset = Azimuth_day.ix[aux[0][-1]]
    time_sunset =  Elevation_day.index[aux[0][-1]]
    return e_sunset, a_sunset, time_sunset
    

def Hour_angle(date_time):
    '''The hour angle describes how far east or west the Sun is from the local meridian.
    It is zero when the Sun is on the meridian and decreases at a rate of 15° per hour
    Negativo: desde la medianoche cuando -12 (-180°), 0: al mediodía
    Positivo: desde el mediodía a la media noche (180°)'''
    hour_local = date_time.hour + (date_time.minute/60.) + (date_time.second/3600.)
    hs = 180 - (15* hour_local)
    
    return hs
    


def Day_number(date_time):
    #para conocer el día juliano se usa el atributo día del año de la función timetuple
    N =  date_time.timetuple().tm_yday
    return N
#==============================================================================
# Inputs    
#==============================================================================

#Hora local
date_str = '2017-01-01'
date_time = dt.datetime.strptime(date_str,'%Y-%m-%d') 
TI = 30 #Tiempo de intervalo en minutos, entre los calculos de flujo
UTC = -5
LD = 6.25225  #Latitud del sitio en grados (positivo al norte, ngativo al sur del ecuador)
LON = -75.5664
ELEVACION = 0 #m.s.n.m

SD = Day_number(date_time) #Día de Inicio del calculo
ED = Day_number(date_time) #Día de finalización del calculo
DEM = 1

#Comienzo del flow chart 
#==============================================================================
#Conversiones
DR = ((2.*np.pi)/360.)  # factor de conversion de grados a radianes
N = SD  #es el día de inicio del calculo 
TR = TI * 0.004363323  #Convertir minutos en radianes (15° por hora /60 minutos).*DR)
LR = LD*DR #Latitud en radianes
#==============================================================================
#Valores asociados al DEM

B_d = 0 #Es la pendiente que se obtiene del DEM
B = B_d*DR # Pendiente en radianes

aW_n = -1 #Es el aspecto que se obtiene del DEM (con 0° en el norte)
#Cambio de aspecto porque el azimuth es cero en el sur (ESTO ES SI EL ASPECTO VA DE 0 - 360)
if aW_n== -1: aW_s = 0
elif aW_n <= 180: aW_s = 180 - aW_n # si se ubica entre N-E-S,  (le less or equal)
elif aW_n > 180: aW_s = aW_n - 180 # si se ubica entre S-W_E, 
else:
    'Valor de aspecto invalido' #elif aW_n == 360: 540 - aW_n
aW = aW_s*DR # aspecto en radianes

W0 = 0  #Initialgrid
#==============================================================================
#  Calculos paralelos pysolar
#==============================================================================
index_horas = [pd.date_range(date_str+' 00:00',date_str+' 23:59',freq='1min')]    
    
Elevations = pd.DataFrame(index = index_horas, columns = ['Elevations'])
Azimuths = pd.DataFrame(index = index_horas, columns = ['Azimuths'])
          

date_day= pd.date_range(date_str+' 00:00',date_str+' 23:59',freq="1min")         
dates_utc = [dtime + relativedelta(hours=(UTC*-1)) for dtime in date_day]  
           

Eleva =  [sun_elevation(LD,LON,d,ELEVACION) for d in dates_utc]
Azimu = [sun_azimuth(LD,LON,d,ELEVACION) for d in dates_utc]      
Elevations ['Elevations'] =Eleva
Azimuths['Azimuths'] = Azimu
         
'''  Este enfoque me parece más preciso que el dado por el algoritmo original
porque el azume que  SS = -SR en términos de alguno horario solar...'''    
e_sunsrise, a_sunsrise,index_sunrise = sunrise(Elevations,Azimuths)
e_sunset, a_sunset, index_sunset = sunset(Elevations,Azimuths)
SS_ps = Hour_angle(index_sunset)*DR
SR_ps = Hour_angle(index_sunrise)*DR

#==============================================================================
# 
#==============================================================================


while N <= ED: #Para que lo realice mientras hasta que llegue al día final
    #==============================================================================
    def Declination_angle(N):
        '''Devuelve el angulo de inclinaciónd e la tierra en Radianes y se calcula con el día Juliano'''
        DR = (2*np.pi/360.)
        ds = 23.45*DR*np.sin((360.*DR)*(284.+N)/365.)
        return ds
    
    ds =  Declination_angle(N) #En radianes
    
    def Solar_flux_out_atmosphere(N):
        '''Estima la radiación incidente a tope de atmósfera en W/m2, con la ecuación de 
        Kreith and Kreider (1978) and Duffie and Beckman (1991)
        
        Esto considera la variación de la distancia entre la tierra y el sol durante el año
        debido a la excentricidad de la orbita de la tierra'''
        
        So = 1367. #Constante solar (W/m2)
        Io = So*(1+(0.0344*np.cos((360.*DR*N/365.))))
        return Io
        
    Io = Solar_flux_out_atmosphere(N)

    print 'OK Io: '+str(Io)
    #==============================================================================
    '''Ajuste para latitudes exceding 66.5 N/S, verificar que x  no es mayor a 1 para acos(x)'''
    if  -1 * np.tan(LR) * np.tan(ds) < -1.0: #less than (lt)
        SR = np.arccos(-1.0)                                              
    elif -1 * np.tan(LR) * np.tan(ds) >  1.0: #greater than (gt)           
        SR = np.arccos(1.0)                                               
    else:    # PARA EL RESTO DE LATITUDES                                                                      "
        SR = np.arccos(-1*np.tan(LR)*np.tan(ds)) #Amanecer en radianes (para -66.5°,66.5°)
        
    SS = -SR #Atardecer  en radianes
    print 'Amanecer Angulo horario Rd: original' +str(SR) + '  Pysolar '+ str(SR_ps)
    print 'Atarceder Angulo horario Rd: original' +str(SS) + '  Pysolar '+ str(SS_ps)
    #==============================================================================
    '''Hour angle, the angular displacement of the sun east or west of the local meridian
    due to rotation of the earth on its axis at 15◦ per hour; morning negative, afternoon
    positive.'''
    hs = SR - (TR/2.) # Angulo horario real en el momento del calculo (en la mitad del intervalo)
    #==============================================================================
    Np = 0 #numero de paso

    while hs >= SS: #Para que lo realice mientras hasta que llegue el atardecer
#        print 'Angulo horario: '+str(hs)
#        print  hs > SS
    #==============================================================================
        #Hallar angulo de elevacion del sol
        def altitud(LR,ds,hs):
            '''Esta función calcula el angulo de elevación del sol (en radianes) sobre una superficie plana
            en función de L: latitud del sitio, ds: Ángulo de declinación solar, hs: Ángulo horario
            TODOS EN RADIANES'''
            sin_a = (np.sin(LR)*np.sin(ds)) + (np.cos(LR)*np.cos(ds)*np.cos(hs))
            a = np.arcsin(sin_a)
            return a

        a = altitud(LR,ds,hs)
        aD = a/DR
        print 'a en grados: '+str(aD)
        #==============================================================================
        #Hallar angulo de azimuth
        
        def azimuth(ds,hs,a):    
            ''' the angular displacement from south of the projection of beam radiation
            on the horizontal plane. Displacements east of south are negative and west of
            south are positive.
            Esta función calcula el angulo de azimuth del sol (en radianes) sobre una superficie plana
            en función de L: latitud del sitio, ds: Ángulo de declinación solar, hs: Ángulo horario
            TODOS EN RADIANES'''
            sin_az = (np.cos(ds)*np.sin(hs))/np.cos(a)
            az = np.arcsin(sin_az)
            return az

        '''Porque el condicional'''
        #To find the azimuth angle, it is important to distinguish the case where the Sun
        #is in the northern half of the sky from the case where it is in the southern half.
        #If cos hs is greater ( less) than tan ds /tan L then the Sun is in the northern
        #(southern) half of the sky and its azimuth angle is in the range - 90° to 90° (90° to 270°).
        
        TEST = np.tan(ds)/np.tan(LR)
        Y = np.cos(hs)
        
        if Y > TEST: az = azimuth(ds,hs,a)
        elif Y < TEST:  az = np.pi - azimuth (ds,hs,a)
        elif Y == TEST and hs>=0: az = np.pi/2.
        elif Y == TEST  and hs <0: az = - np.pi/2.
        else: 
            print 'El calculo de azimuth esta raro'
        print 'az (degrees): '+str(az/DR)
        
        #==============================================================================
        #Conversión de ángulos a grados para poner como input en hillshade
        if az >= 0:
            azD = az/DR
        else: 
            azD = 360 - (np.abs(az)/DR) 
            '''OJO EN EL ORIGINAL ESTABA SIN VALOR ABSOLUTO'''
        
        
        #==============================================================================
        '''Calculo de la radiación DIRECTA'''
        #==============================================================================
        #Solar radiation received at a site will depend upon the solar flux outside the
        #atmosphere, the optical air mass, water vapour and aerosol content of the atmosphere.
        
        
        def Air_mass_ratio(a):
            '''The air mass ratio is the relative mass of air through which solar radiation
            must pass to reach the surface of the Earth.
            It varies from M=1 when the Sun is overhead to about 30 when the Sun is at the horizon.
            The two main factors a ecting the air mass ratio are the direction of the path and
            the local altitude.
             Input: altitud en radiaciones'''
            M = np.sqrt(1229. + ((614.*np.sin(a))**2.)) - (614.*np.sin(a))
            return M
            
        M =  Air_mass_ratio(a)
        
#        print 'OK M: '+str(M)
        #As the solar radiation passes through the Earth’s atmosphere it is modi® ed due to:
        # - absorption by di erent gases in the atmosphere,
        # - molecular (or Rayleigh) scattering by the permanent gases,
        # - aerosol (Mie) scattering due to particulates.
        
        def transmittance(M):
            '''Kreith and Kreider (1978 ) have described the atmospheric transmittance for
            beam radiation by the empirical relationship given in equation.'''
            tb = 0.56*(np.exp(-0.65* M)+ np.exp(-0.095*M))
            
            return tb 
            
        tb = transmittance(M)    
#        print 'OK tb: '+str(tb)
        
        #Therefore the shortwave solar radiation striking a surface normal to the Sun’s
        #rays (Is) is given by equation (15). The atmospheric transmittance in the above
        #equation can be replaced by site speciic values if they are available.
        '''Se puede mejorar si se tienen los valores in situ.'''
        '''solar radiation striking a surface normal to the Sun’s'''
        Is = Io * tb
#        print 'Is (Io*tb): '+str(Is)
        #==============================================================================
        
        '''solar radiation on a tilted surface (Ip ).'''
        #In the next stage, shaded and illuminated points are calculated. The HILLSHADE
        #command (in both Arc/Info and Genasys) creates a shaded relief grid by considering
        #the illumination angle and shadows from a grid of elevation, solar azimuth angle
        #and solar altitude angle. Shadows are de® ned by the local horizon at each cell. In
        #Arc/Info shadows are assigned a value of zero and illuminated cells are given a value
        #of one
        
        '''sombra = 0 , iluminado = 1'''
        sombra = 1 #/*sungrid = HILLSHADE (%cover%, %solarazdeg%, %solaraltdeg%, shadow)
        
#       /*sungrid = HILLSHADE (%cover%, %solarazdeg%, %solaraltdeg%, shadow)  /*nez: was disabled because it is wrong in N-lat.
#       
#       &if ( %solarazdeg% <= 180 ) &then                                     /*nez: added to correct for northern lat.s
#         &s azi = [calc ( 180 - %solarazdeg% )]                              /*nez:                   "
#       &else                                                                 /*nez:                   "
#         &s azi = [calc ( 180 + ( 360 - %solarazdeg% ) )]                    /*nez:                   "
#         /*&type %azi%,  %solarazdeg%                                        /*nez:                   "
#

        '''Angle of incidence, the angle between the beam radiation on a surface and the normal
        to that surface. 0°, es que el angulo del sol y el normal esel mismo osea la rad es directa
        y mayor a 90 es que el sol esta por debajo de la superficie
        i is the angle between the normal to the surface and the direction to the Sun
        B y aW están en radianes aquí :'''
        cos_i= (np.sin(ds)*(np.sin(LR)*np.cos(B) - (np.cos(LR)*np.sin(B)*np.cos(aW))))+ \
                      (np.cos(ds)*np.cos(hs))*(np.cos(LR)*np.cos(B) + np.sin(LR)*np.sin(B)*np.cos(aW))+\
                      (np.cos(ds)*np.sin(B)*np.sin(aW)*np.sin(hs))
                     
        incidence = np.arccos(cos_i)/DR
        print 'cos_i in degres: OK (O - 90) '+str(incidence)
        Ip = Is * cos_i
        print 'Ip: '+str(Ip)
        
        
        #       /* Trust me on the following two lines (You always need to fudge a little).
        #       if cos_i < 0: shaded = 0
        #       else shaded = 1
        # =============================================================================

        '''obtencion de la radiacion difusa y reflejada'''
        def diffuse_radiation_kumar(B,a,tb,Io):
            '''Origen: Kumar ( tomado de Liu and Jordan)
            Diffuse solar radiation (Id ) was calculated using the method suggested by Gates (1980),
            Principle:  the smaller the transmittance to scattered skylight
            td is the radiation difusion coefficient. td can be related to tb by equation (Liu and Jordan 1960) 
            which applies to clear sky conditions, and shows that the greater the direct solar beam transmittance'''
            td= 0.271 - (0.294*tb)
#            td[a<=0] = 0 #Este condicional es para cuando no sea de día no ponga rad difusa
            if a ==0: ta =0
            Id= Io*td*(np.cos(B/2.)**2.)*np.sin(a)
            return Id
        
        def reflected_radiation_kumar(B,a,tb,Io):
            '''Origen: Kumar    
            The magnitude of reflected radiation depends on the slope of the surface and the
            ground reflectance coefficient. The reflected radiation here is the ground reflected
            radiation, both direct sunlight and diffuse skylight, impinging on the slope after
            being reflected from other surfaces visible above the slope’s local horizon. The
            reflecting surfaces are considered to be Lambertian. Here reflected radiation (Ir ) was
            calculated based on equation (19) (Gates 1980):
            where r is the ground reflectance coefficient and tr is the reflectance transmittivity'''
            r =  0.2 # A value of 0.20 was used for the reflectance coeficient of vegetation
            tr = 0.271 + (0.706*tb)
#            tr[a<=0] = 0 #Este condicional es para cuando no sea de día no ponga rad difusa
            if a ==0: tr =0
            Ir = r*Io*tr*(np.sin(B/2.)**2.)*np.sin(a)
            
            return Ir     

        Id = diffuse_radiation_kumar(B,a,tb,Io)   
        Ir = reflected_radiation_kumar(B,a,tb,Io)
        #==============================================================================
#        W2 = Ip* W1 * 60 *shaded* TI #
        W2 = ((Ip* sombra)+Id+Ir) * 60. * TI  # (Acum ese tiempo MJ/W2) supongo que es TI es para saber los segundos del intervalo de tiempo
#        W2 = Ip* sombra * 60 * TI #supongo que es TI es para saber los segundos del intervalo de tiempo
#        print 'W2 (W.s/m2) =(J/m2): '+str(W2)
        print 'W2 (MJ/m2): '+str(W2*1e-6)
        #==============================================================================
        W3 = W2 + W0
        
        '''Acumulador :)  W0 Es el resultado final'''
        W0 = W3 
        saved_kumar.update({Np:{'hs':hs,'W0_acum':W0,'az':azD,'azR':az,'alt':aD,'W_paso':W2,'i':incidence}})
        Np = Np+1 #aumento del numero de paso

#        print 'W0: '+str(W0) 
        print '____________________'

        
        ''' OJO CUAL ES EL PASO DE LA RADIACION DIRECTA Y DIFUSA'''
        #td is the radiation di usion coe cient. td can be related to tb by equation
        #(18) (Liu and Jordan 1960)
        #td=0.271 -(0.294*tb)
        ##Di use solar radiation (Id ) was calculated using the method suggested by Gates (1980)
        #Id=Io*td*(np.cos(b/2)**2)*np.sin(a)
        #
        ##==============================================================================
        '''CONTADOR PARA EL PASO SIGUIENTE'''
        hs = hs -TR  # en el amanecer este angulo aquí es positivo.... por eso se resta
        
    #==============================================================================
    #Pregunta si ya anocheció para saber si pasa al siguiente día
    N = N+1
        #==============================================================================
        #Pregunta si ya llegó al día final para parar la operación
        #==============================================================================
        #==============================================================================
    #        # # 
    #    %outgrid% = int(initialgrid)
    #/* NOTE : THE UNITS FOR RADIATION IN THE OUTGRID ARE kJ/m^2/timeperiod
    #/* If these are to be converted to MJ/m^2/day, then they should be divided by 1000 * no. of days.

    print 'Resultado final día'
    print 'W0:'+ str(W0*1e-6)+' en MJ/m2'

#==============================================================================
    print ' '
    print ' '
    print '''PROCESO CON PySolar''' 
#==============================================================================
    W0 = 0  #Initialgrid
    Np = 0 #numero de paso
    hs = SR_ps - (TR/2.) # Angulo horario real en el momento del calculo (en la mitad del intervalo)
    hs_index = index_sunrise
    while hs >= SS_ps: #Para que lo realice mientras hasta que llegue el atardecer
#        print 'Angulo horario: '+str(hs)
#        print  hs > SS
    #==============================================================================
        #Hallar angulo de elevacion del sol
        aD = sun_elevation(LD,LON,hs_index + relativedelta(hours=(UTC*-1)),ELEVACION)
        a = aD*DR
        print 'a en grados: '+str(aD)

        #==============================================================================
        #Hallar angulo de azimuth
        azD = sun_azimuth(LD,LON,hs_index + relativedelta(hours=(UTC*-1)),ELEVACION)
        az = np.abs(azD)*DR
#        az = np.abs((180.0 - azD)%360.0)*DR

        hss = Hour_angle(hs_index)*DR   
        TEST = np.tan(ds)/np.tan(LR)
        Y = np.cos(hss)
    
        if Y > TEST: az = az
        elif Y < TEST:  az = (az+np.pi)*-1
        elif Y == TEST and hss>=0: az = np.pi/2.
        elif Y == TEST  and hss <0: az = - np.pi/2.
        else: 
            print 'El calculo de azimuth esta raro'
        print 'az (degrees): '+str(az/DR)
            


        print 'az (degrees): '+str(az/DR)
        #==============================================================================
        '''Calculo de la radiación DIRECTA'''
        #==============================================================================
        def Air_mass_ratio(a):
            '''The air mass ratio is the relative mass of air through which solar radiation
            must pass to reach the surface of the Earth.
            It varies from M=1 when the Sun is overhead to about 30 when the Sun is at the horizon.
            The two main factors a ecting the air mass ratio are the direction of the path and
            the local altitude.
             Input: altitud en radiaciones'''
            M = np.sqrt(1229. + ((614.*np.sin(a))**2.)) - (614.*np.sin(a))
            return M
            
        M =  Air_mass_ratio(a)
        
#        print 'OK M: '+str(M)
        #As the solar radiation passes through the Earth’s atmosphere it is modi® ed due to:
        # - absorption by di erent gases in the atmosphere,
        # - molecular (or Rayleigh) scattering by the permanent gases,
        # - aerosol (Mie) scattering due to particulates.
        
        def transmittance(M):
            '''Kreith and Kreider (1978 ) have described the atmospheric transmittance for
            beam radiation by the empirical relationship given in equation.'''
            tb = 0.56*(np.exp(-0.65* M)+ np.exp(-0.095*M))
            
            return tb 
            
        tb = transmittance(M)    
#        print 'OK tb: '+str(tb)
        
        #Therefore the shortwave solar radiation striking a surface normal to the Sun’s
        #rays (Is) is given by equation (15). The atmospheric transmittance in the above
        #equation can be replaced by site speciic values if they are available.
        '''Se puede mejorar si se tienen los valores in situ.'''
        '''solar radiation striking a surface normal to the Sun’s'''
        Is = Io * tb
#        print 'Is (Io*tb): '+str(Is)
        #==============================================================================
        
        '''solar radiation on a tilted surface (Ip ).'''
        #In the next stage, shaded and illuminated points are calculated. The HILLSHADE
        #command (in both Arc/Info and Genasys) creates a shaded relief grid by considering
        #the illumination angle and shadows from a grid of elevation, solar azimuth angle
        #and solar altitude angle. Shadows are de® ned by the local horizon at each cell. In
        #Arc/Info shadows are assigned a value of zero and illuminated cells are given a value
        #of one
        
        '''sombra = 0 , iluminado = 1'''
        sombra = 1 #/*sungrid = HILLSHADE (%cover%, %solarazdeg%, %solaraltdeg%, shadow)
        
#       /*sungrid = HILLSHADE (%cover%, %solarazdeg%, %solaraltdeg%, shadow)  /*nez: was disabled because it is wrong in N-lat.
#       
#       &if ( %solarazdeg% <= 180 ) &then                                     /*nez: added to correct for northern lat.s
#         &s azi = [calc ( 180 - %solarazdeg% )]                              /*nez:                   "
#       &else                                                                 /*nez:                   "
#         &s azi = [calc ( 180 + ( 360 - %solarazdeg% ) )]                    /*nez:                   "
#         /*&type %azi%,  %solarazdeg%                                        /*nez:                   "
#

        '''Angle of incidence, the angle between the beam radiation on a surface and the normal
        to that surface. 0°, es que el angulo del sol y el normal esel mismo osea la rad es directa
        y mayor a 90 es que el sol esta por debajo de la superficie
        i is the angle between the normal to the surface and the direction to the Sun
        B y aW están en radianes aquí :'''
        cos_i= (np.sin(ds)*(np.sin(LR)*np.cos(B) - (np.cos(LR)*np.sin(B)*np.cos(aW))))+ \
                      (np.cos(ds)*np.cos(hs))*(np.cos(LR)*np.cos(B) + np.sin(LR)*np.sin(B)*np.cos(aW))+\
                      (np.cos(ds)*np.sin(B)*np.sin(aW)*np.sin(hs))
#        cos_i = 1
        incidence = np.arccos(cos_i)/DR

        print 'cos_i in degres: OK (O - 90) '+str(incidence)
        Ip = Is * cos_i
        print 'Ip: '+str(Ip)
        
        #=============================================================================
        '''obtencion de la radiacion difusa y reflejada'''
        Id = diffuse_radiation_kumar(B,a,tb,Io)   
        Ir = reflected_radiation_kumar(B,a,tb,Io)

        
#       /* Trust me on the following two lines (You always need to fudge a little).
#       if cos_i < 0: shaded = 0
#       else shaded = 1

        #==============================================================================
        '''Obtención de la radiación incidente global'''
        W2 = ((Ip* sombra)+Id+Ir) * 60. * TI   # (Acum ese tiempo MJ/W2) supongo que es TI es para saber los segundos del intervalo de tiempo
#        W2 = Ip* W1 * 60 *shaded* TI #
#        W2 = Ip* sombra * 60 * TI #supongo que es TI es para saber los segundos del intervalo de tiempo
#        print 'W2 (W.s/m2) =(J/m2): '+str(W2)
        print 'W2 (MJ/m2): '+str(W2*1e-6)
        #==============================================================================
        W3 = W2 + W0
        
        '''Acumulador :)  W0 Es el resultado final'''
        W0 = W3 
        saved_python.update({Np:{'hs':hs,'W0_acum':W0,'az':azD,'azR':az,'alt':aD,'W_paso':W2,'i':incidence,'date':hs_index}})
        Np = Np+1 #aumento del numero de paso

#        print 'W0: '+str(W0) 
        print '____________________'

        
        ''' OJO CUAL ES EL PASO DE LA RADIACION DIRECTA Y DIFUSA'''
        #td is the radiation di usion coe cient. td can be related to tb by equation
        #(18) (Liu and Jordan 1960)
        #td=0.271 -(0.294*tb)
        ##Di use solar radiation (Id ) was calculated using the method suggested by Gates (1980)
        #Id=Io*td*(np.cos(b/2)**2)*np.sin(a)
        #
        ##==============================================================================
        '''CONTADOR PARA EL PASO SIGUIENTE'''
        print hs_index
        hs = hs -TR  # en el amanecer este angulo aquí es positivo.... por eso se resta
        hs_index = hs_index + relativedelta(minutes = TI)

        
        
    #==============================================================================
    #Pregunta si ya anocheció para saber si pasa al siguiente día
    N = N+1
        #==============================================================================
        #Pregunta si ya llegó al día final para parar la operación
        #==============================================================================
        #==============================================================================
    #        # # 
    #    %outgrid% = int(initialgrid)
    #/* NOTE : THE UNITS FOR RADIATION IN THE OUTGRID ARE kJ/m^2/timeperiod
    #/* If these are to be converted to MJ/m^2/day, then they should be divided by 1000 * no. of days.

    print 'RESULTADOS KUMAR PySolar  CON EL cos(i) = 1 es decir que el angulo es 0'
    print 'Resultado final día'
    print 'W0:'+ str(W0*1e-6)+' en MJ/m2'
 
saved_kumar = pd.DataFrame.from_dict(saved_kumar,orient='index')
saved_python = pd.DataFrame.from_dict(saved_python,orient='index')

plt.figure()
plt.title('Azimuth sol - Grados')
plt.plot(saved_kumar['az'],label = 'Kumar');plt.plot(saved_python['az'])
plt.legend()
plt.show();plt.close()


plt.figure()
plt.title('Azimuth sol - radianes')
plt.plot(saved_kumar['azR'],label = 'Kumar');plt.plot(saved_python['azR'])
plt.legend()
plt.show();plt.close()
            
            
plt.figure()
plt.title('Elevacion sol - grados')
plt.plot(saved_kumar['alt'],label = 'Kumar');plt.plot(saved_python['alt'])
plt.legend()
plt.show();plt.close()


plt.figure()
plt.title('Irradiancia por paso de tiempo')
plt.plot(saved_kumar['W_paso'],label = 'Kumar');plt.plot(saved_python['W_paso'])
plt.legend()
plt.show();plt.close()

plt.figure()
plt.title('Angulo incidencia en grados')
plt.plot(saved_kumar['i'],label = 'Kumar');plt.plot(saved_python['i'])
plt.legend()
plt.show();plt.close()


plt.figure()
plt.title('Irradiacion integrada en \n cada paso de tiempo')
plt.plot(saved_kumar['W0_acum']*1e-6,label = 'Kumar');plt.plot(saved_python['W0_acum']*1e-6)
plt.legend()
plt.show();plt.close()



#==============================================================================
#==============================================================================
#==============================================================================
#import Pysolar.solar as ps
#def sun_elevation(latitude,longitude,date_time,elevacion_msnm):
#    #GetAltitude(latitude_deg, longitude_deg, utc_datetime, elevation = 0, temperature_celsius = 25, pressure_millibars = 1013.25)
#    ele =  ps.GetAltitude(latitude,longitude,date_time,elevation = elevacion_msnm)
#    return ele   
#def sun_azimuth(latitude,longitude,date_time,elevacion_msnm):
#    azi = ps.GetAzimuth(latitude,longitude,date_time,elevation = elevacion_msnm)
#    #GetAzimuth(latitude_deg, longitude_deg, utc_datetime, elevation = 0)
#    return azi  #Para que el azimuth sea de 0 a 360
