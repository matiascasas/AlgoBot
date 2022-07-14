import ta
import numpy as np
import pandas as pd

# ---------------------------------------------------------------- #
###########################     Signals    #########################
# Esta clase tiene como atributos el df y algunos parametros
# variables para calcular las signals de entrada (ej: n).
# El objetivo es tener tu DataFrame y que se le pueda sumar
# cualquier indicador
# ---------------------------------------------------------------- #

class Signals:

    def __init__(self, df, n, stratergy):
        self.df = df
        self.n = n
        self.stratergy = stratergy

    def indicators(self):

        self.df['%K'] = ta.momentum.stoch(self.df.High, self.df.Low, self.df.Close, window=14, smooth_window=3)
        self.df['%D'] = self.df['%K'].rolling(3).mean()  # %D es la media movil de %K
        self.df['rsi'] = ta.momentum.rsi(self.df.Close, window=14)

        self.df['macd'] = ta.trend.macd_diff(self.df.Close)
        adx_class = ta.trend.ADXIndicator(high = self.df['High'],    #no se le puede cambiar el suavizado!
                                               low = self.df['Low'],
                                               close = self.df['Close'],
                                               window = 14,
                                               fillna = False)
        self.df['adx'] = adx_class.adx()
        self.df['adx_neg'] = adx_class.adx_neg()
        self.df['adx_pos'] = adx_class.adx_pos()

        self.df['atr'] = ta.volatility.AverageTrueRange(high = self.df['High'],    #no se le puede cambiar el suavizado!
                                                        low = self.df['Low'],
                                                        close = self.df['Close'],
                                                        window = 14,
                                                        fillna = False).average_true_range()

        self.df = self.df.drop(self.df.index[range(15)])      #Eliminamos las 15 primeras filas
        self.df.dropna(inplace=True)

    def gettrigger(self, buy=True):
        dfx = pd.DataFrame()
        for i in range(self.n + 1):
            mask = (self.df['%K'].shift(i) < 20) & (self.df['%D'].shift(i) < 20)
            dfx = dfx.append(mask, ignore_index=True)
        return dfx.sum(axis=0)

    # Metodo para agregar las columnas de trigger y compra al df en base a la estrategia deseada
    def decide(self):

        if self.stratergy == "estrategia_1":
            self.df['trigger'] = np.where(self.gettrigger(), 1, 0)
            self.df['Buy'] = np.where(self.df.trigger & self.df['%K'].between(20, 80) & self.df['%D'].between(20, 80)
                                  & (self.df['rsi'] > 50) & (self.df['macd'] > 0), 1, 0)

        if self.stratergy == "estrategia_adx":
            self.df['Buy'] = np.where((self.df['adx'] > 25) & (self.df['adx_pos'] > self.df['adx_neg']), 1, 0)