import binanceUtils
from signals import Signals
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------- #
###############     Estrategia1: Stoch, RSI y MACD    ################
# https://www.youtube.com/watch?v=r8pU-8l1KPU&ab_channel=Algovibes
#
# Condiciones de compra:
#   -> En los ultimos n steps el Stochastic (%K y %D) bajo los 20
#   -> Stochastic (%K y %D) entre 20 y 80
#   -> RSI mayor a 50
#   -> MACD por encima de la signal line (MACD diff > 0)
#
# Condiciones de venta:
#   -> Target: 1.005*Buying_price
#   -> Stop Loss: 0,995*Buying_price
# ---------------------------------------------------------------- #


def estrategia1(client, sym, qty, t, tSearching, tChecking, stopLoss, target, openPosition=False):
    df = binanceUtils.getData(client, sym, '1m', tSearching, '0')
    signal_class = Signals(df, 25, "estrategia_1")
    signal_class.indicators()
    signal_class.decide()

    if signal_class.df.Buy.iloc[-1]:  # abre posicion y compra
        order = client.create_order(symbol=sym,
                                    side='BUY',
                                    type='MARKET',
                                    quantity=qty)
        print(order)
        buy_price = float(order['fills'][0]['price'])  # Estudiar como retorna el order
        open_position = True

    while open_position:
        time.sleep(t)
        df = binanceUtils.getData(client, sym, '1m', tChecking, '0')
        print(f'Current close is:' + str(df.Close.iloc[-1]))
        print(f'Current target is:' + str(buy_price * target))
        print(f'Current stop is:' + str(buy_price * stopLoss))

        if (df.Close[-1] <= buy_price * stopLoss) or (df.Close[-1] >= buy_price * target):
            order = client.create_order(symbol=sym,
                                        side='SELL',
                                        type='MARKET',
                                        quantity=qty)
            print(order)
            break


def estrategia1_backtesting_graph(client, sym, k_stop_loss, k_target, str_time, end_time, interval, open_position=False):

    i = 0
    j = 0
    buy_price = 0
    suma = 0
    compras = 0
    venta_positiva = 0
    venta_negativa = 0

    df_history = binanceUtils.getData(client, sym, interval, str_time, end_time)  #obtiene data historica

    if isinstance(df_history, pd.DataFrame):

        df = df_history
        signalClass = Signals(df, 25, "estrategia_1")
        signalClass.indicators()
        signalClass.decide()

        # Plots
        fig, ax = plt.subplots(5)
        fig.suptitle('Estrategia 1: ' + sym + ' desde: ' + str_time + ' hasta: ' + end_time)
        fig.tight_layout()

        x_axe = signalClass.df.index
        y_axe = np.ones(len(signalClass.df.index))

        ax[0].set_title('Precio de cierre')
        ax[0].grid(linestyle='dotted')
        ax[0].plot(signalClass.df.index, signalClass.df['Close'])

        ax[1].set_title('RSI')
        ax[1].grid(linestyle='dotted')
        ax[1].plot(signalClass.df['rsi'])
        ax[1].plot(x_axe, np.multiply(y_axe, 50), 'tab:red')

        ax[2].set_title('MacD')
        ax[2].grid(linestyle='dotted')
        ax[2].plot(signalClass.df['macd'])
        ax[2].plot(x_axe, np.multiply(y_axe, 0), 'tab:red')

        ax[3].set_title('Estocastico')
        ax[3].grid(linestyle='dotted')
        ax[3].plot(signalClass.df['%K'])
        ax[3].plot(signalClass.df['%D'])
        ax[3].plot(x_axe, np.multiply(y_axe, 80), 'tab:red')
        ax[3].plot(x_axe, np.multiply(y_axe, 20), 'tab:red')

        ax[4].set_title('ATR')
        ax[4].grid(linestyle='dotted')
        ax[4].plot(signalClass.df.index, signalClass.df['atr'])

        while i <= (len(signalClass.df)-2):

            if signalClass.df.Buy.iloc[i]:  # abre posicion y compra

                ax[0].annotate('Compra', (signalClass.df.index[i], signalClass.df.Close.iloc[i]),
                            arrowprops = dict(facecolor='blue', shrink=0.05))
                ax[1].annotate('Compra', (signalClass.df.index[i], signalClass.df.rsi.iloc[i]),
                               arrowprops=dict(facecolor='blue', shrink=0.05))
                ax[2].annotate('Compra', (signalClass.df.index[i], signalClass.df.macd.iloc[i]),
                               arrowprops=dict(facecolor='blue', shrink=0.05))

                buy_price = signalClass.df.Close.iloc[i]
                compras = compras + 1
                open_position = True
                j = i

            else:
                i = i + 1

            while open_position and j<=(len(signalClass.df)-2):

                j = j + 1
                i = j
                # Calculamos stopLoss y target
                stop_loss = binanceUtils.stop_loss_atr(signalClass.df, k_stop_loss, i)
                target = binanceUtils.target(signalClass.df, k_target, i)

                print("----------------------")
                print("Close price: ")
                print(df.Close[j])
                print("\n")
                print("Stop Loss: ")
                print(stop_loss)
                print("\n")
                print("Target: ")
                print(target)
                print("\n")
                print("----------------------")

                if (signalClass.df.Close[j] <= buy_price * stop_loss) or (signalClass.df.Close[j] >= buy_price * target):

                    dif = (signalClass.df.Close[j] - buy_price)
                    if dif > 0:

                        venta_positiva = venta_positiva + 1
                        suma = suma + dif

                        ax[0].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                    arrowprops=dict(facecolor='green', shrink=0.05))
                        ax[1].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                       arrowprops=dict(facecolor='green', shrink=0.05))
                        ax[2].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                       arrowprops=dict(facecolor='green', shrink=0.05))
                        ax[3].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                       arrowprops=dict(facecolor='green', shrink=0.05))
                    else:

                        venta_negativa = venta_negativa + 1
                        suma = suma + dif

                        ax[0].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                    arrowprops=dict(facecolor='red', shrink=0.05))
                        ax[1].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                       arrowprops=dict(facecolor='red', shrink=0.05))
                        ax[2].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                       arrowprops=dict(facecolor='red', shrink=0.05))
                        ax[3].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                       arrowprops=dict(facecolor='red', shrink=0.05))

                    open_position = False
                    break

        print('Numero de compras: ' + str(compras) + '\n')
        print('Numero de ventas Positivas: ' + str(venta_positiva) + '\n')
        print('Numero de ventas Negativas: ' + str(venta_negativa) + '\n')
        print('Saldo total: ' + str(suma) + '\n')
        plt.show()


def estrategia1_backtesting(client, sym,  k_stop_loss, k_target, str_time, end_time, interval, open_position=False):

    i = 0
    j = 0
    buy_price = 0
    suma = 0
    compras = 0
    venta_positiva = 0
    venta_negativa = 0

    df_history = binanceUtils.getData(client, sym, interval, str_time, end_time)  #obtiene data historica

    if isinstance(df_history, pd.DataFrame):

        df = df_history
        signalClass = Signals(df, 25, "estrategia_1")
        signalClass.indicators()
        signalClass.decide()

        while i <= (len(signalClass.df)-2):
            print(i)
            if signalClass.df.Buy.iloc[i] and (signalClass.df.adx[i] > 25):  # abre posicion y compra

                buy_price = signalClass.df.Close.iloc[i]
                compras = compras + 1
                open_position = True
                j = i

            else:
                i = i + 1

            while open_position and j<=(len(signalClass.df)-2):

                j = j + 1
                i = j
                # Calculamos stopLoss y target
                stop_loss = binanceUtils.stop_loss_atr(signalClass.df, k_stop_loss, i)
                target = binanceUtils.target(signalClass.df, k_target, i)

                if (signalClass.df.Close[j] <= buy_price * stop_loss) or (signalClass.df.Close[j] >= buy_price * target):

                    dif = (signalClass.df.Close[j] - buy_price)
                    if dif > 0:
                        venta_positiva = venta_positiva + 1
                        suma = suma + dif
                    else:
                        venta_negativa = venta_negativa + 1
                        suma = suma + dif

                    open_position = False
                    break

        print('Numero de compras: ' + str(compras) + '\n')
        print('Numero de ventas Positivas: ' + str(venta_positiva) + '\n')
        print('Numero de ventas Negativas: ' + str(venta_negativa) + '\n')
        print('Saldo total: ' + str(suma) + '\n')


def estrategia1_testing(client, sym, qty, t, tSearching, tChecking, stopLoss, target, file, openPosition=False):

    df = binanceUtils.getData(client, sym, '1m', tSearching)
    if isinstance(df, pd.DataFrame):
        signalClass = Signals(df, 25, "estrategia_1")
        signalClass.indicators()
        signalClass.decide()
        print(signalClass.df.Close.iloc[-1])

        if signalClass.df.Buy.iloc[-1]:  # abre posicion y compra
            buyPrice = signalClass.df.Close.iloc[-1]
            print('----------------------------------- \n')
            print('COMPRA a: ' + str(buyPrice) + '\n')
            openPosition = True

    while openPosition:
        time.sleep(t)
        df = binanceUtils.getData(client, sym, '1m', tChecking)

        if isinstance(df, pd.DataFrame):
            if (df.Close[-1] <= buyPrice * stopLoss) or (df.Close[-1] >= buyPrice * target):
                print('VENTA a:' + str(df.Close[-1]) + '\n')
                dif = (df.Close[-1] - buyPrice) * float(qty)
                print('SALDO: ' + str(dif) + '\n')

                if dif > 0:
                    file.write('1 \n')
                if dif < 0:
                    file.write('0 \n')

                break