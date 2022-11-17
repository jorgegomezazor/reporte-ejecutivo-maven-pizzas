import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from PIL import Image
import os
def extract(): #importo los csv
    order_details = pd.read_csv('order_details.csv') #importo el csv de order_details
    orders = pd.read_csv('orders.csv') #importo el csv de orders
    pizza_types = pd.read_csv('pizza_types.csv',encoding='latin1') #importo el csv de pizza_types
    pizza = pd.read_csv('pizzas.csv') #importo el csv de pizzas
    return  order_details, orders, pizza_types, pizza
def transform(order_details, orders, pizza_types, pizz):
    pizza = {}
    fechas = []
    for i in range(len(pizza_types)):
        pizza[pizza_types['pizza_type_id'][i]] = pizza_types['ingredients'][i] #guardo los ingredientes en un diccionario
    for fecha in orders['date']:
        f = pd.to_datetime(fecha, errors='raise', dayfirst=True, yearfirst=False, utc=None, format='%d/%m/%Y', exact=True, unit=None, infer_datetime_format=False, origin='unix', cache=True) #convierto las fechas a datetime
        fechas.append(f) #guardo las fechas en una lista
    cant_pedidos = [[] for _ in range(53)] #creo una lista de listas para guardar la cantidad de pedidos por semana
    pedidos = [[] for _ in range(53)] #creo una lista de listas para guardar los pedidos por semana
    for pedido in range(len(fechas)):
        cant_pedidos[fechas[pedido].week-1].append(pedido+1) #guardo la cantidad de pedidos por semana
    for p in range(1,order_details['order_details_id'][len(order_details['order_details_id'])-1]-1): 
        for i in range(order_details['quantity'][p]):
            pedidos[fechas[order_details['order_id'][p]-1].week-1].append(order_details['pizza_id'][p]) #guardo los pedidos por semana teniendo en cuenta la cantidad de pizzas
    ingredientes_anuales = {}
    diccs = []
    for dic in range(53):
        diccs.append({}) #creo una lista de diccionarios para guardar los ingredientes por semana
    for i in range(len(pizza_types)):
        ingreds = pizza_types['ingredients'][i] #guardo los ingredientes en una variable
        ingreds = ingreds.split(', ') #separo los ingredientes
        for ingrediente in ingreds:
            ingredientes_anuales[ingrediente] = 0
            for i in range(len(diccs)):
                diccs[i][ingrediente] = 0 #guardo los ingredientes en los diccionarios
    for i in range(len(pedidos)):
        for p in pedidos[i]:
            ing = 0
            tamano = 0
            if p[-1] == 's': #guardo el tamaño de la pizza
                ing = 1 #si es s la pizza tiene 1 ingrediente de cada
                tamano = 2 
            elif p[-1] == 'm':
                ing = 2 #si es m la pizza tiene 2 ingredientes de cada
                tamano = 2
            elif p[-1] == 'l':
                if p[-2] == 'x':
                    if p[-3] == 'x':
                        ing = 5 #si es xxl la pizza tiene 5 ingredientes de cada
                        tamano = 4
                    else:
                        ing = 4 #si es xl la pizza tiene 4 ingredientes de cada
                        tamano = 3
                else:
                    ing = 3 #si es l la pizza tiene 3 ingredientes de cada
                    tamano = 2
            ings = pizza[p[:-tamano]].split(', ')
            for ingrediente in ings:
                ingredientes_anuales[ingrediente] += ing #guardo los ingredientes en el diccionario de ingredientes anuales
                diccs[i][ingrediente] += ing #guardo los ingredientes en los diccionarios de ingredientes por semana
    for i in range(len(diccs)):
        for j in diccs[i]:
            diccs[i][j] = int(np.ceil((diccs[i][j] + (ingredientes_anuales[j]/53))/2)) #aplico la predicción
    #pizzas mas pedidas
    pizzas = {}
    for i in range(len(pizz)):
        pizzas[pizz['pizza_id'][i]] = 0 #guardo las pizzas en un diccionario
    for i in range(len(pedidos)):
        for p in pedidos[i]:
            pizzas[p] += 1 #guardo las pizzas en el diccionario
    return diccs, ingredientes_anuales, cant_pedidos, pizzas
def load(diccs, ingredientes_anuales, cant_pedidos, pizzas):
    ingredientes_anuales =  sorted(ingredientes_anuales.items(), key=lambda x: x[1], reverse=True) #ordeno los ingredientes por cantidad de pedidos
    ing_ans = {}
    for ing in range(len(ingredientes_anuales)):
        ing_ans[ingredientes_anuales[ing][0]] = ingredientes_anuales[ing][1] #guardo los ingredientes anuales en un diccionario
    pizzas = sorted(pizzas.items(), key=lambda x: x[1], reverse=True)
    pizzas = pizzas[:10] #guardo las 10 pizzas mas pedidas
    pzs = {}
    for p in range(len(pizzas)):
        pzs[pizzas[p][0]] = pizzas[p][1]
    imagenes = []
    pdf = FPDF() #creo el pdf
    pdf.add_page()
    pdf.set_font('Arial', size = 25) #tamaño de la fuente
    pdf.cell(200, 10, txt = 'Maven Pizzas', ln = 1, align='C') #escribo el titulo del pdf
    pdf.cell(200, 10, txt = 'Reporte ejecutivo',ln = 2, align='C') 
    pdf.set_font('Arial', size = 15)
    pdf.cell(200, 10, txt = 'Jorge Gómez Azor',ln = 3,align='R') #escribo el nombre del autor
    pdf.image('maven_pizzas.png', x = 70, y = 70, w = 80, h = 50)
    for i in range(len(diccs)):
        plt.bar(diccs[i].keys(), diccs[i].values()) #grafico los diccionarios
        plt.xticks(rotation=90, fontsize=5)
        plt.title('Semana ' + str(i+1))
        plt.savefig('semana' + str(i+1) + '.png', bbox_inches='tight') #guardo los graficos
        imagenes.append('semana' + str(i+1) + '.png') 
        plt.clf() #limpio el grafico
    plt.bar(ing_ans.keys(), ing_ans.values()) #grafico los ingredientes anuales
    plt.xticks(rotation=90, fontsize=5)
    plt.title('Ingredientes anuales')
    plt.savefig('ingredientes_anuales.png', bbox_inches='tight')
    imagenes.append('ingredientes_anuales.png')
    plt.clf()
    plt.bar(pzs.keys(), pzs.values()) #grafico las pizzas mas pedidas
    plt.xticks(rotation=90, fontsize=5)
    plt.title('Pizzas mas pedidas')
    plt.savefig('pizzas_mas_pedidas.png', bbox_inches='tight')
    imagenes.append('pizzas_mas_pedidas.png')
    plt.clf()
    for i in range(len(cant_pedidos)): #escribo la cantidad de pedidos por semana
        plt.bar(i+1, len(cant_pedidos[i]))
    plt.title('Cantidad de pedidos por semana')
    plt.savefig('cantidad_pedidos.png', bbox_inches='tight')
    imagenes.append('cantidad_pedidos.png')
    plt.clf()
    for imagen in imagenes:
        pdf.add_page() #agrego una pagina
        pdf.image(imagen, x = 20, y = 60, w = 160, h = 100) #agrego las imagenes al pdf
    pdf.output("reporte_ejecutivo.pdf", "F") #guardo el pdf
if __name__ == '__main__':
    order_details, orders, pizza_types,pizza = extract()
    diccs, ingredientes_anuales, cant_pedidos, pizzas = transform(order_details, orders, pizza_types,pizza)
    load(diccs, ingredientes_anuales, cant_pedidos, pizzas)
    