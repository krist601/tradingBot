from binance.client import Client
import ta
import pandas as pd
import time

class TradingBot:
    def __init__(self, api_key, api_secret, symbol, cantidad_inversion, tiempo_espera):
        self.client = Client(api_key, api_secret)
        self.symbol = symbol
        self.cantidad_inversion = cantidad_inversion
        self.tiempo_espera = tiempo_espera
        self.total_inversion = 0

    def obtener_datos_historicos(self, symbol, interval, limit):
        klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        data = []
        for kline in klines:
            timestamp = pd.to_datetime(kline[0], unit='ms')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])
            data.append([timestamp, open_price, high_price, low_price, close_price, volume])

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df.set_index('timestamp', inplace=True)
        return df

    def comprar(self, symbol, cantidad):
        #order = self.client.create_order(
        #    symbol=symbol,
        #    side=Client.SIDE_BUY,
        #    type=Client.ORDER_TYPE_MARKET,
        #    quantity=cantidad
        #)
        self.total_inversion += self.cantidad_inversion
        print(f"Compra realizada: "+symbol+" - "+str(cantidad))

    def vender(self, symbol, cantidad):
        #order = self.client.create_order(
        #    symbol=symbol,
        #    side=Client.SIDE_SELL,
        #    type=Client.ORDER_TYPE_MARKET,
        #    quantity=cantidad
        #)
        self.total_inversion -= self.cantidad_inversion
        print(f"Venta realizada: "+symbol+" - "+str(cantidad))

    def ejecutar(self):
        # Obtener datos históricos del par de trading
        interval = Client.KLINE_INTERVAL_1HOUR
        limit = 100
        data = self.obtener_datos_historicos(self.symbol, interval, limit)

        # Variable para realizar un seguimiento del estado de compra
        comprado = False

        # Bucle principal del bot
        while True:
            # Actualizar los datos con el último valor del precio
            latest_data = self.client.get_klines(symbol=self.symbol, interval=interval, limit=1)
            latest_price = float(latest_data[0][4])
            latest_timestamp = pd.to_datetime(latest_data[0][0], unit='ms')

            # Agregar el último valor al DataFrame de datos históricos
            data.at[latest_timestamp, 'open'] = latest_data[0][1]
            data.at[latest_timestamp, 'high'] = latest_data[0][2]
            data.at[latest_timestamp, 'low'] = latest_data[0][3]
            data.at[latest_timestamp, 'close'] = latest_data[0][4]
            data.at[latest_timestamp, 'volume'] = latest_data[0][5]

            # Calcular indicadores técnicos
            data['ma'] = ta.trend.sma_indicator(data['close'], window=20)
            data['ema'] = ta.trend.ema_indicator(data['close'], window=20)

            # Obtener los últimos valores de los indicadores
            latest_ma = data['ma'].iloc[-1]
            latest_ema = data['ema'].iloc[-1]

            # Restringir el tamaño de los datos históricos
            data = data[-limit:]

            # Lógica del bot
            if not comprado and latest_price > latest_ma and latest_price > latest_ema:
                # Comprar
                self.comprar(self.symbol, self.cantidad_inversion / latest_price)
                comprado = True
            elif comprado and latest_price < latest_ma and latest_price < latest_ema:
                # Vender
                self.vender(self.symbol, self.cantidad_inversion / latest_price)
                comprado = False

            # Calcular el monto total ganado o perdido
            monto_ganado_perdido = self.total_inversion - self.cantidad_inversion

            # Imprimir el monto total ganado o perdido
            print(f"Monto total ganado/perdido: {monto_ganado_perdido}")

            # Esperar antes de la siguiente iteración
            time.sleep(self.tiempo_espera)

def run_trading_bot():
    print("corriendo")
    # Configuración del bot
    api_key = ''
    api_secret = ''
    symbol = 'BTCUSDT'
    cantidad_inversion = 10
    tiempo_espera = 60  # Tiempo de espera en segundos entre cada iteración

    # Crear una instancia del bot y ejecutarlo
    bot = TradingBot(api_key, api_secret, symbol, cantidad_inversion, tiempo_espera)
    bot.ejecutar()


# Ejecutar el bot de trading
run_trading_bot()
