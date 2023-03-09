import numpy as np
import pandas as pd
import pymysql
import PySimpleGUI as sg
import unidecode

print("Importado con éxito")




# Selección de procedencia y host de almacenamiento

# Creación de ventanas para input de datos


layout = [  [sg.Text('Datos de conexión a la base')],
            [sg.Text('Host:'), sg.InputText()],
            [sg.Text('User:'), sg.InputText()],
            [sg.Text('Password:'), sg.InputText()],
            [sg.Text('Database:'), sg.InputText()],
            [sg.Text('Port:'), sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')] ]


# Create the Window
window = sg.Window('Conexión de SQL', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel' or 'Ok': # if user closes window or clicks cancel
        print('Host ', values[0])
        print('User', values[1])
        print('Password', values[2])
        print('Database', values[3])
        print('Port', values[4])
        break
    
window.close()

host = values[0]
user = values[1]
passwd = values[2]
db = values[3]
port = values[4]



event, values = sg.Window('Procedencia', [[sg.Text('Seleccione la procedencia->'), sg.Listbox(["TODOS...", "BUENOS AIRES", "CATAMARCA", "CHACO", "CHUBUT", "CIUDAD AUTÓNOMA DE BUENOS AIRES", "CÓRDOBA", "CORRIENTES", "ENTRE RÍOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUÉN", "RÍO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMÁN"], size=(20, 3), key='LB')],
    [sg.Button('Ok'), sg.Button('Cancelar')]]).read(close=True)

if event == 'Ok':
    sg.popup(f'Elegiste {values["LB"][0]}')
else:
    sg.popup_cancel('El usuario no eligió')
    quit()

proc = values["LB"][0]
procedencia = unidecode.unidecode(values["LB"][0]).lower()


# Chequeo de conexión a la base


try:
    connection = pymysql.connect(host=host,user=user, passwd=passwd, db=db, port=int(port))
    cursor = connection.cursor()
    connection.commit()
    connection.close()
    print("La conexión a SQL está correctamente configurada.")
except:
    sg.popup(f'La conexión a la base dió un error. Compruebe si en MySQL tiene\nconfigurado correctamente el acceso a la base.')
    quit()



try:
    connection = pymysql.connect(host=host,user=user, passwd=passwd, db=db, port=int(port))
    cursor = connection.cursor()
    data = pd.read_sql_query (f"SELECT * FROM {procedencia}", connection)
    connection.commit()
    connection.close()
    print("La base se ha cargado correctamente")
except:
    layout = [[sg.Text('No se encontró la base.\nActualice con el código data-update.py.')]]

    # Create the Window
    window = sg.Window("Error", layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
    quit()



data = data[ data['FECHA CONCERTACION'].str.contains("CÓRDOBA")==False ]

data['AÑO OP'] = data['FECHA OPERACION'].str.slice(start=6, stop = 10).astype(float)
data['MES OP'] = data['FECHA OPERACION'].str.slice(start=3, stop = 5).astype(float)
data['DIA OP'] = data['FECHA OPERACION'].str.slice(start=0, stop = 2).astype(float)


    # Fecha para carga de datos
    
fecha_max = data.loc[data['AÑO OP'] == max(data['AÑO OP'])]
fecha_max = fecha_max.loc[fecha_max['MES OP']== max(fecha_max['MES OP'])]
fecha_max = fecha_max.loc[fecha_max['DIA OP']== max(fecha_max['DIA OP'])]
fecha_max = fecha_max['FECHA OPERACION'].values
fecha_max

layout = [[sg.Text(f"Última fecha el {fecha_max[0][0:10]}")]]

# Create the Window
window = sg.Window("Info", layout)
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break



# Reemplazamos todos los "A Fijar" diferentes por un sólo tipo de "A Fijar":

data.loc[data.PRECIO.isin(['Fijar Precio/Prec. Cam.','Fijar Precio/Mercado Comprador',
'Fijar Precio/Otros', 'Fijar Precio/M. T. País', 'Fijar Precio','Fijar Precio/Fas teórico','Fijar Precio/PR R. Conj.',
 'Fijar Precio/M. T. Ext.']),"PRECIO"] = "A Fijar"


# Cambiamos la condición de pago a "A Plazo" y a "Contraentrega":
data.loc[~data["CONDICION PAGO"].isin(['A plazo']),"CONDICION PAGO"] = "Contraentrega"




# La cosecha no se encuentra armonizada, muchos agregan sólo el año de cosecha, mientras
# que otros escriben los dos años de la campaña. Por ejemplo, algunos escriben "COSECHA 2021" y otros "COSECHA 20/21",
# que es escencialmente lo mismo. Normalizo eso:

data = data[data['COSECHA'].str.contains('SI')==False]
data = data[data['COSECHA'].str.contains('an')==False]

#Elimino los datos donde existe un error en la COSECHA, y se la ha cargado como "0":
data[data.COSECHA==0].count()
data = data[data.COSECHA!=0]

data.COSECHA = data.COSECHA.map(lambda x: x if x.find("/")>=0 else "COSECHA "+str(int(x[-2:])-1).zfill(2)+"/"+x[-2:].zfill(2))
data.COSECHA = data.COSECHA.map(lambda x: x.replace("-1", "99"))
data.COSECHA.unique()



# Selección de cosecha


event, values = sg.Window('Cosecha', [[sg.Text('Seleccione la cosecha->'), sg.Listbox(data.COSECHA.unique(), size=(20, 3), key='LB')],
    [sg.Button('Ok'), sg.Button('Cancelar')]]).read(close=True)

if event == 'Ok':
    sg.popup(f'Elegiste {values["LB"][0]}')
else:
    sg.popup_cancel('El usuario no eligió')
    quit()

cosecha = values["LB"][0]



# Selección de producto

event, values = sg.Window('Producto', [[sg.Text('Seleccione el producto->'), sg.Listbox(data['PRODUCTO'].unique(), size=(20, 3), key='LB')],
    [sg.Button('Ok'), sg.Button('Cancelar')]]).read(close=True)

if event == 'Ok':
    sg.popup(f'Elegiste {values["LB"][0]}')
else:
    sg.popup_cancel('El usuario no eligió')
    quit()

producto = values["LB"][0]


campaña_filtrada = data[data['COSECHA'].str.contains(f'{cosecha}')]

producto_filtrado = campaña_filtrada[campaña_filtrada['PRODUCTO'].str.contains(f'{producto}')]


# All the stuff inside your window.
layout = [  [sg.Text('Haga click derecho en su carpeta de almacenamiento,\nluego dentro de propiedades busque la ubicación y copie y pegue la ruta.')],
            [sg.Text('Path a la carpeta:'), sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')] ]


# Create the Window
window = sg.Window('Carpeta de almacenamiento', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel' or 'Ok': # if user closes window or clicks cancel
        print('Path: ', values[0])
        break
    
window.close()


path = values[0]
folder_path = fr'{path}'

producto_filtrado.to_excel(f'{folder_path}\{producto}_{cosecha.replace(" ", "").replace("/", "_")}_{procedencia}.xlsx', index= False)


layout = [[sg.Text(f"Archivo almacenado en {folder_path}")]]

# Create the Window
window = sg.Window("Info", layout)
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

exit()