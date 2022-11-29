import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
def extract(): # Función que extrae los datos
    order_details = pd.read_csv('order_details.csv', encoding='latin1', sep=';') # Leo el archivo order_details.csv
    orders = pd.read_csv('orders.csv', encoding='latin1',sep=';') # Leo el archivo orders.csv
    pizza_types = pd.read_csv('pizza_types.csv',encoding='latin1',sep=',') # Leo el archivo pizza_types.csv
    pizza = pd.read_csv('pizzas.csv',encoding='latin1',sep=',') # Leo el archivo pizza.csv
    return  order_details, orders, pizza_types,pizza
def limpiar_datos(order_details, orders):
    ord = pd.merge(order_details, orders, on='order_id') # Hago un merge de los dataframes order_details y orders
    #quito columna time
    ord = ord.drop(columns=['time'])
    ord = ord.dropna() # Elimino los nulls
    pd.set_option('mode.chained_assignment', None) # Deshabilito el warning SettingWithCopyWarning
    for i in range(1,len(ord['pizza_id'])):
        try:
            m = ord['pizza_id'][i]
            palabra = ''
            for l in range(len(m)):
                if m[l] =='@':
                    palabra += 'a' # Reemplazo las @ por a
                elif m[l] == '0':
                    palabra += 'o' # Reemplazo los 0 por o
                elif m[l] == '-':
                    palabra += '_' # Reemplazo los - por _
                elif m[l] == ' ':
                    palabra += '_' # Reemplazo los espacios por _
                elif m[l] == '3':
                    palabra += 'e' # Reemplazo los 3 por e
                else:
                    palabra += m[l] # Si no es ninguna de las anteriores, la agrego tal cual
            ord['pizza_id'][i] = ord['pizza_id'][i].replace(m,palabra)  # Reemplazo la palabra por la nueva
        except:
            #elimino la fila que no se pudo limpiar
            try:
                ord = ord.drop(i)
            except:
                pass
    order_details_2 = ord[['order_details_id','order_id', 'pizza_id', 'quantity']] # Creo un nuevo dataframe con las columnas que me interesan
    order_details_2.to_csv('order_details_2.csv', index=False) # Guardo el dataframe en un archivo csv
    orders_2 = ord[['order_id','date']] # Creo un nuevo dataframe con las columnas que me interesan
    orders_2.to_csv('orders_2.csv', index=False) # Guardo el dataframe en un archivo csv
    return order_details_2, orders_2
def transform(order_details, orders, pizza_types, pizz):
    pizza = {}
    fechas = []
    for i in range(len(pizza_types)):
        pizza[pizza_types['pizza_type_id'][i]] = pizza_types['ingredients'][i] #guardo los ingredientes en un diccionario
    for fecha in orders['date']:
        try: 
            f = pd.to_datetime(float(fecha)+3600, unit='s') #convierto la fecha a datetime
        except:
            f = pd.to_datetime(fecha) # Convierto la fecha a datetime
        fechas.append(f) #guardo las fechas en una lista
    cant_pedidos = [[] for _ in range(53)] #creo una lista de listas para guardar la cantidad de pedidos por semana
    pedidos = [[] for _ in range(53)] #creo una lista de listas para guardar los pedidos por semana
    for pedido in range(len(fechas)):
        # print(fechas[pedido])
        cant_pedidos[fechas[pedido].week-1].append(pedido+1) #guardo la cantidad de pedidos por semana
    bucle = 0
    for p in range(2,len(order_details['order_details_id'])): 
        try:
            bucle = abs(order_details['quantity'][p])
        except:
            try:
                if order_details['quantity'][p] == 'One' or order_details['quantity'][p] == 'one':
                    bucle = 1
                elif order_details['quantity'][p] == 'Two' or order_details['quantity'][p] == 'two':
                    bucle = 2
            except:
                pass
        try:
            for i in range(bucle):
                pedidos[fechas[abs(order_details['order_id'][p]-1)].week-1].append(order_details['pizza_id'][p]) #guardo los pedidos por semana teniendo en cuenta la cantidad de pizzas
        except:
            pass
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
    return diccs, ingredientes_anuales, cant_pedidos, pizzas, pedidos
def load(diccs, ingredientes_anuales, cant_pedidos, pizzas,pedidos,piz):
    ingredientes_anuales =  sorted(ingredientes_anuales.items(), key=lambda x: x[1], reverse=True) #ordeno los ingredientes por cantidad de pedidos
    ing_ans = {}
    for ing in range(len(ingredientes_anuales)):
        ing_ans[ingredientes_anuales[ing][0]] = ingredientes_anuales[ing][1] #guardo los ingredientes anuales en un diccionario
    pizzas = sorted(pizzas.items(), key=lambda x: x[1], reverse=True)
    pizzas = pizzas[:10] #guardo las 10 pizzas mas pedidas
    pzs = {}
    for p in range(len(pizzas)):
        pzs[pizzas[p][0]] = pizzas[p][1]
    ingresos = 0
    for i in range(len(pedidos)):
        for p in pedidos[i]:
            ingresos += piz['price'][piz['pizza_id'] == p].values[0] #calculo los ingresos
    imagenes = []
    pdf = FPDF() #creo el pdf
    pdf.add_page()
    pdf.set_font('Arial', size = 25) #tamaño de la fuente
    pdf.cell(200, 10, txt = 'Maven Pizzas', ln = 1, align='C') #escribo el titulo del pdf
    pdf.cell(200, 10, txt = 'Reporte ejecutivo',ln = 2, align='C') 
    pdf.set_font('Arial', size = 15)
    pdf.cell(200, 10, txt = 'Jorge Gómez Azor',ln = 3,align='R') #escribo el nombre del autor
    pdf.cell(200,10,txt='Ingresos anuales: ' + str(int(ingresos)) + ' euros',ln = 20,align='C') #escribo los ingresos anuales
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
    pdf.output("reporte_ejecutivo.pdf") #guardo el pdf
if __name__ == '__main__':
    order_details, orders, pizza_types,pizza = extract()
    order_details, orders = limpiar_datos(order_details,orders)
    diccs, ingredientes_anuales, cant_pedidos, pizzas, pedidos = transform(order_details, orders, pizza_types,pizza)
    load(diccs, ingredientes_anuales, cant_pedidos, pizzas, pedidos, pizza)
