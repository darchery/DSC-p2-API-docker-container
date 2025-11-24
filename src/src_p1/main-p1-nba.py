import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
from sklearn.preprocessing import MinMaxScaler
import joblib
import json

# ------------------------------------------------------------------------------
# CARGA DE DATOS
# ------------------------------------------------------------------------------

df = pd.read_csv("src/src_p1/datos.csv", index_col=0, parse_dates=True)

print(df.head())
print(df.shape); print() # (7267,1) (según el fichero cambiará el número de filas)

df.plot()
plt.title("Datos originales")
plt.show()

#-------------------------------------------------------------------------------
# PREPROCESAMIENTO Y CREACIÓN DE VENTANAS
# ------------------------------------------------------------------------------
# Tamaño de la ventana
windows_size = 10

#  Asignamos los datos esta variable
data = df.values
# Normalizar los datos (las redes LSTM aprenden mejor con datos escalados)
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(df.values)

n_features = 1

# Crear las ventanas temporales
# Lo que se predice (y) es el "siguiente" valor de la secuencia
# pasando la ventana actual que tenemos.

def split_sequence(data, data_scaled, windows_size):
	X, y = list(), list()
	for i in range(len(data)):
		# find the end of this pattern
		end_ix = i + windows_size
		# check if we are beyond the sequence
		if end_ix > len(data)-1:
			break
		# gather input and output parts of the pattern
		data_x, data_y = data_scaled[i:end_ix], data[end_ix]  # Lo que se predice (y) es el "siguiente" valor de la secuencia
		X.append(data_x)
		y.append(data_y)
	return np.array(X),np. array(y)


X, y = split_sequence(data, data_scaled, windows_size)

n_features = 1

# Comprobamos la forma de los datos
print("Forma de X: ", X.shape)  # (nº_muestras, pasos temporales/tam_ventana, features)
print("Forma de Y: ", y.shape); print()


# ------------------------------------------------------------------------------
# CONSTRUCCIÓN DEL MODELO LSTM
# ------------------------------------------------------------------------------
# Crear la RNN(Recurrent Neural Network)
model = Sequential()
model.add(Input(shape=(windows_size, n_features)))
model.add(LSTM(50, activation='relu'))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')
model.summary()

# ------------------------------------------------------------------------------
# ENTRENAMIENTO
# ------------------------------------------------------------------------------
# Entrenar la RNN
history = model.fit(
    X, y,
    epochs=20,
    batch_size=32,
    validation_split=0.1,
    verbose=1
)

# ------------------------------------------------------------------------------
# PREDICCIÓN Y DETECCIÓN DE ANOMALÍAS
# ------------------------------------------------------------------------------
# Un posible criterio de anomalía
# Calcular el error absoluto medio (MAE) de los "siguientes" valores de cada secuencia y los valores predichos

# Hacemos la predicciones
y_pred = model.predict(X)

# Escalado MinMax
# Invertimos la escala para obtener valores originales
y_pred_inv = scaler.inverse_transform(y_pred)
y_inv = scaler.inverse_transform(y)

# Calcular el promedio del MAE(Mean Absolute Error)
mae = np.mean(np.abs(y_pred_inv - y_inv), axis=1)

# Criterios: percentil 99
threshold = np.percentile(mae, 99)

# Guardamos el threshold
with open("src/config.json", "w") as f:
	json.dump({"threshold": threshold, "windows_size": windows_size}, f)

anomalies = mae > threshold

# Mostrar las fechas de las anomalías
# las anomalias se refieren a las ventanas, no a filas específicas dentro de la ventana
fechas_test = df.index[windows_size:]
print(f"El número de anomalías es {np.sum(anomalies)} sobre {len(fechas_test)}")
print("Fechas y valores anómalos detectados:")
anomalies_date_value = df.loc[fechas_test[anomalies]]
print(anomalies_date_value)

# -------------------------------------------------------------------------------------------------
# GRAFICAR RESULTADOS
# -------------------------------------------------------------------------------------------------
# Mostrar la gráfica con las anomalías
plt.figure(figsize=(12,5))
plt.plot(fechas_test, y_inv, color='blue', label='Valor real-y_test')
plt.plot(fechas_test, y_pred_inv, color='orange', linestyle='dotted',label='Predicción-y_pred')
plt.scatter(fechas_test[anomalies], y_inv[anomalies], color='red', label='Anomalías')
plt.legend()
plt.title("Detección de anomalías con LSTM - Mejorada(Min-Max + Tam_Ventana=20)")
plt.show()


# -------------------------------------------------------------------------------------------------
# CÓDIGO PARA LA REUTILIZACIÓN DE LA PRÁCTICA 1 EN LA PRÁCTICA 2(EJERCICIO 2)
# -------------------------------------------------------------------------------------------------
# Guardamos el modelo
model.save('src/modelo.keras')
# Guardamos el escalador
joblib.dump(scaler, 'src/scaler.pkl')