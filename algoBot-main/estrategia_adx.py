import binanceUtils
from signals import Signals
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ----------------------------------------------------------------------------- #
###############          Estrategia ADX          ################################
# https://www.youtube.com/watch?v=pAFJmmjY9K8&ab_channel=TradingStrategyTesting
#
# Condiciones de compra:
#   -> ADX > 25
#   -> ADX pos > ADX neg
#
# Condiciones de venta:
#   -> ADX neg > ADX pos
# ----------------------------------------------------------------------------- #

def estrategia_adx_backtesting_graph(client, sym, k_stop_loss, k_target, str_time, end_time, interval, open_position=False):

    i = 0
    j = 0
    compras = 0
    buy_price = 0
    suma = 0
    venta_positiva = 0
    venta_negativa = 0

    df_history = binanceUtils.getData(client, sym, interval, str_time, end_time)  #obtiene data historica

    if isinstance(df_history, pd.DataFrame):

        df = df_history
        signalClass = Signals(df, 25, "estrategia_adx")
        signalClass.indicators()
        signalClass.decide()

        print("LARGO:")
        print(len(signalClass.df))
        # Plots
        fig, ax = plt.subplots(2)
        fig.suptitle('Estrategia ADX: ' + sym + ' desde: ' + str_time + ' hasta: ' + end_time)
        fig.tight_layout()

        x_axe = signalClass.df.index
        y_axe = np.ones(len(signalClass.df.index))

        ax[0].set_title('Precio de cierre')
        ax[0].grid(linestyle='dotted')
        ax[0].plot(signalClass.df.index, signalClass.df['Close'])

        ax[1].set_title('ADX')
        ax[1].grid(linestyle='dotted')
        ax[1].plot(signalClass.df['adx'], "r-")
        ax[1].plot(x_axe, np.multiply(y_axe, 25))
        ax[1].plot(signalClass.df['adx_neg'], "b-")
        ax[1].plot(signalClass.df['adx_pos'], "g-")

        while i <= (len(signalClass.df)-2):
            print(i)
            if signalClass.df.Buy.iloc[i]:  # abre posicion y compra
                ax[0].annotate('Compra', (signalClass.df.index[i], signalClass.df.Close.iloc[i]),
                            arrowprops = dict(facecolor='blue', shrink=0.05))
                ax[1].annotate('Compra', (signalClass.df.index[i], signalClass.df.rsi.iloc[i]),
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

                # print("----------------------")
                # print("Close price: ")
                # print(df.Close[j])
                # print("\n")
                # print("Stop Loss: ")
                # print(stop_loss)
                # print("\n")
                # print("Target: ")
                # print(target)
                # print("\n")
                # print("----------------------")

                if (signalClass.df.Close[j] <= buy_price * stop_loss)\
                        or (signalClass.df.adx_neg[j] > signalClass.df.adx_pos[j])\
                        or (signalClass.df.Close[j] >= buy_price * target):

                    dif = (signalClass.df.Close[j] - buy_price)
                    if dif > 0:
                        venta_positiva = venta_positiva + 1
                        suma = suma + dif

                        ax[0].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                    arrowprops=dict(facecolor='green', shrink=0.05))
                        ax[1].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                       arrowprops=dict(facecolor='green', shrink=0.05))
                    else:
                        venta_negativa = venta_negativa + 1
                        suma = suma + dif

                        ax[0].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                    arrowprops=dict(facecolor='red', shrink=0.05))
                        ax[1].annotate('Venta', (signalClass.df.index[j], signalClass.df.Close.iloc[j]),
                                       arrowprops=dict(facecolor='red', shrink=0.05))

                    open_position = False
                    break

        print('Numero de compras: ' + str(compras) + '\n')
        print('Numero de ventas Positivas: ' + str(venta_positiva) + '\n')
        print('Numero de ventas Negativas: ' + str(venta_negativa) + '\n')
        print('Saldo total: ' + str(suma) + '\n')
        plt.show()