import csv
import struct
import time
import random
from ipcqueue import sysvmq
import threading
pageTable=[]
tamanoPT=0
FORMAT='IIfB' # IdentificadorSensor,fecha, dato,bit para verificar dato. 
#Pedir datos, metodo que va a llamar el graficador
#Buscar page table
#Malloc maravilloso 
#Guardar 
#HabilitarPagina = 0
#pedirPagina =1
#guardar=2
buzonGeneral=sysvmq.Queue(420)#Buzon para procesos recolectores
buzonLlamados=sysvmq.Queue(17)#Buzon para solicitar al administrador meter datos.
buzonRetornos=sysvmq.Queue(16)#Buzon para recibir la respuesta del administrador.
buzonParametros=sysvmq.Queue(15)
buzonLlamadoGraficador=sysvmq.Queue(69)
buzonRetornoGraficador=sysvmq.Queue(469)
def mallocMaravilloso(sensorId,tamanoPagina): #Agrego en la page table y despues habilito pagina en memoria principal 
	global pageTable,tamanoPT					#Y despues meto el numero de pagina en la page table 
	pageTable.append([])
	pageTable[tamanoPT].append(sensorId)
	print(pageTable)
	buzonLlamados.put(0)
	print("TamanoPagina",tamanoPagina)
	buzonParametros.put(tamanoPagina)
	nuevaPag=buzonRetornos.get()
	#nuevaPag=aMemoria.habilitarPagina(tamanoPagina)
	pageTable[tamanoPT].append(nuevaPag)
	tamanoPT+=1
	
def getPaginasSensor(sensorId):# Busca en la page table y retorna los numeros de pagina referentes a un sensorId, lo utiliza pedirDatos()
	global pageTable,tamanoPT
	encontrado=False
	numerosPagina=[]
	i=0
	while(i<tamanoPT and encontrado==False):
		if(pageTable[i][0]==sensorId):
			numerosPagina=pageTable[i][1:]
			encontrado=True
		i+=1
	return numerosPagina

def pedirDatos(sensorId): # Pido datos por medio de un sensor ID,la interfaz los va a buscar a la pagetable y se comunica con la memoria principal para retornarlos
	numerosPaginaSensor=[]
	matrizRetorno = []
	numeroPaginaSensor=getPaginasSensor(sensorId)
	for i in range(0,len(numeroPaginaSensor)):
		matrizRetorno.append([])
		buzonLlamados.put(1)
		print("Numero pagina Sensor",numeroPaginaSensor[i])
		buzonParametros.put(numeroPaginaSensor[i])
		paginaAMeter=buzonRetornos.get()
		print ("pam: ",paginaAMeter,i)
		matrizRetorno[i].append(paginaAMeter)
	buzonRetornoGraficador.put(matrizRetorno)
	
def buscarSensorId(sensorId):#Busco el sensorId en la page table y me retorna el indice
	global pageTable,tamanoPT
	indice=-1
	i=0
	hallado=False
	while(i<tamanoPT and hallado==False):
		if(pageTable[i][0]==sensorId):
			indice=i
		i+=1
	return indice
			
def getSensorId(pack):#Desempaqueta y retorna el sensor id
	var = struct.unpack(FORMAT,pack) # Desempaqueta los datos recibidos
	identificador=var[0]
	return identificador
	
def datoUtil(pack):#Desempaqueta y retorna fecha y dato en un paquete
	var = struct.unpack(FORMAT,pack) # Desempaqueta los datos recibidos
	print("Arreglo de Paquete desempaquetado",var)
	datoAleer=var[3]
	packUtil=0
	#packUtil=[var[1],var[2]]
	
	if(datoAleer==0):
		packUtil=struct.pack('IB',var[1],var[2])
	elif(datoAleer==1):
		packUtil=struct.pack('II',var[1],var[2])
	elif(datoAleer==2):
		packUtil=struct.pack('If',var[1],var[2])
		
	print("Contenido packUtil",packUtil)
	return packUtil

def getTamanoPag(pack):
	tamPagina=0
	var = struct.unpack(FORMAT,pack) # Desempaqueta los datos recibidos
	datoAleer=var[3]
	if(datoAleer==0):
		tamPagina=5
	else:
		tamPagina=8
	return tamPagina

def guardar(pack):#Busca el sensor ID, sino esta entonces lo agrega a la page table y luego guarda los datos en memoria.
	global pageTable
	ind=buscarSensorId(getSensorId(pack))
	if(ind==-1):
		tamPagina=getTamanoPag(pack)
		mallocMaravilloso(getSensorId(pack),tamPagina)
	packDatos=datoUtil(pack)
	buzonLlamados.put(2)
	buzonParametros.put(packDatos)
	print(pageTable[ind][len(pageTable[ind])-1])
	buzonParametros.put(pageTable[ind][len(pageTable[ind])-1])
	numP=buzonRetornos.get()
	#numP=aMemoria.guardar(packDatos)
	if(numP!=-1):
		pageTable[ind].append(numP)
	
while(True):
	packRecolector =-1
	try:	
		packRecolector = buzonGeneral.get_nowait() # get_nowait() revisa el buzon, si esta vacio no pasa nada, y sino recibe el dato para enviarlo
	except:
		pass	
	if 	(packRecolector != -1):
		guardar(packRecolector)
	sID=-1
	try:
		sID=buzonLlamadoGraficador.get_nowait()
	except:
		pass
	if(sID!=-1):
		pedirDatos(sID)
	time.sleep(1)
		
