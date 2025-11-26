# Sistema de Monitorización Industrial y Detección de Anomalías (DSC)

Este repositorio contiene la implementación completa de la práctica de "Contenedores con Docker" para la asignatura de Desarrollo de Software Crítico. El proyecto consiste en un sistema de monitorización de sensores industriales diseñado para ser resiliente, escalable y capaz de detectar anomalías en tiempo real mediante técnicas de Inteligencia Artificial.

## Descripción del Proyecto

El desarrollo se ha estructurado en tres fases incrementales que cubren distintos aspectos de la ingeniería de software moderna:

### Ejercicio 1: Monitorización y Contenerización

Desarrollo de una API REST utilizando Python (Flask) para la ingesta de datos de sensores.

  * **Persistencia:** Uso de **Redis TimeSeries** para el almacenamiento eficiente de mediciones temporales.
  * **Visualización:** Despliegue de **Grafana** conectado a Redis para la visualización de datos en tiempo real.
  * **Contenerización:** Empaquetado de la solución mediante Docker para garantizar la portabilidad.

### Ejercicio 2: Detección de Anomalías con Machine Learning

Integración de un módulo de Inteligencia Artificial en la API REST.

  * **Modelo:** Se utiliza una red neuronal pre-entrenada (Keras/TensorFlow) y un escalador (Scikit-learn) cargados dinámicamente.
  * **Lógica:** El sistema almacena una ventana deslizante de mediciones previas, predice el siguiente valor esperado y lo compara con el valor real recibido. Si la diferencia supera un umbral predefinido (`threshold`), se alerta de una anomalía.
  * **Endpoint:** Implementación del recurso `/detectar`.

### Ejercicio 3: Alta Disponibilidad y Tolerancia a Fallos

Evolución de la arquitectura para eliminar puntos únicos de fallo (SPOF) en la base de datos: 1908. El código fuente ha sido adaptado para soportar dinámicamente dos arquitecturas de despliegue distribuido:

  * **Redis Sentinel:** Arquitectura Maestro-Esclavo con monitorización automática y *failover* (recuperación ante fallos).
  * **Redis Cluster:** Arquitectura de fragmentación (*sharding*) con múltiples maestros y réplicas distribuidas para escalabilidad horizontal.

-----

## Arquitectura y Tecnologías

  * **Lenguaje:** Python 3.11
  * **Framework Web:** Flask
  * **Base de Datos:** Redis Stack (incluye Redis TimeSeries)
  * **Inteligencia Artificial:** TensorFlow, Keras, Numpy, Joblib
  * **Infraestructura:** Docker, Docker Compose
  * **Repositorio de Imágenes:** Docker Hub

-----

## Instalación y Despliegue

El sistema está configurado para descargar automáticamente las imágenes necesarias desde Docker Hub (`darchery/p2-mediciones-contenedores:ej3`), garantizando la compatibilidad en entornos Linux/AMD64.

### 1\. Clonar el repositorio

```bash
git clone https://github.com/darchery/DSC-p2-API-docker-container.git
cd DSC-p2-API-docker-container
```

### 2\. Ejecución del Sistema

El proyecto ofrece dos modos de ejecución correspondientes al Ejercicio 3. Ambos modos incluyen todas las funcionalidades de los Ejercicios 1 y 2 (ingesta y detección de anomalías).

**Opción A: Despliegue con Redis Cluster (Recomendado)**
Levanta una infraestructura con 6 nodos de Redis (3 maestros y 3 esclavos) y la API web configurada para operar en modo clúster.

```bash
docker compose -f src/docker-compose-cluster-ej3.yml --project-name p2-cluster up
```

*Nota: Se utiliza la subred personalizada `172.28.0.0/16` en la configuración de red para evitar conflictos de direccionamiento IP con el sistema host (Windows/WSL).*

**Opción B: Despliegue con Redis Sentinel**
Levanta una infraestructura con 1 Maestro, 2 Réplicas y 3 instancias Sentinel para la monitorización y consenso.

```bash
docker compose -f src/docker-compose-sentinel-ej3.yml --project-name p2-sentinel up
```

-----

## Documentación de la API

La API se expone en el puerto **4000** del host local.

### 1\. Ingesta de Datos (Ejercicio 1)

Almacena una nueva medición en la serie temporal.

  * **URL:** `/nuevo`
  * **Método:** `GET`
  * **Parámetros:** `dato` (valor numérico)
  * **Ejemplo:** `http://localhost:4000/nuevo?dato=24.5`.

### 2\. Listado de Mediciones (Ejercicio 1)

Recupera el histórico de mediciones almacenadas y muestra el identificador del contenedor que atendió la petición.

  * **URL:** `/listar`
  * **Método:** `GET`
  * **Ejemplo:** `http://localhost:4000/listar`.

### 3\. Borrado de Mediciones (Ejercicio 1)

Borra las mediciones almacenadas.

  * **URL:** `/borrar`
  * **Método:** `GET`
  * **Ejemplo:** `http://localhost:4000/borrar`.

### 4\. Detección de Anomalías (Ejercicio 2)

Inserta una medición y evalúa simultáneamente si constituye una anomalía respecto al patrón histórico reciente.

  * **URL:** `/detectar`
  * **Método:** `GET`
  * **Parámetros:** `dato` (valor numérico)
  * **Respuesta:** Devuelve un JSON con la predicción del modelo, el umbral de tolerancia, la ventana de datos usada y un booleano indicando si es anomalía.
  * **Ejemplo:** `http://localhost:4000/detectar?dato=120.0`.

-----

## Verificación de Tolerancia a Fallos (Ejercicio 3)

Para verificar la robustez del sistema, se recomienda realizar pruebas de caos (*Chaos Engineering*) deteniendo contenedores críticos mientras el sistema está en funcionamiento.

**Procedimiento de prueba en Redis Cluster:**

1.  Identificar los nodos maestros:
    ```bash
    docker exec -it redis-node-1 redis-cli -c CLUSTER NODES
    ```
2.  Detener manualmente un contenedor que actúe como maestro (por ejemplo, el nodo 1):
    ```bash
    docker stop redis-node-1
    ```
3.  Verificar la recuperación. Al consultar nuevamente el estado del clúster desde otro nodo, se observará que la réplica correspondiente ha sido promocionada a maestro automáticamente, y la API continúa operativa sin pérdida de servicio.

-----

## Estructura del Repositorio

A continuación se detalla la organización de los archivos del proyecto:

```text
├── .gitignore                         # Ficheros ignorados por git
├── README.md                          # Documentación del proyecto
└── src/                               # Código fuente y archivos de configuración
    ├── src_p1/                        # Recursos adicionales de la Práctica 1
    │   ├── datos.csv                  # Dataset original
    │   └── main-p1-nba.py             # Script de entrenamiento inicial
    ├── Dockerfile-ej1                 # Imagen para el Ejercicio 1
    ├── Dockerfile-ej2                 # Imagen para el Ejercicio 2
    ├── Dockerfile-ej3                 # Imagen final (Ejercicio 3)
    ├── config.json                    # Configuración de umbral y tamaño de ventana
    ├── docker-compose-cluster-ej3.yml # Orquestación Redis Cluster
    ├── docker-compose-ej1.yml         # Orquestación Ejercicio 1
    ├── docker-compose-ej2.yml         # Orquestación Ejercicio 2
    ├── docker-compose-sentinel-ej3.yml# Orquestación Redis Sentinel
    ├── docker-swarm-ej1.yml           # Despliegue en Docker Swarm
    ├── main-ej1.py                    # Lógica Ejercicio 1
    ├── main-ej2.py                    # Lógica Ejercicio 2
    ├── main-ej3.py                    # Lógica final (Cluster/Sentinel)
    ├── modelo.keras                   # Modelo de red neuronal pre-entrenado
    ├── requirements.txt               # Dependencias de Python
    └── scaler.pkl                     # Escalador de datos para el modelo
 
```

## Autor

Práctica desarrollada por **Lucas Díaz Ruiz** para la asignatura de Desarrollo de Software Crítico.
Imagen Docker disponible en: https://www.google.com/search?q=https://hub.docker.com/r/darchery/p2-mediciones-contenedores.