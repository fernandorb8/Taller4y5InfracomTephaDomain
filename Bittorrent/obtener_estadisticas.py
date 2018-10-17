'''
Created on 15 oct 2018

@author: Fernando
'''

NUMCLIENTES = [2,3,4,5,6,10,23]
MAXNUMCLIENTES = NUMCLIENTES[len(NUMCLIENTES)-1]
TORFILES = [250,500]
NUMITERS = [1,2,3,4,5]
CAMPOS = ["Paquetes enviados promedio", "Paquetes recibidos promedio", "Tiempo descarga promedio (s)"]
IPMAP = {"172.24.101.207":1,
        "172.24.101.208":2,
        "172.24.101.209":3,
        "172.24.101.210":4,
        "172.24.101.211":5,
        "172.24.101.212":6,
        "172.24.101.213":7,
        "172.24.101.214":8,
        "172.24.101.215":9,
        "172.24.101.216":10}

estadisticas = []
#Para cada una de las cantidades de clientes.
for posnumcliente, numcliente in enumerate(NUMCLIENTES):
    estadisticas.append([])
    #Por cada archivo que se transfiere.
    for postorfile, torfile in enumerate(TORFILES):
        estadisticas[posnumcliente].append([])
        #Para cada cliente.
        for i in range(1, numcliente +1):
            estadisticas[posnumcliente][postorfile].append([0,0,0])    
            #Para cada iteración.      
            for positeri, iteri in enumerate(NUMITERS):
                folder_name = "_".join(["Clients", str(numcliente), str(iteri), str(torfile)]) + "/"
                file_name = "client_" + str(i) + ".log"
                relative_file_name = folder_name + file_name
                
                #Campos ["Paquetes enviados", "Paquetes recibidos", "Tiempo descarga"]
                estadisticas_iter =[0,0,0]
                
                try:
                    f = open(relative_file_name, "r")
                    line = f.readline()
                    while not line == "":
                        line_1 = line
                        line_2 = f.readline()
                        if line_2 == "":
                            line_3 = line_2
                            line = ""
                        else:
                            #Agregar estadísticas de la iteración.
                            line_3 = f.readline()
                            line = f.readline()
                            if "se envia la pieza" in line_2:
                                estadisticas_iter[0] = estadisticas_iter[0] + 1
                            elif "se recibe la pieza" in line_2:
                                estadisticas_iter[1] = estadisticas_iter[1] + 1
                            elif "el tiempo de descarga fue" in line_2:
                                line_arr = line_2.split(";")
                                estadisticas_iter[2] = float(line_arr[1])
                    
                    #Agregar estadísticas de todas las iteraciones.            
                    estadisticas[posnumcliente][postorfile][i-1][0] = estadisticas[posnumcliente][postorfile][i-1][0] \
                    + estadisticas_iter[0]
                    
                    estadisticas[posnumcliente][postorfile][i-1][1] = estadisticas[posnumcliente][postorfile][i-1][1] \
                    + estadisticas_iter[1]
                    
                    estadisticas[posnumcliente][postorfile][i-1][2] = estadisticas[posnumcliente][postorfile][i-1][2] \
                    + estadisticas_iter[2]
                    
                    #Promediar en la última iteración.
                    if positeri == (len(NUMITERS) -1) :
                        estadisticas[posnumcliente][postorfile][i-1][0] = estadisticas[posnumcliente][postorfile][i-1][0] \
                        / len(NUMITERS)
                        estadisticas[posnumcliente][postorfile][i-1][1] = estadisticas[posnumcliente][postorfile][i-1][1] \
                        / len(NUMITERS)
                        estadisticas[posnumcliente][postorfile][i-1][2] = estadisticas[posnumcliente][postorfile][i-1][2] \
                        / len(NUMITERS)
                finally:        
                    f.close()
                    
#Imprimir resultados. 
with open("resultados.txt","w") as f:                
    for postorfile in range(len(TORFILES)):  
        f.write("Archivo de "+str(TORFILES[postorfile])+"MB\n")      
        for poscampo in range(len(CAMPOS)):
            f.write(CAMPOS[poscampo]+"\n")
            for numcliente in NUMCLIENTES:
                f.write("\t"+str(numcliente))
            f.write("\n")
            for numcliente in range(MAXNUMCLIENTES):
                f.write("Cliente "+str(numcliente+1))
                for posnumclientesi, numclientesi in enumerate(NUMCLIENTES):
                    if numcliente < numclientesi:
                        f.write("\t"+str(estadisticas[posnumclientesi][postorfile][numcliente][poscampo]))
                    else:
                        f.write("\t")
                f.write("\n")