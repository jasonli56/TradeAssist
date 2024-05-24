from flask import Flask, render_template, request
import tradeAssist

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/hello', methods=['GET'])
def hello():
    return "hello jason"


@app.route('/backtest', methods=['POST'])
def backtest():
    overbought = int(request.form['overbought'])
    oversold = int(request.form['oversold'])
    dayAverage = int(request.form['dayAverage'])
    function = request.form['function']
    symbol = request.form['symbol']

    # Call tradeAssist to get backtest results
    result = tradeAssist.find_RSI(overbought, oversold, dayAverage, function, symbol)

    # Call templates to display results
    return render_template('results.html', data=result)

if __name__ == '__main__':
    app.run(debug=True)