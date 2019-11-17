# coding: utf8
import struct
import time
import random
from ipcqueue import sysvmq
import pdb
numeroPagina = 0
memoriaPrincipal = [] #Memoria principal o local
numeroFilasMemoria = 4
contadorFilaActual = 0
max8 = 10575
max5 = 16920
buzonLlamados = sysvmq.Queue(17)
buzonRetornos = sysvmq.Queue(16)
buzonParametros = sysvmq.Queue(15)

#Codigos de llamados
#HabilitarPagina = 0
#pedirPagina =1
#guardar=2

for i in range(numeroFilasMemoria):
    memoriaPrincipal.append([])

def pasarPaginaLocalADistribuida(indPagSwap): #Recibe el indice de la página a hacer swap y pasa una página (arreglo) a memoria distribuida por medio de un paquete mediante un socket.
	global memoriaPrincipal
	guardado = False
	
	#Para el paquete de mandar a guardar en M.Distribuida se ocupan los siguientes datos:
	opCode = 0
	idPagina = memoriaPrincipal[indPagSwap][0]
	tamPag = 0 #Tamano de la pagina a la que se le esta haciendo swap en ese momento.
	if( memoriaPrincipal[indPagSwap][1] == 5 ):
		tamPag = len(memoriaPrincipal[indPagSwap]) * 5 #Para tener el tamano en bytes 
	elif( memoriaPrincipal[indPagSwap][1] == 8 ):
		tamPag = len(memoriaPrincipal[indPagSwap]) * 8 #Tamano en bytes
	datosPag = memoriaPrincipal[indPagSwap][:]
	
	#Se empaquetan y luego se envian esos datos mediante el protocolo correspondiente.
		#Con el puerto e IP que estan quemadas para la Interfaz Distribuida.
	
	#Para borrar la pagina de memoria local
	del memoriaPrincipal[indPagSwap][:]
	
	#Se recibe una confirmacion con: (Se debe ver si es necesario verificar lo que recibo.)
		#opCode (Ver si hubo algun error)
			#Si hubo error se debe volver a ejecutar este metodo y se devuelve false
			#Si se guardo bien devuelvo true (creo que solo eso)
		#idPagina
		#Si hay algun error que hacer? Se vuelve a enviar a guardar?

def pasarPaginaDistribuidaALocal(indPagSwap, numP):
	global memoriaPrincipal
	#Para el paquete de pedir a la interfaz distribuida una pagina se ocupan los siguientes datos:
	opCode = 1
	idPagina = numP
	#Se empaquetan y se envian los datos mediante el protocolo correspondiente.

	#Se recibe el paquete de respuesta
	#En caso de que no haya error (creo que se hace viendo el opCode):
	#Se recibe la pagina solicitada	
	idPaginaR = -1 #el -1 se debe cambiar por el idPagina recibida en protocolo
	datosPagina = 0 # el 0 se debe cambiar por los datos recibidos en protocolo

	#Colocar la pagina en memoria local
	memoriaPrincipal[indPagSwap] = datosPagina[:]

	#Si hay error (viendo opCode)

	
def busquedaPaginaSwap(): #Sirve para localizar el indice de la pagina en la que se va a ser swap.
	global memoriaPrincipal, max5, max8, numeroFilasMemoria
	pagSwapB = False
	indMemSwap = -1
	i = 0
	while(i<numeroFilasMemoria and pagSwapB == False):
		if( paginallenaMemoriaPrincipal(i) ):
			pagSwap = True
			indMemSwap = i
		i += 1

	#Si ninguna esta llena.
	if(pagSwapB == False):
		#Escoje una random
		indMemSwap = random.randint(0,numeroFilasMemoria-1)
	return indMemSwap


def busquedaPaginaMemoriaPrincipal(numPABuscar):#Sirve para localizar el indice de la pagina que se esta buscando en memPrincipal
	global memoriaPrincipal
	indiceARetornar = -1
	paginaEncontrada = False
	i = 0
	while(i<numeroFilasMemoria and paginaEncontrada==False):
		if(len(memoriaPrincipal[i]) > 0 and memoriaPrincipal[i][0]==numPABuscar):
			indiceARetornar = i
			paginaEncontrada = True
		i += 1
	return indiceARetornar
			
			
#Habilitarle una pagina a un proceso y la coloca en la memoria principal     
def habilitarPagina(tamanoCelda):
	global numeroPagina, contadorFilaActual,memoriaPrincipal,max5,max8,numeroFilasMemoria
	#Para cuando la memoria principal tiene filas vacias
	if (contadorFilaActual < numeroFilasMemoria): 
		memoriaPrincipal[contadorFilaActual].append(numeroPagina)
		numeroPagina += 1
		memoriaPrincipal[contadorFilaActual].append(tamanoCelda)
		contadorFilaActual += 1
	#Cuando esta llena, entonces se empieza a hacer swap.
	else:
		indMemSwap = busquedaPaginaSwap()
		pasarPaginaLocalADistribuida(indMemSwap)
		#Agregar nueva pagina en memoria local
		memoriaPrincipal[indMemSwap].append(numeroPagina)
		numeroPagina += 1
		memoriaPrincipal[indMemSwap].append(tamanoCelda)
	return numeroPagina-1


#Es para entregarle a la interfaz la pagina solicitada.		
def pedirPagina(numeroP):
	global memoriaPrincipal,numeroFilas,max5,max8
	paginaADevolver = []	
	indicePaginaADevolver = busquedaPaginaMemoriaPrincipal(numeroP)
	#Esta en memoria
	if (indicePaginaADevolver != -1):
		paginaADevolver = memoriaPrincipal[indicePaginaADevolver][:]
	#No esta en memoria
	else:
		#Hace swap
		indMemSwap = busquedaPaginaSwap()
		pasarPaginaLocalADistribuida(indMemSwap)
		pasarPaginaDistribuidaALocal(indMemSwap,numeroP)
		#Se toma de la memoria local la pagina deseada
		paginaADevolver = memoriaPrincipal[indMemSwap][:]
		
	#print("PagADevolver: ",paginaADevolver)
	return paginaADevolver
	
def paginallenaMemoriaPrincipal(indiceP): #Verificar por medio de un indice si una pagina esta llena en memoria local
	paginaLlena = False
	#print("Ind:" + str(indiceP))
	#print ("Tamano de celdas pagina" + str(memoriaPrincipal[indiceP][1]))
	#print ("Tamano" + str(len(memoriaPrincipal[indiceP])))
	if(memoriaPrincipal[indiceP][1] == 5):
		#print("Entre al if que es")
		if(len(memoriaPrincipal[indiceP]) == max5):
			#print("Entre a if que dice que si esta llena")
			paginaLlena = True
	elif(memoriaPrincipal[indiceP][1] == 8):
		if(len(memoriaPrincipal[indiceP]) == max8):
			paginaLlena = True
	#print("Retorna pagina llena con" + str(paginaLlena))
	return paginaLlena
	
def guardar(pack,numP): #Guarda en memoria. Puede tener varias condiciones que la pagina(que le da la intefaz local) este en memoria principal pero no este llena entonces solo guarda
						#Que este en memoria principal pero la pagina esta llena y que la pagina no este en memoria principal
	global numeroFilas, memoriaPrincipal,max5,max8
	numeroPag = -1 #Se retorna a la interfaz, para saber si se le habilito una nueva pagina a ese sensor o no(-1).
	indiceP = busquedaPaginaMemoriaPrincipal(numP)
	print(indiceP)
	#Si esta en memoria principal
	if(indiceP != -1):
		#print("Se llama a paginaLlena con indice" + str(indiceP))
		#Reviso si la pagina esta llena.
		paginaLlena = paginallenaMemoriaPrincipal(indiceP)
		#Si tiene espacio
		#print ("Pagina llena de guardar " + str(paginaLlena))
		if(paginaLlena == False):
			#Guarda el dato
			memoriaPrincipal[indiceP].append(pack)
		#Si esta llena
		else:
			#print ("Esta entrando al else que dice que esta llena")
			#Se habilita una nueva pagina
			pagNueva = habilitarPagina(memoriaPrincipal[indiceP][1])
			#Ver en que posicion de memoria local quedo, y luego ya se puede guardar
			indiceP = busquedaPaginaMemoriaPrincipal(pagNueva)
			#Se guarda
			memoriaPrincipal[indiceP].append(pack)
			numeroPag = pagNueva
	#Si no esta en memoria local
	else:
		#print("Entre al else")
		indMemSwap = busquedaPaginaSwap()
		#print("Indice swap:" + str(indMemSwap))
		pasarPaginaLocalADistribuida(indMemSwap)
		pasarPaginaDistribuidaALocal(indMemSwap,numP)
		paginaLlena = paginallenaMemoriaPrincipal(indMemSwap)
		#Si tiene espacio 
		if(paginaLlena == False):
			#Se guarda
			memoriaPrincipal[indMemSwap].append(pack)
		#Si esta llena
		else:
			#print ("Esta entrando al otro else en donde se dice que la pagina esta llena")
			pagNueva = habilitarPagina(memoriaPrincipal[indMemSwap][1])
			indMemSwap = busquedaPaginaMemoriaPrincipal(pagNueva)
			memoriaPrincipal[indMemSwap].append(pack)
			numeroPag = pagNueva
	return numeroPag
	
while(True):
	codigoLlamado = buzonLlamados.get()
	if(codigoLlamado == 0): #Llama a Habilitar pagina
		parametro = buzonParametros.get() #Saco parametros
		paginaHabilitada = habilitarPagina(parametro)
		buzonRetornos.put(paginaHabilitada) #Envio lo que me retorno la funcion
	elif(codigoLlamado == 1):#Llama a pedir pagina
		parametro = buzonParametros.get()
		paginaADevolver = pedirPagina(parametro)
		#print("BUZON RETORNO: ",paginaADevolver)
		buzonRetornos.put(paginaADevolver)
		
	elif(codigoLlamado == 2): #Llama a guardar 
		parametro1 = buzonParametros.get()
		parametro2 = buzonParametros.get()
		numPage = guardar(parametro1,parametro2)
		buzonRetornos.put(numPage)
	
		
			

	
			
			
			
			
		
	

