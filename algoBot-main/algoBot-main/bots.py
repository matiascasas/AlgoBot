import time
import binanceUtils
import estrategia_1
import estrategia_adx

# ---------------------------------------------------------------- #
###########################     Bots    #########################
# En ese file se definen todos los bots para cada estrategia
# ---------------------------------------------------------------- #

def bot_estrategia1_testing():
    client = binanceUtils.auth_binance_file()
    if client != -1:
        while True:
            file = open("resultados.txt", "a")
            estrategia_1.estrategia1_testing(client=client,
                                             sym='BTCUSDT',
                                             qty='100',
                                             t=0.5,
                                             tSearching='100',
                                             tChecking='2',
                                             stopLoss=0.995,
                                             target=1.005,
                                             file=file)
            file.close()
            time.sleep(0.5)


def bot_backtesting_estrategia1():
    client = binanceUtils.auth_binance_file()
    estrategia_1.estrategia1_backtesting(client= client,
                                         sym= 'BTCUSDT',
                                         k_stop_loss= 1,
                                         k_target= 2,
                                         str_time= "01 Nov, 2021",
                                         end_time= "30 Nov, 2021",
                                         interval= '1m')

def bot_backtesting_estrategia1_graph():
    client = binanceUtils.auth_binance_file()
    estrategia_1.estrategia1_backtesting_graph(client = client,
                                               sym = 'ADAUSDT',
                                               k_stop_loss = 3,
                                               k_target = 2,
                                               str_time = "01 Feb, 2022",
                                               end_time = "05 Feb, 2022",
                                               interval = '1m')

def bot_backtesting_estrategia_adx_graph():
    client = binanceUtils.auth_binance_file()
    estrategia_adx.estrategia_adx_backtesting_graph(client = client,
                                                    sym = 'ADAUSDT',
                                                    k_stop_loss = 1,
                                                    k_target = 2,
                                                    str_time = "02 Jan, 2021",
                                                    end_time = "02 Jul, 2021",
                                                    interval = '1d')
