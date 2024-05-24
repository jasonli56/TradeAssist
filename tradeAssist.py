import requests
import json
import datetime


class StockData:
    def __init__(self, date, open, high, low, close, volume):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.percentChange = 0.0
        self.gain = 0.0
        self.loss = 0.0
        self.avGain = 0.0
        self.avLoss = 0.0
        self.RS = 0.0
        self.RSI = 0.0
        # pos stands for position e.g. buy/sell
        self.initalPos = 0
        self.pos = 0
        self.balance = 0.0


def fetch_crypto_data(function, symbol):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': function,
        'symbol': symbol,
        'market': 'EUR',
        'apikey': 'V0JN0GYEV6PHMGTW'
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)

            stockMap = []
            # Convert JSON data into objects
            time_series = data["Time Series (Digital Currency Daily)"]
            for date, value in time_series.items():
                stock = StockData(date,
                                  float(value["1. open"]),
                                  float(value["2. high"]),
                                  float(value["3. low"]),
                                  float(value["4. close"]),
                                  float(value["5. volume"]))
                stockMap.append(stock)
            return stockMap
        else:
            # Handle API request errors
            print(f"API request failed with status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def fetch_stock_data(function, symbol):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': function,
        'symbol': symbol,
        'apikey': 'V0JN0GYEV6PHMGTW'
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)

            stockMap = []
            # Convert JSON data into objects
            time_series = data["Time Series (Daily)"]
            for date, value in time_series.items():
                stock = StockData(date,
                                  float(value["1. open"]),
                                  float(value["2. high"]),
                                  float(value["3. low"]),
                                  float(value["4. close"]),
                                  float(value["5. volume"]))
                stockMap.append(stock)
            return stockMap
        else:
            # Handle API request errors
            print(f"API request failed with status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def find_RSI(overbought, oversold, dayAv, function, symbol):
    if function == 'DIGITAL_CURRENCY_DAILY':
        prices = fetch_crypto_data(function, symbol)
    else:
        prices = fetch_stock_data(function, symbol)
    length = len(prices)

    prevClose = 0
    for count in range(length - 1, -1, -1):

        currStock = prices[count]
        # Calculate percent change
        if prevClose == 0:
            currStock.percentChange = 0
        else:
            currStock.percentChange = (currStock.close - prevClose) / prevClose

        # Calculate stock gain
        if prevClose == 0:
            currStock.gain = 0
        elif currStock.close > prevClose:
            currStock.gain = currStock.close - prevClose

        # Calculate stock loss
        if prevClose == 0:
            currStock.loss = 0
        elif prevClose > currStock.close:
            currStock.loss = prevClose - currStock.close

        # Skips the RSI calculations for the first 13 days
        prevClose = currStock.close
        if length - count <= dayAv:
            currStock.pos = 1
            currStock.balance = 100
            continue

        # Calculates Average Gain over 14 days
        totalGain = 0
        for i in range(count + 1, count + (dayAv + 1)):
            totalGain += prices[i].gain
        currStock.avGain = totalGain / dayAv

        # Calculates Average Loss over 14 days
        totalLoss = 0
        for i in range(count + 1, count + (dayAv + 1)):
            totalLoss += prices[i].loss
        currStock.avLoss = totalLoss / dayAv

        # Calculates RS and RSI
        currStock.RS = currStock.avGain / currStock.avLoss
        currStock.RSI = 100 - (100 / (1 + currStock.RS))

        # Finds inital postion using 70/30 RSI split
        if currStock.RSI > overbought:
            currStock.initalPos = -1
        elif currStock.RSI < oversold:
            currStock.initalPos = 1
        else:
            currStock.initalPos = 0

        # Finds position
        if currStock.initalPos == -1 * prices[count + 1].pos:
            currStock.pos = -1 * prices[count + 1].pos
        else:
            currStock.pos = prices[count + 1].pos

    strResult = ""
    data = []
    # Backtests and prints results
    for i in range(length - (dayAv + 1), -1, -1):
        currStock = prices[i]
        multiplier = 1 + (currStock.percentChange * prices[i + 1].pos)

        currStock.balance = prices[i + 1].balance * multiplier
        # print(currStock.balance)

        data.append({"date": currStock.date, "price": currStock.balance})

    return data
