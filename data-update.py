import numpy as np
import pandas as pd
import datetime as dt
import os
import datetime
import pymysql
import time
import datetime
from datetime import date
import glob
import shutil
import PySimpleGUI as sg
import unidecode

# Selenium libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


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



# All the stuff inside your window.
layout = [  [sg.Text('Haga click derecho en su carpeta de descargas,\nluego dentro de propiedades busque la ubicación y copie y pegue la ruta.')],
            [sg.Text('Path a la carpeta:'), sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')] ]


# Create the Window
window = sg.Window('Carpeta de descargas', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel' or 'Ok': # if user closes window or clicks cancel
        print('Path: ', values[0])
        break
    
window.close()


path = values[0]


# Carpeta para almacenar archivos temporales


# All the stuff inside your window.
layout = [  [sg.Text('Crear una carpeta de archivos temporales, \nluego copie y pegue la ruta de acceso a la carpeta.\nDebe ser una carpeta vacía.')],
            [sg.Text('Path a la carpeta:'), sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Carpeta de archivos temporales', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel' or 'Ok': # if user closes window or clicks cancel
        print('Path: ', values[0])
        break
    
window.close()


path_archivos = values[0]



# Borramos los archivos de sio-granos de las descargas para que no haya errores



folder_path = fr'{path}'
file_type = r'\*csv'
files = glob.glob(folder_path + file_type)
max_file = max(files, key=os.path.getctime)


while "operaciones_informadas" in max_file:
    os.remove(max_file)

    folder_path = fr'{path}'
    file_type = r'\*csv'
    files = glob.glob(folder_path + file_type)
    max_file = max(files, key=os.path.getctime)


# Borramos los archivos del directorio en el que descargaremos los datos que faltan

directory = fr'{path_archivos}/*'
files = glob.glob(directory)

for file in files:
    if os.path.exists(file):
        os.remove(file)


print("Directorios de trabajo limpios.")

# Selección de procedencia 



event, values = sg.Window('Procedencia', [[sg.Text('Seleccione la procedencia->'), sg.Listbox(["TODOS...", "BUENOS AIRES", "CATAMARCA", "CHACO", "CHUBUT", "CIUDAD AUTÓNOMA DE BUENOS AIRES", "CÓRDOBA", "CORRIENTES", "ENTRE RÍOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUÉN", "RÍO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMÁN"], size=(20, 3), key='LB')],
    [sg.Button('Ok'), sg.Button('Cancelar')]]).read(close=True)

if event == 'Ok':
    sg.popup(f'Elegiste {values["LB"][0]}')
else:
    sg.popup_cancel('El usuario no eligió')
    quit()

proc = values["LB"][0]
procedencia = unidecode.unidecode(values["LB"][0]).lower().replace(" ", "_")

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



# Intentamos conectarnos a la base y buscar la última fecha, caso contrario se descargará todo el historial de datos de sio-granos

try:
    connection = pymysql.connect(host=host,user=user, passwd=passwd, db=db, port=int(port))
    cursor = connection.cursor()
    base_de_datos = pd.read_sql_query (f"SELECT * FROM {procedencia}", connection)
    connection.commit()
    connection.close()
    
    
    # Columnas con año, mes, día

    base_de_datos = base_de_datos[ base_de_datos['FECHA CONCERTACION'].str.contains("CÓRDOBA")==False ]
    base_de_datos = base_de_datos[base_de_datos['FECHA OPERACION'].str.match("[0-9]{2}/[0-9]{2}/[0-9]{4}")]

    base_de_datos['AÑO OP'] = base_de_datos['FECHA OPERACION'].str.slice(start=6, stop = 10).astype(float)
    base_de_datos['MES OP'] = base_de_datos['FECHA OPERACION'].str.slice(start=3, stop = 5).astype(float)
    base_de_datos['DIA OP'] = base_de_datos['FECHA OPERACION'].str.slice(start=0, stop = 2).astype(float)


    # Fecha para carga de datos
    
    fecha_max = base_de_datos.loc[base_de_datos['AÑO OP'] == max(base_de_datos['AÑO OP'])]
    fecha_max = fecha_max.loc[fecha_max['MES OP']== max(fecha_max['MES OP'])]
    fecha_max = fecha_max.loc[fecha_max['DIA OP']== max(fecha_max['DIA OP'])]
    fecha_max = fecha_max['FECHA OPERACION'].values
    fecha_max
    print(f"Última fecha el {fecha_max[0]}")
except:
    print("No se encontró la base, se procede a cargarla desde cero.")
    fecha_max = np.array(['01/01/2013 02:04:21 p.m.'], dtype=object)




old_max_day = int(fecha_max[0][0:2])
old_max_month = int(fecha_max[0][3:5])-1
old_max_year = int(fecha_max[0][6:10])


# Loop para descargar datos si hay una diferencia de más de 180 días

while (datetime.date.today() - datetime.date(old_max_year, old_max_month+1, old_max_day)).days >= 180:
    print("Los días a cargar son más de 180. Se carga en intervalos de 180 días, este es el límite de sio granos.")
    today_day = (datetime.date(old_max_year, old_max_month+1, old_max_day) + dt.timedelta(days=180)).day
    today_month = (datetime.date(old_max_year, old_max_month+1, old_max_day) + dt.timedelta(days=180)).month
    today_year = (datetime.date(old_max_year, old_max_month+1, old_max_day) + dt.timedelta(days=180)).year

    old_max_day = old_max_day+1
    old_max_month = old_max_month
    old_max_year = old_max_year

    if today_day==1:                  # El día corriente no está disponible para descargar, hay que
        today_day = 28                       # usar el día anterior
        if today_month==1:
            today_month = 11
            today_year = date.today().year-1
        else:
            today_month = date.today().month-2
    else:    
        today_day = today_day-1
        today_month = today_month-1      # Enero lo cuentan como 0, y de ahí empiezan a sumar...
        today_year = today_year



    if today_day == 28 and today_month == 1:
        today_day = 27
    else:
        today_day = today_day

    print("Descargando fechas: ", old_max_day, old_max_month+1, old_max_year, " --- ", today_day,today_month+1,today_year)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.siogranos.com.ar/Consulta_publica/operaciones_informadas_exportar.aspx")
    driver.maximize_window()
    time.sleep(3)

    # Fecha de Inicio:
    fecha_inicio = driver.find_element(By.NAME,"txtFechaOperacionDesde").click()
    time.sleep(1)
    # Mes:
    select_mes_inicio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-month"))
    select_mes_inicio.select_by_value(str(old_max_month))
    time.sleep(1)
    # Año:
    select_anio_inicio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-year"))
    select_anio_inicio.select_by_value(str(old_max_year))
    time.sleep(1)
    # Dia:
    day_inicio = driver.find_element(By.XPATH,"//a[@class='ui-state-default' and text()="+str(old_max_day)+"]")
    day_inicio.click()


    # Fecha de hoy:
    fecha_hoy = driver.find_element(By.NAME,"txtFechaOperacionHasta").click()
    time.sleep(1)
    # Mes:
    select_mes = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-month"))
    select_mes.select_by_value(str(today_month))
    time.sleep(1)
    # Año:
    select_anio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-year"))
    select_anio.select_by_value(str(today_year))
    time.sleep(1)
    # Dia:
    day = driver.find_element(By.XPATH,"//a[@class='ui-state-default' and text()="+str(today_day)+"]")
    day.click()

    # Procedencia:
    sel = Select(driver.find_element(By.ID, "ddlProvincia"))
    time.sleep(3)
    try:
        sel.select_by_visible_text(proc)
    except:
        time.sleep(10)
        sel.select_by_visible_text(proc)


    csv = driver.find_element(By.ID,"btn_generar_csv")
    csv.click()
    time.sleep(15)

    # Buscamos el último archivo descargado
    folder_path = fr'{path}'
    file_type = r'\*csv'
    files = glob.glob(folder_path + file_type)
    max_file = max(files, key=os.path.getctime)



    # Si el archivo no llegó a descargarse, puede ser por demoras en el internet o porque no están los datos
    
    if "operaciones_informadas" in max_file:
        print("Se encontró el archivo en descargas.")
        shutil.move(max_file, f'{path_archivos}/{old_max_day,old_max_month+1,old_max_year}-{today_day,today_month+1,today_year}.csv')
        print("Archivo movido a la carpeta de trabajo.")
    else:
        print("No se encontró el archivo en descargas.")

        event, values = sg.Window('Error', [[sg.Text('No se encontró el archivo descargado. Ver en pestaña de Chrome sio-granos.\n Si no habían datos para la fecha seleccionada, presione no hay datos.')],[sg.Button('No hay datos'), sg.Button('Página caída'), sg.Button('Se está descargando')]]).read(close=True)

        while event == "Página caída":
            sg.popup('Se intentará nuevamente')
            print("Descargando fechas: ", old_max_day, old_max_month+1, old_max_year, " --- ", today_day,today_month+1,today_year)
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get("https://www.siogranos.com.ar/Consulta_publica/operaciones_informadas_exportar.aspx")
            driver.maximize_window()
            time.sleep(3)

            # Fecha de Inicio:
            fecha_inicio = driver.find_element(By.NAME,"txtFechaOperacionDesde").click()
            time.sleep(1)
            # Mes:
            select_mes_inicio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-month"))
            select_mes_inicio.select_by_value(str(old_max_month))
            time.sleep(1)
            # Año:
            select_anio_inicio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-year"))
            select_anio_inicio.select_by_value(str(old_max_year))
            time.sleep(1)
            # Dia:
            day_inicio = driver.find_element(By.XPATH,"//a[@class='ui-state-default' and text()="+str(old_max_day)+"]")
            day_inicio.click()


            # Fecha de hoy:
            fecha_hoy = driver.find_element(By.NAME,"txtFechaOperacionHasta").click()
            time.sleep(1)
            # Mes:
            select_mes = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-month"))
            select_mes.select_by_value(str(today_month))
            time.sleep(1)
            # Año:
            select_anio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-year"))
            select_anio.select_by_value(str(today_year))
            time.sleep(1)
            # Dia:
            day = driver.find_element(By.XPATH,"//a[@class='ui-state-default' and text()="+str(today_day)+"]")
            day.click()

            # Procedencia:
            sel = Select(driver.find_element(By.ID, "ddlProvincia"))
            time.sleep(3)
            try:
                sel.select_by_visible_text(proc)
            except:
                time.sleep(10)
                sel.select_by_visible_text(proc)


            csv = driver.find_element(By.ID,"btn_generar_csv")
            csv.click()
            time.sleep(15)

            # Buscamos el último archivo descargado
            folder_path = fr'{path}'
            file_type = r'\*csv'
            files = glob.glob(folder_path + file_type)
            max_file = max(files, key=os.path.getctime)

            if "operaciones_informadas" in max_file:
                    print("Se encontró el archivo en descargas.")
                    shutil.move(max_file, f'{path_archivos}/{old_max_day,old_max_month+1,old_max_year}-{today_day,today_month+1,today_year}.csv')
                    print("Archivo movido a la carpeta de trabajo.")
            else:
                print("No se encontró el archivo en descargas.")

            event, values = sg.Window('Error', [[sg.Text('No se encontró el archivo descargado. Ver en pestaña de Chrome sio-granos.\n Si no habían datos para la fecha seleccionada, presione no hay datos.')],
                                                    [sg.Button('No hay datos'), sg.Button('Página caída'), sg.Button('Se está descargando')]]).read(close=True)




        if event == 'No hay datos':
            sg.popup(f'No habían datos para la fecha seleccionada, se continúa con la descarga.')
            print("No hay datos para las fechas seleccionadas.")
        else:
            sg.popup('Espere...')
            print("En espera de descarga...")
            time.sleep(30)
            # Buscamos el último archivo descargado
            folder_path = fr'{path}'
            file_type = r'\*csv'
            files = glob.glob(folder_path + file_type)
            max_file = max(files, key=os.path.getctime)
            if "operaciones_informadas" in max_file:
                shutil.move(max_file, f'{path_archivos}/{old_max_day,old_max_month+1,old_max_year}-{today_day,today_month+1,today_year}.csv')
            else:
                
                event, values = sg.Window('Error', [[sg.Text('No se encontró el archivo descargado. ¿Habían datos para la fecha seleccionada? (Ver en pestaña de Chrome sio-granos)')],[sg.Button('No hay datos'), sg.Button('Se está descargando')]]).read(close=True)

                if event == 'No hay datos':
                    sg.popup(f'No habían datos para la fecha seleccionada, se continúa con la descarga.')
                else:
                    sg.popup_cancel('Hubo un error. Intente correr el programa nuevamente. Asegúrese de contar con una buena conexión a internet.')
                    quit()

    print("----------------------------------------------------")


    old_max_year = today_year
    old_max_month = today_month
    old_max_day = today_day

print("Loop de descarga de datos de hace más de 180 días finalizado.")

if (datetime.date.today() - datetime.date(old_max_year, old_max_month+1, old_max_day)).days <= 1:
    # All the stuff inside your window.
    layout = [[sg.Text('Los datos se encuentran actualizados.')]]

    # Create the Window
    window = sg.Window("Carga completa", layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
    quit()


try:
    # Creo un Dataframe vacio y una lista con los archivos que se encuentran en el directorio, en caso de querer 
    # agregar un período de tiempo muy largo:

    data = pd.DataFrame()
    fichero = os.listdir(f'{path_archivos}/')

    #Creo un "for" que me lea todos los archivos y me vaya apendizando las bases a nuestro Dataframe "data":

    for base in fichero:    # Compila todos los archivos de la carpeta
            apendice = pd.read_csv(f'{path_archivos}/{base}', index_col=None, sep=";",encoding='utf-16le', header=0,error_bad_lines=False,warn_bad_lines=True)
            data = pd.concat([data,apendice])


    # CARGA A SQL

    baseSQL = pd.DataFrame()

    for i in data.columns:
        baseSQL[i] = data[i].astype(str)


    # Busco los nombres de columnas y paso el tipo de dato del dataframe a uno compatible con SQL:    
        
    def getColumnDtypes(dataTypes):
        dataList = []
        for x in dataTypes:
            if(x == 'int64'):
                dataList.append('int')
            elif (x == 'float64'):
                dataList.append('float')
            elif (x == 'bool'):
                dataList.append('boolean')
            else:
                dataList.append('varchar(50)')
        return dataList

    columnas_nombres = list(baseSQL.columns.values)
    columnas_tipo_de_datos = getColumnDtypes(baseSQL.dtypes)





    # Defino el statement para crear la tabla:
    crear_tabla_statement = f'CREATE TABLE IF NOT EXISTS {procedencia} ('
    for i in range(len(columnas_tipo_de_datos)):
        crear_tabla_statement = crear_tabla_statement +"\n`" + columnas_nombres[i] +  "` " + columnas_tipo_de_datos[i] + ', '
    crear_tabla_statement = crear_tabla_statement[:-2] + ');'
        
        # Me conecto a la base

    connection = pymysql.connect(host=host,user=user, passwd=passwd, db=db, port=int(port))
    cursor = connection.cursor()

        # Creo la tabla:
    try: 
        cursor.execute(crear_tabla_statement)
    except:
        print("La tabla ya existe, se va a proceder a cargar los datos.")


        # Preparo la inserción de datos:
    cols = "`,`".join([str(i) for i in baseSQL.columns.tolist()])

    for i,row in baseSQL.iterrows():
        sql = f"INSERT INTO {procedencia} (`" + cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
        cursor.execute(sql, tuple(row))
except:
    print("La carga de datos es menor a 180 días")


connection.commit()
connection.close()
print("Se cargaron los datos de más de 180 días de antigüedad")


connection = pymysql.connect(host=host,user=user, passwd=passwd, db=db, port=int(port))
cursor = connection.cursor()
base_de_datos = pd.read_sql_query (f"SELECT * FROM {procedencia}", connection)
connection.commit()
connection.close()
    
    
# Columnas con año, mes, día

old_max_day = old_max_day+1
old_max_month = old_max_month
old_max_year = old_max_year

if date.today().day==1:                  # El día corriente no está disponible para descargar, hay que
    today_day = 28                       # usar el día anterior
    if date.today().month==1:
        today_month = 11
        today_year = date.today().year-1
    else:
        today_month = date.today().month-2
else:    
        today_day = date.today().day-1
        today_month = date.today().month-1      # Enero lo cuentan como 0, y de ahí empiezan a sumar...
        today_year = date.today().year


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.siogranos.com.ar/Consulta_publica/operaciones_informadas_exportar.aspx")
driver.maximize_window()
time.sleep(3)

# Fecha de Inicio:
fecha_inicio = driver.find_element(By.NAME,"txtFechaOperacionDesde").click()
time.sleep(1)
# Mes:
select_mes_inicio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-month"))
select_mes_inicio.select_by_value(str(old_max_month))
time.sleep(1)
# Año:
select_anio_inicio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-year"))
select_anio_inicio.select_by_value(str(old_max_year))
time.sleep(1)
# Dia:
day_inicio = driver.find_element(By.XPATH,"//a[@class='ui-state-default' and text()="+str(old_max_day)+"]")
day_inicio.click()


# Fecha de hoy:
fecha_hoy = driver.find_element(By.NAME,"txtFechaOperacionHasta").click()
time.sleep(1)
# Mes:
select_mes = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-month"))
select_mes.select_by_value(str(today_month))
time.sleep(1)
# Año:
select_anio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-year"))
select_anio.select_by_value(str(today_year))
time.sleep(1)
# Dia:
day = driver.find_element(By.XPATH,"//a[@class='ui-state-default' and text()="+str(today_day)+"]")
day.click()

# Procedencia:
sel = Select(driver.find_element(By.ID, "ddlProvincia"))
time.sleep(3)
try:
    sel.select_by_visible_text(proc)
except:
    time.sleep(10)
    sel.select_by_visible_text(proc)


csv = driver.find_element(By.ID,"btn_generar_csv")
csv.click()
time.sleep(30)

# Borramos los archivos del directorio en el que descargaremos los datos que faltan

directory = fr'{path_archivos}/*'
files = glob.glob(directory)

for file in files:
    if os.path.exists(file):
        os.remove(file)


# Buscamos el último archivo descargado
folder_path = fr'{path}'
file_type = r'\*csv'
files = glob.glob(folder_path + file_type)
max_file = max(files, key=os.path.getctime)







if "operaciones_informadas" in max_file:
    shutil.move(max_file, fr'{path_archivos}')
else:
    event, values = sg.Window('Error', [[sg.Text('No se encontró el archivo descargado. Ver en pestaña de Chrome sio-granos.\n Si no habían datos para la fecha seleccionada, presione no hay datos.\n Si hay problemas de internet o se cayó la página, puede descargar manualmente los datos de\n la fecha seleccionada (ver en terminal) y luego presionar "No hay datos", o cancelar e intentar nuevamente.')],[sg.Button('No hay datos'), sg.Button('Página caída'), sg.Button('Se está descargando')]]).read(close=True)

    while event == "Página caída":
            sg.popup('Se intentará nuevamente')
            print("Descargando fechas: ", old_max_day, old_max_month+1, old_max_year, " --- ", today_day,today_month+1,today_year)
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get("https://www.siogranos.com.ar/Consulta_publica/operaciones_informadas_exportar.aspx")
            driver.maximize_window()
            time.sleep(3)

            # Fecha de Inicio:
            fecha_inicio = driver.find_element(By.NAME,"txtFechaOperacionDesde").click()
            time.sleep(1)
            # Mes:
            select_mes_inicio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-month"))
            select_mes_inicio.select_by_value(str(old_max_month))
            time.sleep(1)
            # Año:
            select_anio_inicio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-year"))
            select_anio_inicio.select_by_value(str(old_max_year))
            time.sleep(1)
            # Dia:
            day_inicio = driver.find_element(By.XPATH,"//a[@class='ui-state-default' and text()="+str(old_max_day)+"]")
            day_inicio.click()


            # Fecha de hoy:
            fecha_hoy = driver.find_element(By.NAME,"txtFechaOperacionHasta").click()
            time.sleep(1)
            # Mes:
            select_mes = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-month"))
            select_mes.select_by_value(str(today_month))
            time.sleep(1)
            # Año:
            select_anio = Select(driver.find_element(By.CLASS_NAME,"ui-datepicker-year"))
            select_anio.select_by_value(str(today_year))
            time.sleep(1)
            # Dia:
            day = driver.find_element(By.XPATH,"//a[@class='ui-state-default' and text()="+str(today_day)+"]")
            day.click()

            # Procedencia:
            sel = Select(driver.find_element(By.ID, "ddlProvincia"))
            time.sleep(3)
            try:
                sel.select_by_visible_text(proc)
            except:
                time.sleep(10)
                sel.select_by_visible_text(proc)


            csv = driver.find_element(By.ID,"btn_generar_csv")
            csv.click()
            time.sleep(15)

            # Buscamos el último archivo descargado
            folder_path = fr'{path}'
            file_type = r'\*csv'
            files = glob.glob(folder_path + file_type)
            max_file = max(files, key=os.path.getctime)

            if "operaciones_informadas" in max_file:
                    print("Se encontró el archivo en descargas.")
                    shutil.move(max_file, f'{path_archivos}/{old_max_day,old_max_month+1,old_max_year}-{today_day,today_month+1,today_year}.csv')
                    print("Archivo movido a la carpeta de trabajo.")
            else:
                print("No se encontró el archivo en descargas.")

            event, values = sg.Window('Error', [[sg.Text('No se encontró el archivo descargado. Ver en pestaña de Chrome sio-granos.\n Si no habían datos para la fecha seleccionada, presione no hay datos.')],
                                                    [sg.Button('Descargado/No hay datos'), sg.Button('Página caída'), sg.Button('Se está descargando')]]).read(close=True)




    event, values = sg.Window('Error', [[sg.Text('El archivo ya se descargó o se confirmó que no hay datos. Presione Ok.')],[sg.Button('Ok'), sg.Button('Cancelar')]]).read(close=True)

    if event == 'Ok':
        print("Problema solucionado.")

    else:
        sg.popup_cancel('Hubo un error. Intente correr el programa nuevamente. Asegúrese de contar con una buena conexión a internet.')
        quit()


# Carga final de datos

# Creo un Dataframe vacio y una lista con los archivos que se encuentran en el directorio, en caso de querer 
# agregar un período de tiempo muy largo:
data = pd.DataFrame()
fichero = os.listdir(f'{path_archivos}')

    #Creo un "for" que me lea todos los archivos y me vaya apendizando las bases a nuestro Dataframe "data":

for base in fichero:    # Compila todos los archivos de la carpeta
    apendice = pd.read_csv(f"{path_archivos}/{base}", index_col=None, sep=";",encoding='utf-16le', header=0,error_bad_lines=False,warn_bad_lines=True)
    data = pd.concat([data,apendice])


baseSQL = pd.DataFrame()

for i in data.columns:
    baseSQL[i] = data[i].astype(str)

columnas_nombres = list(baseSQL.columns.values)
columnas_tipo_de_datos = getColumnDtypes(baseSQL.dtypes)



# Defino el statement para crear la tabla:
crear_tabla_statement = f'CREATE TABLE IF NOT EXISTS {procedencia} ('
for i in range(len(columnas_tipo_de_datos)):
    crear_tabla_statement = crear_tabla_statement +"\n`" + columnas_nombres[i] +  "` " + columnas_tipo_de_datos[i] + ', '
crear_tabla_statement = crear_tabla_statement[:-2] + ');'
        
# Me conecto a la base

connection = pymysql.connect(host=host,user=user, passwd=passwd, db=db, port=int(port))
cursor = connection.cursor()

# Creo la tabla:

try: 
    cursor.execute(crear_tabla_statement)
except:
    print("La tabla ya existe, se va a proceder a cargar los datos:")


# Preparo la inserción de datos:
cols = "`,`".join([str(i) for i in baseSQL.columns.tolist()])

for i,row in baseSQL.iterrows():
    sql = f"INSERT INTO {procedencia} (`" + cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
    cursor.execute(sql, tuple(row))

connection.commit()
connection.close()
print("Carga finalizada.")
sg.popup(f'Carga finalizada.')


quit()