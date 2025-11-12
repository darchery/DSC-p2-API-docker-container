from flask import Flask, request
from redis import Redis, RedisError
import os
import socket 
from datetime import datetime

# ---------------------------------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------------------------------
def timestamp_a_fecha_con_formato(timestamp):
    fecha_segundos = timestamp / 1000 # a segundos
    fecha = datetime.fromtimestamp(fecha_segundos) # Transforma de segundos a un objeto datatime
    fecha_str = fecha.strftime('%d/%m/%Y %H:%M:%S') # Asigna el formato europeo
    return fecha_str

# ---------------------------------------------------------------------------------------------------
# Código plantilla basado en app.py
# ---------------------------------------------------------------------------------------------------

# Nos conectamos a redis

# Obtiene el valor de la variable de entorno REDIS_HOST, si esta no está definida, devolverá por defecto "localhost",
# en ella está la dirección del servidor redis al que se intentará conectar
REDIS_HOST = os.getenv('REDIS_HOST', "localhost")

print("REDIS_HOST: "+REDIS_HOST) # Confirmamos el host usado

# Crea un cliente de redis que se conectará a REDIS_HOST, se usará la db 0, tendrá tiempos de espera(segundos) para 
# conectarse y para realizar operaciones(evita que el programa se bloquee si Redis no responde) y usará el puerto 
# 6379(predeterminado de redis) 
redis = Redis(host=REDIS_HOST, db=0, socket_connect_timeout=2, socket_timeout=2, decode_responses=True)

# Creamos la instancia de la aplicación web Flask
app = Flask(__name__)

# Registra la función nueva_medicion() como el manejador de las soliciturdes HTTP GET a la ruta "/nuevo"
# Cuando  un cliente acceda a http://host:port/ => Flask ejecutará la función hello() y delvolverá el resultado como
# respuesta HTTP
@app.route("/nuevo")
def nueva_medicion():
    # Hacemos una petición GET del valor enviado
    dato = request.args.get("dato")
    # Si no hay valor devolveremos un mensaje de error y el "status code" de HTTP 400
    if dato is None:
        return "ERROR: falta el parámetro 'dato'", 400
    # El usuario ha introducido un valor(sea correcto o no)
    else :
        try:
            # La API debe leer valores decimales
            valor = float(dato)
        except  ValueError:
            return "ERROR: el valor debe ser numérico", 400

        # Capturamos la fecha actual, la convertimos el objeto datatime  a un número
        # flotante que representa el tiempo en segundos, luego la pasamos a milisegundos ya que 
        # RedisTimeSeries usa milisengundos nativamente y por último 
        # convertimos este valor a el tipo  entero(el formato de redis lo requiere)
        timestamp = int(datetime.now().timestamp() * 1000) 

        try:
            # Ejecutamos el comando de RedisTimeSeries TS.ADD para añadir una instancia
            # a la serie temporal 'mediciones'
            redis.execute_command('TS.ADD', 'mediciones', timestamp, valor)
        except RedisError as e:
            return f"ERROR: error al insertar un dato con Redis => {e}", 500
        except Exception as e:
            return f"ERROR: error inesperado al insertar un datos en Redis => {e}", 500
        
        return f"CORRECTO: <b>Dato={dato}</b> almacenado en la fecha <b>{timestamp_a_fecha_con_formato(timestamp)}</b><br> por el hostname: <b>{socket.gethostname()}</b>"
    

@app.route("/listar")
def listar():
    try:
        # Obtener las muestras de la serie temporal mediciones
        # El - indica comenzar desde el tiempo más temprano (antiguo) al + que indica el tiempo más reciente
        muestras = redis.execute_command('TS.REVRANGE', 'mediciones', '-', '+',)
        # Indicaremos el nombre del host
        salida = f"<b>Hostname:</b> {socket.gethostname()}<br>"
        
        # Si hay muestras => listaremos los valores en la variable salida en formato html
        for time, valor in muestras:
            salida += f"{timestamp_a_fecha_con_formato(time)} => {valor}<br>" 
        return salida
    except RedisError as e:
        return f"ERROR: error al listar los datos con Redis => {e}", 500
    except Exception as e:
        return f"ERROR: error inesperado listar los datos => {e}", 500

@app.route("/borrar")
def borrar_mediciones():
    try:
        # Ejecutaremos este comando para comprobar si hay muestras o no disponibles
        redis.execute_command('TS.REVRANGE', 'mediciones', '-', '+',)
    
        # Si hay muestras => borramos la serie temporal
        redis.delete("mediciones")
        return "Las mediciones se han borrado con éxito."
    except RedisError as e:
        return f"ERROR: error al borrar los datos con Redis => {e}", 500
    except Exception as e:
        return f"ERROR: error inesperado al borrar los datos => {e}", 500

@app.route("/")
def bienvenido_instrucciones():
    return (
    f"<b>Hostname:</b> {socket.gethostname()}<br>"
    "Bienvenid@ a la API de <b>mediciones</b>!<br>"
    "Funciones disponibles:<br>"
    "<b>(1) /nuevo?dato=VALOR </b>: añade una medición<br>"
    "<b>(2) /listar </b>: muestra las mediciones tomadas<br>"
    "<b>(3) /borrar </b>: borra todas las mediciones<br>"
    "<b>(4) / </b>: página principal<br>")

if __name__ == "__main__":
    # Obtiene el valor de la variable de entorno PORT y si no está definidad usará el puerto 80
    PORT = os.getenv('PORT', 80)
    # Imprime el puerto para una verificación
    print("PORT: "+str(PORT))
    # Arranca el servidor Flask escuchando a todas las interfaces(0.0.0.0) para ser accesible desde otros contenedores
    # o la máquina host
    app.run(host='0.0.0.0', port=PORT)

