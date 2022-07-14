import requests
from binance.client import Client   # https://python-binance.readthedocs.io/en/latest/
from binance.exceptions import BinanceAPIException
import getpass
import pandas as pd
import conf
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# Funcion para loggearse en Binance cargando credenciales de conf.py
def auth_binance_file():
    try:
        client = Client(api_key=conf.apiKey, api_secret=conf.secKey)
        if client.get_system_status() != 1:
            print('Servidor OK')
        else:
            print('Servidor en mantenimiento')
        print(client.get_account())
    except BinanceAPIException as e:
        print(e)
        return -1
    return client


# Funcion para loggearse en Binance preguntando en consola
def auth_binance_console():
    apikey = input('apikey: ')
    seckey = getpass.getpass('secKey: ')

    client = Client(apikey, seckey)
    print(client.get_system_status())  # status:1 -> servidor en mantenimiento

    try:
        print(client.get_account())
    except BinanceAPIException as e:
        return -1
    return client


# Funcion para pedir la data a la API
def getData(client, symbol, interval, str_time, end_time):
    try:
        if end_time == 0:
            frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                              interval,
                                                              str_time + 'min ago UTC'))
        else:
            frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                              interval,
                                                              str_time, end_time))
    except requests.exceptions.RequestException as e:
        print(e)
        return
    except requests.ConnectionError as e:
        print(e)
        return
    except BinanceAPIException as e:
        print(e)
        return

    if frame.empty:
        print('getMinuteData:: Bad request')

    frame = frame.iloc[:, :6]  # solo 6 columnas de interes
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')  # Ahora el DataFrame es ordenado por el tiempo
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


# Funcion para calcular el stop loss
# k = {1..5}
# Retorna el porcentaje en decimal
def stop_loss_atr(df, k, i):
    stop = (df.Close.iloc[i] - (k * df.atr.iloc[i]))
    return stop / df.Close.iloc[i]


# Funcion para calcular el target
# Retorna el porcentaje en decimal
def target(df, k, i):
    target = df.Close.iloc[i] + (k * df.atr.iloc[i])
    return target / df.Close[i]
