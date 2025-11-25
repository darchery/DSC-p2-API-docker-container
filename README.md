Tienes toda la razón. Basándome en los archivos que has ido subiendo y los comandos que hemos ejecutado (`src/docker-compose-cluster-ej3.yml`, `src/requirements.txt`, etc.), he ajustado la sección de **Estructura del Repositorio** para que sea un reflejo **exacto** de tu carpeta de trabajo.

Aquí tienes el **README.md final y corregido**. Solo tienes que copiarlo y pegarlo.

-----

# Sistema de Monitorización Industrial y Detección de Anomalías (DSC)

Este repositorio contiene la implementación completa de la práctica de "Contenedores con Docker" para la asignatura de Desarrollo de Software Crítico. El proyecto consiste en un sistema de monitorización de sensores industriales diseñado para ser resiliente, escalable y capaz de detectar anomalías en tiempo real mediante técnicas de Inteligencia Artificial.

## Descripción del Proyecto

El desarrollo se ha estructurado en tres fases incrementales que cubren distintos aspectos de la ingeniería de software moderna:

### Ejercicio 1: Monitorización y Contenerización

[cite\_start]Desarrollo de una API REST utilizando Python (Flask) para la ingesta de datos de sensores[cite: 5, 8, 9, 12, 13, 16].

  * [cite\_start]**Persistencia:** Uso de **Redis TimeSeries** para el almacenamiento eficiente de mediciones temporales[cite: 10, 20].
  * [cite\_start]**Visualización:** Despliegue de **Grafana** conectado a Redis para la visualización de datos en tiempo real[cite: 8, 11].
  * [cite\_start]**Contenerización:** Empaquetado de la solución mediante Docker[cite: 6, 8].

### Ejercicio 2: Detección de Anomalías con Machine Learning

[cite\_start]Integración de un módulo de Inteligencia Artificial en la API REST[cite: 63, 64].

  * [cite\_start]**Modelo:** Se utiliza una red neuronal pre-entrenada (Keras/TensorFlow) y un escalador (Scikit-learn)[cite: 65, 66, 67, 68].
  * **Lógica:** El sistema almacena una ventana deslizante de mediciones previas, predice el siguiente valor esperado y lo compara con el valor real recibido. [cite\_start]Si la diferencia supera un umbral predefinido, se alerta de una anomalía[cite: 78, 79].
  * [cite\_start]**Endpoint:** Implementación del recurso `/detectar`[cite: 76].

### Ejercicio 3: Alta Disponibilidad y Tolerancia a Fallos

[cite\_start]Evolución de la arquitectura para eliminar puntos únicos de fallo (SPOF) en la base de datos[cite: 84, 85]. El código fuente ha sido adaptado para soportar dinámicamente dos arquitecturas de despliegue distribuido:

  * [cite\_start]**Redis Sentinel:** Arquitectura Maestro-Esclavo con monitorización automática y failover[cite: 86, 87].
  * [cite\_start]**Redis Cluster:** Arquitectura de fragmentación (sharding) con múltiples maestros y réplicas distribuidas[cite: 88, 89].

-----

## Arquitectura y Tecnologías

  * **Lenguaje:** Python 3.11
  * **Framework Web:** Flask
  * **Base de Datos:** Redis Stack (incluye Redis TimeSeries)
  * **Inteligencia Artificial:** TensorFlow, Numpy, Joblib
  * **Infraestructura:** Docker, Docker Compose
  * **Repositorio de Imágenes:** Docker Hub

-----

## Instalación y Despliegue

[cite\_start]El sistema está configurado para descargar automáticamente las imágenes necesarias desde Docker Hub (`darchery/p2-mediciones-contenedores:ej3`), garantizando la compatibilidad en entornos Linux/AMD64[cite: 131].

### 1\. Clonar el repositorio

```bash
git clone https://github.com/darchery/DSC-p2-API-docker-container.git
cd DSC-p2-API-docker-container
```

### 2\. Ejecución del Sistema

[cite\_start]El proyecto ofrece dos modos de ejecución correspondientes al Ejercicio 3. Ambos modos incluyen todas las funcionalidades de los Ejercicios 1 y 2[cite: 91].

**Opción A: Despliegue con Redis Cluster (Recomendado)**
Levanta una infraestructura con 6 nodos de Redis (3 maestros y 3 esclavos) y la API web configurada para operar en modo clúster.

```bash
docker compose -f src/docker-compose-cluster-ej3.yml --project-name p2-cluster up
```

*Nota: Se utiliza la subred personalizada `172.28.0.0/16` para evitar conflictos de direccionamiento IP con el host.*

**Opción B: Despliegue con Redis Sentinel**
Levanta una infraestructura con 1 Maestro, 2 Réplicas y 3 instancias Sentinel para la monitorización.

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
  * [cite\_start]**Ejemplo:** `http://localhost:4000/nuevo?dato=24.5`[cite: 13, 14, 29].

### 2\. Listado de Mediciones (Ejercicio 1)

Recupera el histórico de mediciones almacenadas y muestra el identificador del contenedor que atendió la petición (útil para verificar balanceo de carga).

  * **URL:** `/listar`
  * **Método:** `GET`
  * [cite\_start]**Ejemplo:** `http://localhost:4000/listar`[cite: 16, 17, 18].

### 3\. Detección de Anomalías (Ejercicio 2)

Inserta una medición y evalúa simultáneamente si constituye una anomalía respecto al patrón histórico reciente.

  * **URL:** `/detectar`
  * **Método:** `GET`
  * **Parámetros:** `dato` (valor numérico)
  * **Respuesta:** Devuelve la predicción del modelo, el umbral de tolerancia y un booleano indicando si es anomalía.
  * [cite\_start]**Ejemplo:** `http://localhost:4000/detectar?dato=120.0`[cite: 64, 76, 79, 81].

-----

## Verificación de Tolerancia a Fallos (Ejercicio 3)

[cite\_start]Para verificar la robustez del sistema, se recomienda realizar pruebas de caos (Chaos Engineering) deteniendo contenedores críticos mientras el sistema está en funcionamiento[cite: 93, 94].

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
├── Dockerfile                         # Definición de la imagen del contenedor
├── README.md                          # Documentación del proyecto
└── src/                               # Código fuente y archivos de configuración
    ├── config.json                    # Configuración de umbrales y ventanas para ML
    ├── docker-compose-cluster-ej3.yml # Orquestación para Redis Cluster
    ├── docker-compose-sentinel-ej3.yml# Orquestación para Redis Sentinel
    ├── main-ej3.py                    # Aplicación principal (API Flask)
    ├── modelo.keras                   # Modelo de red neuronal pre-entrenado
    ├── requirements.txt               # Dependencias de Python
    └── scaler.pkl                     # Escalador de datos para el modelo
```

## Autor

Práctica desarrollada por **Lucas Díaz Ruiz** para la asignatura de Desarrollo de Software Crítico.
[cite\_start]Imagen Docker disponible en: [darchery/p2-mediciones-contenedores](https://www.google.com/search?q=https://hub.docker.com/r/darchery/p2-mediciones-contenedores)[cite: 131].