#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Esta aplicacion recorre un dossier y registra toda la informacion de este y comprueba si hay cambios en ellos, si ocurre algun cambio lo señala en un log.
# Se debe aplicar sobre los datos significativos si detecta un movimiento estragno la app
import os
import shutil
import time

# Itineracion de creacion diccionario
import collections
import itertools
import pickle

import sys
import hashlib

#################PROYECTO##################
proyect = "SaveServer"
version = "V180924_0.2"

# letreDir = 'D:\\'
rootDir = 'D:\\test'  #
DebugMode = True


# *******************OBTENER DATOS COMO DICIONARIO CON HASH******************#
# Coge toda la informacion pero devuelve un diccionario donde la clave principal es el hash del fichero
def getDicionarioInfoFiles(ruta):
    tGetFiles = time.time()
    print ("Inicia obtencion de datos")
    numeroFichero = 0
    newListDiccionarioInfo = collections.defaultdict(list)
    fileListReturn = []
    for dirName, subdirList, fileList in os.walk(ruta, topdown=False):  # Cojo direccion completa y recorro
        for fname in fileList:  # Cojo nombre y recorro
            direcionFile = dirName + "\\" + fname  # Conformo la direccion
            try:
                fichero = []
                filesize = os.path.getsize(direcionFile)  # Tamano en bytes (Para kilobyte /1024 y megabyte /1024/1024 y asi cuanto quieras)
                filetime = os.path.getmtime(direcionFile)  # Fecha de modificacion
                fichero.append(dirName.encode('utf-8'))
                fichero.append(fname.encode('utf-8'))
                fichero.append(time.ctime(filetime).encode('utf-8'))
                fichero.append(str(filesize).encode('utf-8'))
                # Clave valor el hash del fichero y su registro es (posicion, nombre , fecha y tamaño en byte)
                newListDiccionarioInfo[file_hash(direcionFile)].append(fichero)
            except Exception as e:
                print ("El fichero (" + direcionFile + ") no es compatible")
                print (e)
            numeroFichero = numeroFichero + 1
    # print('-----------FIN-----------')
    print ('Numbers of files :',numeroFichero)
    print ('Tiempo usado en extaccion de listado:', time.time() - tGetFiles)
    # print (dict(newListDiccionarioInfo))
    return newListDiccionarioInfo

# **********************ANALISIS DE RESULTADOS*********************** 
def evaluacionDic(lastDic,newDic):
    tGetFiles = time.time()
    print ("Inicia Analisis")

    dictDeDiferencias = collections.defaultdict(list) # HASH : []
    for indexnewDic, filenewDic in enumerate(newDic):
        if filenewDic in lastDic:
            if (newDic[filenewDic] == lastDic[filenewDic]): #No me interesan las cosas que no cambian
                #print ("El fichero "+ str(newDic[filenewDic]) + " se encuentra y NO CAMBIO") 
                pass
            else: #Hash igual pero algun cambio hay en la estructura de las listas que cambio
                #print ("El fichero "+ str(newDic[filenewDic]) + " se encuentra pero TIENE DIFERENCIAS con respecto" + str(lastDic[filenewDic]))
                #Tengo que encontrar las diferencias
                # Fecha -> fue abierto no modificado
                # Ruta -> Movido
                # Mas Listas o Menos que antes -> Fue copiado o borrado una copia (Ficheros identicos en las estructura) (Cambio de nombre or/and direccion)
                listnew = newDic[filenewDic]
                listlast = lastDic[filenewDic]
                if (len(listnew) == len(listlast)): #No hay copias nueva del fichero
                    for indexnewList, filenewList in enumerate(listnew):
                        if (filenewList == listlast[indexnewList]):             #No me interesan las cosas que no cambian
                            #print ("Este indice del hash NO fue modificado")
                            #No hay copias nueva del fichero
                            pass
                        else:
                            #print ("Este indice del hash FUE modificado")
                            #if not x == 'val' es el más lento.
                            #if x == 'val' + else es ~1.7% más rápido.
                            #if x != 'val' es ~3.6% aún más rápido.
                            if (filenewList[0] != listlast[indexnewList][0]): #Cambio la ruta
                                print ("Cambio la RUTA "+ str(filenewList[0]) + " que anteriormente era " + str(listlast[indexnewList][0]))
                            if (filenewList[1] != listlast[indexnewList][1]): # Cambio el nombre  
                                print ("Cambio el NOMBRE "+ str(filenewList[1]) + " que anteriormente era " + str(listlast[indexnewList][1]))
                            if (filenewList[2] != listlast[indexnewList][2]): # Cambio el fecha  
                                print ("Cambio la FECHA "+ str(filenewList[2]) + " que anteriormente era " + str(listlast[indexnewList][2]))
                            #El tamaño no hace falta evaluarlo si cambia el tamaño cambia el MD5
                elif(len(listnew) > len(listlast)): #Hay mas copias del fichero
                    print ("Se REALIZARON copias del fichero")

                else: # (len(listnew) < len(listlast))
                    print ("Se ELIMINARON copias del fichero")

        else: # Cambio el hash 2 posibilidad Fichero unico nuevo or Fichero Modificado (EN ESTE MOMENTO NO SE PUEDE SABER)
            print ("El fichero "+ str(newDic[filenewDic]) + " a sido Creado Fichero Unico/modificado")

    for indexlastDic, filelastDic in enumerate(lastDic):
        if filelastDic in newDic: #No Es necesario ya fue controlado en if filenewDic in lastDic: 
            pass
        else:  # Cambio el hash 2 posibilidad Fichero unico borrado or Fichero Modificado (EN ESTE MOMENTO SE PUEDE SABER APROXIMADAMENTE)(ES EL NOMBRE IGUAL Y LA RUTA)
            print ("El fichero "+ str(lastDic[filelastDic]) + " a sido borrado Fichero Unico/modificado")
            #Ahora tengo que evaluar si lo que se creo y lo que se borro tienen el mismo nombre porque si es asi fue modificado
    print ("*******************************************************************************")
    print("------------Tiempo--------------")
    print ('Tiempo usado en el analisis:', time.time() - tGetFiles)
    print("--------------------------------")

def evaluefile(laststruct, listnew): #(NO SE USA) Dadas dos listas comprueba las listas
    for indexnewList, filenewList in enumerate(listnew):
        if (listlast == listlast[indexnewList]):             #No me interesan las cosas que no cambian
            #print ("Este indice del hash NO fue modificado")
            #No hay copias nueva del fichero
            pass
        else:
            #print ("Este indice del hash FUE modificado")
            #if not x == 'val' es el más lento.
            #if x == 'val' + else es ~1.7% más rápido.
            #if x != 'val' es ~3.6% aún más rápido.
            if (filenewList[0] != listlast[indexnewList][0]): #Cambio la ruta
                print ("Cambio la ruta "+ str(filenewList[0]) + " que anteriormente era " + str(listlast[indexnewList][0]))
            if (filenewList[1] != listlast[indexnewList][1]): # Cambio el nombre  
                print ("Cambio el nombre "+ str(filenewList[1]) + " que anteriormente era " + str(listlast[indexnewList][1]))
            if (filenewList[2] != listlast[indexnewList][2]): # Cambio el fecha  
                print ("Cambio la fecha "+ str(filenewList[2]) + " que anteriormente era " + str(listlast[indexnewList][2]))
            #El tamaño no hace falta evaluarlo si cambia el tamaño cambia el MD5

# **********************BUSCADOR DE FICHERO DUPLICADOS***************************#
def ficherosDuplicados (newDic):
    tGetFiles = time.time()
    print ("Inicia ficherosDuplicados")

    for indexnewDic, filenewDic in enumerate(newDic):
        if (len(newDic[filenewDic]) > 1):
            printValueToStruct (newDic[filenewDic],0,1)

    print ("*******************************************************************************")
    print("------------Tiempo--------------")
    print ('Tiempo usado en el ficherosDuplicados:', time.time() - tGetFiles)
    print("--------------------------------")    

# **********************GUARDAR DATOS EN BRUTO***************************#
def cargardicionario():
    try:
        with open("dicFiles.dat", "rb") as f:
            return pickle.load(f)
    except (OSError, IOError, EOFError) as e:
        print ("Error de lectura : " + str(e))
        return dict()

def guardardiccionario(dic):
    with open("dicFiles.dat", "wb") as f:
        pickle.dump(dic, f)

# *******************HASH DEL FICHERO*******************************#
def file_hash(filename):
    # h = hashlib.sha1()
    # h = hashlib.sha256()
    h = hashlib.md5()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda: f.read(128 * 1024), b''):
            h.update(b)
    # print("MD5: {0}".format(h.hexdigest()))
    return h.hexdigest()

# *******************MOSTRAR INFO*******************************#
def printValueToStruct(struct, columna,columna1):
    # print (struct)
    for indexStruct, fileStruct in enumerate(struct):
        print (str(fileStruct[columna]))
        print (str(fileStruct[columna1]))

# *****************APLICACIONES******************************#
def appseguimientosfiledic():
    newDicFicheros = {}
    lastDicFichero = {}

    lastDicFichero = cargardicionario()               # Cargamos el anterior diccionario
    newDicFicheros = getDicionarioInfoFiles(rootDir)  # Rastrear ficheros
    if (lastDicFichero == newDicFicheros):
        print ("Todo sigue igual")
    else:
        print ("Hubo algun cambio en la extructura")
        evaluacionDic (lastDicFichero,newDicFicheros) #Evaluamos las diferencias entre diccionarios
        guardardiccionario(newDicFicheros)            #Guardamos el diccionario para la proxima    
    ficherosDuplicados (newDicFicheros)

    #print ("*ESTADO ANTERIOR************************************************************************")
    #print (dict(lastDicFichero))
    #print ("*NUEVO ESTADO***************************************************************")
    #print (dict(newDicFicheros))
    #print ("*******************************************************************************")

    # Tamagnos de las listas
    print ("Tamagnos de la newDicFicheros : " + str(newDicFicheros.__sizeof__()))
    print ("Tamagnos de la lastDicFichero : " + str(lastDicFichero.__sizeof__()))

# *****************MAIN APLICACION******************************#
if __name__ == "__main__":
    # ***************TITULO*********************
    if (DebugMode):
        print("-------------------------")
        print("****" + proyect + "*****")
        print("******" + version + "*******")
        print("-------------------------")
        DebugCiclos = 1  # Variable para los ver la repeticion del bucle principal del programa
        # ***************INICIO******************
    appseguimientosfiledic()

    # ---------------- SALIMOS DEL PROGRAMA -----------------------
    print ("Aplicacion Cerrada")
    input("FIN")
else:
    print("El modulo  ha sido importado")
