def format_telegram_message(recommendations, global_data):
    try:
        message = "📊 Today's Trading Recommendations:\n\n"
        
        for rec in recommendations:
            symbol = rec['symbol']
            message += f"• <b>{symbol}</b>: ₹{rec['current_price']:.2f} ➡️ Target: ₹{rec['target_price']:.2f}\n"
            message += f"  RSI: {rec['rsi_14']:.1f} | SL: ₹{rec['stop_loss']:.2f}\n"
        
        message += f"\n<i>Updated at {global_data['last_updated'].strftime('%Y-%m-%d %H:%M')} IST</i>"
        message += "\n<i>Visit https://robot-pdwz.onrender.com/ for full analysis</i>"
        
        return message
    except Exception as e:
        logger.error(f"Error formatting Telegram message: {e}")
        return f"Error generating recommendations: {str(e)}"
# Flask routes
@app.route('/')
def index():
    """Main page with stock recommendations"""
    if not global_data['stock_recommendations']:
        return render_template('loading.html')
    
    return render_template(
        'index.html',
        recommendations=global_data['stock_recommendations'],
        last_updated=global_data['last_updated'],
        charts=global_data['charts']
    )

@app.route('/backtest')
def backtest():
    """Backtesting results page"""
    if not global_data['backtest_results']:
        return render_template('loading.html')
    
    return render_template(
        'backtest.html',
        backtest_results=global_data['backtest_results'],
        last_updated=global_data['last_updated']
    )

@app.route('/daily')
def daily():
    """Daily summary page"""
    if not global_data.get('daily_summary'):
        return render_template('no_summary.html')
    
    return render_template(
        'daily_summary.html',
        summary=global_data['daily_summary'],
        last_updated=global_data['last_updated']
    )

@app.route('/refresh')
def refresh():
    """Force refresh the data"""
    try:
        fetch_and_analyze_stocks()
        # Send updated recommendations to Telegram
        message = format_recommendations_for_telegram()
        send_to_channel(message)
        return "Data refreshed successfully. <a href='/'>Back to Home</a>"
    except Exception as e:
        return f"Error refreshing data: {str(e)}"

def create_template_files():
    """Create template files if not already present"""
    try:
        os.makedirs('templates', exist_ok=True)
        
   # Index template
index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty50 Stock Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .buy { color: green; font-weight: bold; }
        .sell { color: red; font-weight: bold; }
        .hold { color: orange; }
        .chart-container { height: 400px; overflow: hidden; margin-bottom: 20px; }
        .chart-img { width: 100%; object-fit: contain; max-height: 400px; }
        .card { margin-bottom: 20px; }
        .sticky-header { position: sticky; top: 0; background-color: white; z-index: 100; }
    </style>
</head>
<body>
"""
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Nifty50 Stock Analysis</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/backtest">Backtesting</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/daily">Daily Summary</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/refresh">Refresh Data</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4">Nifty50 Stock Analysis</h1>
                <p class="text-muted">Last updated: {{ last_updated.strftime('%Y-%m-%d %H:%M:%S') }} IST</p>
                
                <div class="alert alert-info">
                    <strong>Disclaimer:</strong> This tool provides technical analysis based on historical data. 
                    All recommendations are for informational purposes only and should not be considered financial advice.
                    Always do your own research before making investment decisions.
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Signal Summary</h5>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-4">
                                <h3 class="buy">{{ recommendations|selectattr('recommendation', 'eq', 'BUY')|list|length }}</h3>
                                <p>BUY Signals</p>
                            </div>
                            <div class="col-4">
                                <h3 class="sell">{{ recommendations|selectattr('recommendation', 'eq', 'SELL')|list|length }}</h3>
                                <p>SELL Signals</p>
                            </div>
                            <div class="col-4">
                                <h3 class="hold">{{ recommendations|selectattr('recommendation', 'eq', 'HOLD')|list|length }}</h3>
                                <p>HOLD Signals</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header sticky-header">
                        <ul class="nav nav-tabs card-header-tabs" id="myTab" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="buy-tab" data-bs-toggle="tab" data-bs-target="#buy" type="button" role="tab">BUY Signals</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="sell-tab" data-bs-toggle="tab" data-bs-target="#sell" type="button" role="tab">SELL Signals</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="all-tab" data-bs-toggle="tab" data-bs-target="#all" type="button" role="tab">All Stocks</button>
                            </li>
                        </ul>
                    </div>
                    <div class="card-body">
                        <div class="tab-content" id="myTabContent">
                            <!-- BUY Tab -->
                            <div class="tab-pane fade show active" id="buy" role="tabpanel">
                                <div class="table-responsive">
                                    <table class="table table-striped table-hover">
                                        <thead>
                                            <tr>
                                                <th>Symbol</th>
                                                <th>Current Price</th>
                                                <th>Change</th>
                                                <th>Target Price</th>
                                                <th>Stop Loss</th>
                                                <th>RSI (14)</th>
                                                <th>RSI (Weekly)</th>
                                                <th>RSI (Monthly)</th>
                                                <th>Reasoning</th>
                                                <th>Chart</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for rec in recommendations %}
                                                {% if rec.recommendation == 'BUY' %}
                                                <tr>
                                                    <td><strong>{{ rec.symbol }}</strong></td>
                                                    <td>₹{{ "%.2f"|format(rec.current_price) }}</td>
                                                    <td class="{{ 'text-success' if rec.percent_change > 0 else 'text-danger' }}">
                                                        {{ "%.2f"|format(rec.percent_change) }}%
                                                    </td>
                                                    <td class="text-success">₹{{ "%.2f"|format(rec.target_price) }}</td>
                                                    <td class="text-danger">₹{{ "%.2f"|format(rec.stop_loss) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_14) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_7) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_30) }}</td>
                                                    <td>
                                                        <ul class="mb-0 ps-3">
                                                            {% for reason in rec.reasoning %}
                                                                <li>{{ reason }}</li>
                                                            {% endfor %}
                                                        </ul>
                                                    </td>
                                                    <td>
                                                        {% if rec.symbol in charts %}
                                                            <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#chartModal{{ loop.index }}">
                                                                View Chart
                                                            </button>
                                                            
                                                            <!-- Chart Modal -->
                                                            <div class="modal fade" id="chartModal{{ loop.index }}" tabindex="-1">
                                                                <div class="modal-dialog modal-lg">
                                                                    <div class="modal-content">
                                                                        <div class="modal-header">
                                                                            <h5 class="modal-title">{{ rec.symbol }} Technical Analysis</h5>
                                                                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                                        </div>
                                                                        <div class="modal-body">
                                                                            <img src="data:image/png;base64,{{ charts[rec.symbol] }}" alt="{{ rec.symbol }} chart" class="img-fluid">
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        {% else %}
                                                            No chart
                                                        {% endif %}
                                                    </td>
                                                </tr>
                                                {% endif %}
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            
                            <!-- SELL Tab -->
                            <div class="tab-pane fade" id="sell" role="tabpanel">
                                <div class="table-responsive">
                                    <table class="table table-striped table-hover">
                                        <thead>
                                            <tr>
                                                <th>Symbol</th>
                                                <th>Current Price</th>
                                                <th>Change</th>
                                                <th>Target Price</th>
                                                <th>Stop Loss</th>
                                                <th>RSI (14)</th>
                                                <th>RSI (Weekly)</th>
                                                <th>RSI (Monthly)</th>
                                                <th>Reasoning</th>
                                                <th>Chart</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for rec in recommendations %}
                                                {% if rec.recommendation == 'SELL' %}
                                                <tr>
                                                    <td><strong>{{ rec.symbol }}</strong></td>
                                                    <td>₹{{ "%.2f"|format(rec.current_price) }}</td>
                                                    <td class="{{ 'text-success' if rec.percent_change > 0 else 'text-danger' }}">
                                                        {{ "%.2f"|format(rec.percent_change) }}%
                                                    </td>
                                                    <td class="text-danger">₹{{ "%.2f"|format(rec.target_price) }}</td>
                                                    <td class="text-warning">₹{{ "%.2f"|format(rec.stop_loss) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_14) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_7) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_30) }}</td>
                                                    <td>
                                                        <ul class="mb-0 ps-3">
                                                            {% for reason in rec.reasoning %}
                                                                <li>{{ reason }}</li>
                                                            {% endfor %}
                                                        </ul>
                                                    </td>
                                                    <td>
                                                        {% if rec.symbol in charts %}
                                                            <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#chartModal{{ loop.index }}">
                                                                View Chart
                                                            </button>
                                                            
                                                            <!-- Chart Modal -->
                                                            <div class="modal fade" id="chartModal{{ loop.index }}" tabindex="-1">
                                                                <div class="modal-dialog modal-lg">
                                                                    <div class="modal-content">
                                                                        <div class="modal-header">
                                                                            <h5 class="modal-title">{{ rec.symbol }} Technical Analysis</h5>
                                                                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                                        </div>
                                                                        <div class="modal-body">
                                                                            <img src="data:image/png;base64,{{ charts[rec.symbol] }}" alt="{{ rec.symbol }} chart" class="img-fluid">
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        {% else %}
                                                            No chart
                                                        {% endif %}
                                                    </td>
                                                </tr>
                                                {% endif %}
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            
                            <!-- All Stocks Tab -->
                            <div class="tab-pane fade" id="all" role="tabpanel">
                                <div class="table-responsive">
                                    <table class="table table-striped table-hover">
                                        <thead>
                                            <tr>
                                                <th>Symbol</th>
                                                <th>Recommendation</th>
                                                <th>Current Price</th>
                                                <th>Change</th>
                                                <th>RSI (14)</th>
                                                <th>RSI (Weekly)</th>
                                                <th>RSI (Monthly)</th>
                                                <th>Chart</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for rec in recommendations %}
                                                <tr>
                                                    <td><strong>{{ rec.symbol }}</strong></td>
                                                    <td class="
                                                        {% if rec.recommendation == 'BUY' %}buy
                                                        {% elif rec.recommendation == 'SELL' %}sell
                                                        {% else %}hold{% endif %}">
                                                        {{ rec.recommendation }}
                                                    </td>
                                                    <td>₹{{ "%.2f"|format(rec.current_price) }}</td>
                                                    <td class="{{ 'text-success' if rec.percent_change > 0 else 'text-danger' }}">
                                                        {{ "%.2f"|format(rec.percent_change) }}%
                                                    </td>
                                                    <td>{{ "%.1f"|format(rec.rsi_14) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_7) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_30) }}</td>
                                                    <td>
                                                        {% if rec.symbol in charts %}
                                                            <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#chartModal{{ loop.index }}">
                                                                View Chart
                                                            </button>
                                                            
                                                            <!-- Chart Modal -->
                                                            <div class="modal fade" id="chartModal{{ loop.index }}" tabindex="-1">
                                                                <div class="modal-dialog modal-lg">
                                                                    <div class="modal-content">
                                                                        <div class="modal-header">
                                                                            <h5 class="modal-title">{{ rec.symbol }} Technical Analysis</h5>
                                                                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                                        </div>
                                                                        <div class="modal-body">
                                                                            <img src="data:image/png;base64,{{ charts[rec.symbol] }}" alt="{{ rec.symbol }} chart" class="img-fluid">
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        {% else %}
                                                            No chart
                                                        {% endif %}
                                                    </td>
                                                </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-5">
        <div class="container">
            <p class="mb-0">© 2025 Nifty50 Stock Analysis | <a href="https://t.me/Stockniftybot" class="text-white">Join Telegram Channel</a></p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        
        with open('templates/index.html', 'w') as f:
            f.write(index_html)
        
        # Backtest template
        backtest_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backtesting Results - Nifty50 Stock Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .win-rate-good { color: green; font-weight: bold; }
        .win-rate-medium { color: orange; font-weight: bold; }
        .win-rate-poor { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Nifty50 Stock Analysis</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/backtest">Backtesting</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/daily">Daily Summary</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/refresh">Refresh Data</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4">Strategy Backtesting Results</h1>
                <p class="text-muted">Last updated: {{ last_updated.strftime('%Y-%m-%d %H:%M:%S') }} IST</p>
                
                <div class="alert alert-warning">
                    <strong>Disclaimer:</strong> Past performance is not indicative of future results. 
                    Backtesting results are based on historical data and may not accurately predict future market behavior.
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Backtesting Results</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>Symbol</th>
                                        <th>Test Period</th>
                                        <th>Total Trades</th>
                                        <th>Win Rate</th>
                                        <th>Avg Profit/Trade</th>
                                        <th>Buy & Hold Return</th>
                                        <th>Details</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for symbol, result in backtest_results.items() %}
                                        <tr>
                                            <td><strong>{{ symbol }}</strong></td>
                                            <td>{{ result.start_date }} to {{ result.end_date }}</td>
                                            <td>{{ result.total_trades }}</td>
                                            <td class="
                                                {% if result.win_rate >= 60 %}win-rate-good
                                                {% elif result.win_rate >= 45 %}win-rate-medium
                                                {% else %}win-rate-poor{% endif %}">
                                                {{ "%.1f"|format(result.win_rate) }}%
                                            </td>
                                            <td class="{{ 'text-success' if result.avg_profit_per_trade > 0 else 'text-danger' }}">
                                                {{ "%.2f"|format(result.avg_profit_per_trade) }}%
                                            </td>
                                            <td class="{{ 'text-success' if result.buy_hold_return > 0 else 'text-danger' }}">
                                                {{ "%.2f"|format(result.buy_hold_return) }}%
                                            </td>
                                            <td>
                                                <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#detailsModal{{ loop.index }}">
                                                    View Trades
                                                </button>
                                                
                                                <!-- Details Modal -->
                                                <div class="modal fade" id="detailsModal{{ loop.index }}" tabindex="-1">
                                                    <div class="modal-dialog modal-lg">
                                                        <div class="modal-content">
                                                            <div class="modal-header">
                                                                <h5 class="modal-title">{{ symbol }} Trade Details</h5>
                                                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                            </div>
                                                            <div class="modal-body">
                                                                <h6>Strategy Performance:</h6>
                                                                <ul>
                                                                    <li>Win Rate: {{ "%.1f"|format(result.win_rate) }}%</li>
                                                                    <li>Average Profit per Trade: {{ "%.2f"|format(result.avg_profit_per_trade) }}%</li>
                                                                    <li>Buy & Hold Return: {{ "%.2f"|format(result.buy_hold_return) }}%</li>
                                                                </ul>
                                                                
                                                                {% if result.trades %}
                                                                <h6>Sample Trades:</h6>
                                                                <div class="table-responsive">
                                                                    <table class="table table-sm">
                                                                        <thead>
                                                                            <tr>
                                                                                <th>Entry Date</th>
                                                                                <th>Entry Price</th>
                                                                                <th>Exit Date</th>
                                                                                <th>Exit Price</th>
                                                                                <th>Profit/Loss</th>
                                                                            </tr>
                                                                        </thead>
                                                                        <tbody>
                                                                            {% for trade in result.trades %}
                                                                                <tr>
                                                                                    <td>{{ trade.entry_date }}</td>
                                                                                    <td>₹{{ "%.2f"|format(trade.entry_price) }}</td>
                                                                                    <td>{{ trade.exit_date }}</td>
                                                                                    <td>₹{{ "%.2f"|format(trade.exit_price) }}</td>
                                                                                    <td class="{{ 'text-success' if trade.profit_pct > 0 else 'text-danger' }}">
                                                                                        {{ "%.2f"|format(trade.profit_pct) }}%
                                                                                    </td>
                                                                                </tr>
                                                                            {% endfor %}
                                                                        </tbody>
                                                                    </table>
                                                                </div>
                                                                {% else %}
                                                                <p>No trade details available.</p>
                                                                {% endif %}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">Strategy Description</h5>
                    </div>
                    <div class="card-body">
                        <h5>Technical Indicators Used:</h5>
                        <ul>
                            <li><strong>RSI (Relative Strength Index):</strong> Buy when RSI < 30 (oversold), Sell when RSI > 70 (overbought)</li>
                            <li><strong>MACD (Moving Average Convergence Divergence):</strong> Buy on MACD crossing above Signal line, Sell on crossing below</li>
                            <li><strong>Moving Averages:</strong> Buy when price above SMA20 and SMA50, Sell when below</li>
                            <li><strong>Stochastic Oscillator:</strong> Buy when %K and %D < 20, Sell when %K and %D > 80</li>
                        </ul>
                        
                        <h5>Trading Rules:</h5>
                        <ol>
                            <li>Enter position when at least 2 buy signals are triggered</li>
                            <li>Exit position when at least 2 sell signals are triggered</li>
                            <li>Use 3-5% stop loss (adjusted based on volatility)</li>
                            <li>Target 5-8% profit (adjusted based on Fibonacci retracement levels)</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-5">
        <div class="container">
            <p class="mb-0">© 2025 Nifty50 Stock Analysis | <a href="https://t.me/Stockniftybot" class="text-white">Join Telegram Channel</a></p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        
        with open('templates/backtest.html', 'w') as f:
            f.write(backtest_html)
        
        # Daily summary template
        daily_summary_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Market Summary - Nifty50 Stock Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .buy { color: green; font-weight: bold; }
        .sell { color: red; font-weight: bold; }
        .hold { color: orange; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Nifty50 Stock Analysis</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
message += f"• <b>{symbol}</b>: ₹{rec['current_price']:.2f} ➡️ Target: ₹{rec['target_price']:.2f}\n"
                    message += f"  RSI: {rec['rsi_14']:.1f} | SL: ₹{rec['stop_loss']:.2f}\n"
        
        message += f"\n<i>Updated at {global_data['last_updated'].strftime('%Y-%m-%d %H:%M')} IST</i>"
        message += "\n<i>Visit https://robot-pdwz.onrender.com/ for full analysis</i>"
        
        return message
    except Exception as e:
        logger.error(f"Error formatting Telegram message: {e}")
        return f"Error generating recommendations: {str(e)}"

# Flask routes
@app.route('/')
def index():
    """Main page with stock recommendations"""
    if not global_data['stock_recommendations']:
        return render_template('loading.html')
    
    return render_template(
        'index.html',
        recommendations=global_data['stock_recommendations'],
        last_updated=global_data['last_updated'],
        charts=global_data['charts']
    )

@app.route('/backtest')
def backtest():
    """Backtesting results page"""
    if not global_data['backtest_results']:
        return render_template('loading.html')
    
    return render_template(
        'backtest.html',
        backtest_results=global_data['backtest_results'],
        last_updated=global_data['last_updated']
    )

@app.route('/daily')
def daily():
    """Daily summary page"""
    if not global_data.get('daily_summary'):
        return render_template('no_summary.html')
    
    return render_template(
        'daily_summary.html',
        summary=global_data['daily_summary'],
        last_updated=global_data['last_updated']
    )

@app.route('/refresh')
def refresh():
    """Force refresh the data"""
    try:
        fetch_and_analyze_stocks()
        # Send updated recommendations to Telegram
        message = format_recommendations_for_telegram()
        send_to_channel(message)
        return "Data refreshed successfully. <a href='/'>Back to Home</a>"
    except Exception as e:
        return f"Error refreshing data: {str(e)}"

def create_template_files():
    """Create template files if not already present"""
    try:
        os.makedirs('templates', exist_ok=True)
        
        # Index template
        index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty50 Stock Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .buy { color: green; font-weight: bold; }
        .sell { color: red; font-weight: bold; }
        .hold { color: orange; }
        .chart-container { height: 400px; overflow: hidden; margin-bottom: 20px; }
        .chart-img { width: 100%; object-fit: contain; max-height: 400px; }
        .card { margin-bottom: 20px; }
        .sticky-header { position: sticky; top: 0; background-color: white; z-index: 100; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Nifty50 Stock Analysis</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/backtest">Backtesting</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/daily">Daily Summary</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/refresh">Refresh Data</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4">Nifty50 Stock Analysis</h1>
                <p class="text-muted">Last updated: {{ last_updated.strftime('%Y-%m-%d %H:%M:%S') }} IST</p>
                
                <div class="alert alert-info">
                    <strong>Disclaimer:</strong> This tool provides technical analysis based on historical data. 
                    All recommendations are for informational purposes only and should not be considered financial advice.
                    Always do your own research before making investment decisions.
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Signal Summary</h5>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-4">
                                <h3 class="buy">{{ recommendations|selectattr('recommendation', 'eq', 'BUY')|list|length }}</h3>
                                <p>BUY Signals</p>
                            </div>
                            <div class="col-4">
                                <h3 class="sell">{{ recommendations|selectattr('recommendation', 'eq', 'SELL')|list|length }}</h3>
                                <p>SELL Signals</p>
                            </div>
                            <div class="col-4">
                                <h3 class="hold">{{ recommendations|selectattr('recommendation', 'eq', 'HOLD')|list|length }}</h3>
                                <p>HOLD Signals</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header sticky-header">
                        <ul class="nav nav-tabs card-header-tabs" id="myTab" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="buy-tab" data-bs-toggle="tab" data-bs-target="#buy" type="button" role="tab">BUY Signals</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="sell-tab" data-bs-toggle="tab" data-bs-target="#sell" type="button" role="tab">SELL Signals</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="all-tab" data-bs-toggle="tab" data-bs-target="#all" type="button" role="tab">All Stocks</button>
                            </li>
                        </ul>
                    </div>
                    <div class="card-body">
                        <div class="tab-content" id="myTabContent">
                            <!-- BUY Tab -->
                            <div class="tab-pane fade show active" id="buy" role="tabpanel">
                                <div class="table-responsive">
                                    <table class="table table-striped table-hover">
                                        <thead>
                                            <tr>
                                                <th>Symbol</th>
                                                <th>Current Price</th>
                                                <th>Change</th>
                                                <th>Target Price</th>
                                                <th>Stop Loss</th>
                                                <th>RSI (14)</th>
                                                <th>RSI (Weekly)</th>
                                                <th>RSI (Monthly)</th>
                                                <th>Reasoning</th>
                                                <th>Chart</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for rec in recommendations %}
                                                {% if rec.recommendation == 'BUY' %}
                                                <tr>
                                                    <td><strong>{{ rec.symbol }}</strong></td>
                                                    <td>₹{{ "%.2f"|format(rec.current_price) }}</td>
                                                    <td class="{{ 'text-success' if rec.percent_change > 0 else 'text-danger' }}">
                                                        {{ "%.2f"|format(rec.percent_change) }}%
                                                    </td>
                                                    <td class="text-success">₹{{ "%.2f"|format(rec.target_price) }}</td>
                                                    <td class="text-danger">₹{{ "%.2f"|format(rec.stop_loss) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_14) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_7) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_30) }}</td>
                                                    <td>
                                                        <ul class="mb-0 ps-3">
                                                            {% for reason in rec.reasoning %}
                                                                <li>{{ reason }}</li>
                                                            {% endfor %}
                                                        </ul>
                                                    </td>
                                                    <td>
                                                        {% if rec.symbol in charts %}
                                                            <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#chartModal{{ loop.index }}">
                                                                View Chart
                                                            </button>
                                                            
                                                            <!-- Chart Modal -->
                                                            <div class="modal fade" id="chartModal{{ loop.index }}" tabindex="-1">
                                                                <div class="modal-dialog modal-lg">
                                                                    <div class="modal-content">
                                                                        <div class="modal-header">
                                                                            <h5 class="modal-title">{{ rec.symbol }} Technical Analysis</h5>
                                                                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                                        </div>
                                                                        <div class="modal-body">
                                                                            <img src="data:image/png;base64,{{ charts[rec.symbol] }}" alt="{{ rec.symbol }} chart" class="img-fluid">
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        {% else %}
                                                            No chart
                                                        {% endif %}
                                                    </td>
                                                </tr>
                                                {% endif %}
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            
                            <!-- SELL Tab -->
                            <div class="tab-pane fade" id="sell" role="tabpanel">
                                <div class="table-responsive">
                                    <table class="table table-striped table-hover">
                                        <thead>
                                            <tr>
                                                <th>Symbol</th>
                                                <th>Current Price</th>
                                                <th>Change</th>
                                                <th>Target Price</th>
                                                <th>Stop Loss</th>
                                                <th>RSI (14)</th>
                                                <th>RSI (Weekly)</th>
                                                <th>RSI (Monthly)</th>
                                                <th>Reasoning</th>
                                                <th>Chart</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for rec in recommendations %}
                                                {% if rec.recommendation == 'SELL' %}
                                                <tr>
                                                    <td><strong>{{ rec.symbol }}</strong></td>
                                                    <td>₹{{ "%.2f"|format(rec.current_price) }}</td>
                                                    <td class="{{ 'text-success' if rec.percent_change > 0 else 'text-danger' }}">
                                                        {{ "%.2f"|format(rec.percent_change) }}%
                                                    </td>
                                                    <td class="text-danger">₹{{ "%.2f"|format(rec.target_price) }}</td>
                                                    <td class="text-warning">₹{{ "%.2f"|format(rec.stop_loss) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_14) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_7) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_30) }}</td>
                                                    <td>
                                                        <ul class="mb-0 ps-3">
                                                            {% for reason in rec.reasoning %}
                                                                <li>{{ reason }}</li>
                                                            {% endfor %}
                                                        </ul>
                                                    </td>
                                                    <td>
                                                        {% if rec.symbol in charts %}
                                                            <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#chartModal{{ loop.index }}">
                                                                View Chart
                                                            </button>
                                                            
                                                            <!-- Chart Modal -->
                                                            <div class="modal fade" id="chartModal{{ loop.index }}" tabindex="-1">
                                                                <div class="modal-dialog modal-lg">
                                                                    <div class="modal-content">
                                                                        <div class="modal-header">
                                                                            <h5 class="modal-title">{{ rec.symbol }} Technical Analysis</h5>
                                                                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                                        </div>
                                                                        <div class="modal-body">
                                                                            <img src="data:image/png;base64,{{ charts[rec.symbol] }}" alt="{{ rec.symbol }} chart" class="img-fluid">
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        {% else %}
                                                            No chart
                                                        {% endif %}
                                                    </td>
                                                </tr>
                                                {% endif %}
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            
                            <!-- All Stocks Tab -->
                            <div class="tab-pane fade" id="all" role="tabpanel">
                                <div class="table-responsive">
                                    <table class="table table-striped table-hover">
                                        <thead>
                                            <tr>
                                                <th>Symbol</th>
                                                <th>Recommendation</th>
                                                <th>Current Price</th>
                                                <th>Change</th>
                                                <th>RSI (14)</th>
                                                <th>RSI (Weekly)</th>
                                                <th>RSI (Monthly)</th>
                                                <th>Chart</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for rec in recommendations %}
                                                <tr>
                                                    <td><strong>{{ rec.symbol }}</strong></td>
                                                    <td class="
                                                        {% if rec.recommendation == 'BUY' %}buy
                                                        {% elif rec.recommendation == 'SELL' %}sell
                                                        {% else %}hold{% endif %}">
                                                        {{ rec.recommendation }}
                                                    </td>
                                                    <td>₹{{ "%.2f"|format(rec.current_price) }}</td>
                                                    <td class="{{ 'text-success' if rec.percent_change > 0 else 'text-danger' }}">
                                                        {{ "%.2f"|format(rec.percent_change) }}%
                                                    </td>
                                                    <td>{{ "%.1f"|format(rec.rsi_14) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_7) }}</td>
                                                    <td>{{ "%.1f"|format(rec.rsi_30) }}</td>
                                                    <td>
                                                        {% if rec.symbol in charts %}
                                                            <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#chartModal{{ loop.index }}">
                                                                View Chart
                                                            </button>
                                                            
                                                            <!-- Chart Modal -->
                                                            <div class="modal fade" id="chartModal{{ loop.index }}" tabindex="-1">
                                                                <div class="modal-dialog modal-lg">
                                                                    <div class="modal-content">
                                                                        <div class="modal-header">
                                                                            <h5 class="modal-title">{{ rec.symbol }} Technical Analysis</h5>
                                                                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                                        </div>
                                                                        <div class="modal-body">
                                                                            <img src="data:image/png;base64,{{ charts[rec.symbol] }}" alt="{{ rec.symbol }} chart" class="img-fluid">
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        {% else %}
                                                            No chart
                                                        {% endif %}
                                                    </td>
                                                </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-5">
        <div class="container">
            <p class="mb-0">© 2025 Nifty50 Stock Analysis | <a href="https://t.me/Stockniftybot" class="text-white">Join Telegram Channel</a></p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        
        with open('templates/index.html', 'w') as f:
            f.write(index_html)
        
        # Backtest template
        backtest_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backtesting Results - Nifty50 Stock Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .win-rate-good { color: green; font-weight: bold; }
        .win-rate-medium { color: orange; font-weight: bold; }
        .win-rate-poor { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Nifty50 Stock Analysis</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/backtest">Backtesting</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/daily">Daily Summary</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/refresh">Refresh Data</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4">Strategy Backtesting Results</h1>
                <p class="text-muted">Last updated: {{ last_updated.strftime('%Y-%m-%d %H:%M:%S') }} IST</p>
                
                <div class="alert alert-warning">
                    <strong>Disclaimer:</strong> Past performance is not indicative of future results. 
                    Backtesting results are based on historical data and may not accurately predict future market behavior.
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Backtesting Results</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>Symbol</th>
                                        <th>Test Period</th>
                                        <th>Total Trades</th>
                                        <th>Win Rate</th>
                                        <th>Avg Profit/Trade</th>
                                        <th>Buy & Hold Return</th>
                                        <th>Details</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for symbol, result in backtest_results.items() %}
                                        <tr>
                                            <td><strong>{{ symbol }}</strong></td>
                                            <td>{{ result.start_date }} to {{ result.end_date }}</td>
                                            <td>{{ result.total_trades }}</td>
                                            <td class="
                                                {% if result.win_rate >= 60 %}win-rate-good
                                                {% elif result.win_rate >= 45 %}win-rate-medium
                                                {% else %}win-rate-poor{% endif %}">
                                                {{ "%.1f"|format(result.win_rate) }}%
                                            </td>
                                            <td class="{{ 'text-success' if result.avg_profit_per_trade > 0 else 'text-danger' }}">
                                                {{ "%.2f"|format(result.avg_profit_per_trade) }}%
                                            </td>
                                            <td class="{{ 'text-success' if result.buy_hold_return > 0 else 'text-danger' }}">
                                                {{ "%.2f"|format(result.buy_hold_return) }}%
                                            </td>
                                            <td>
                                                <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#detailsModal{{ loop.index }}">
                                                    View Trades
                                                </button>
                                                
                                                <!-- Details Modal -->
                                                <div class="modal fade" id="detailsModal{{ loop.index }}" tabindex="-1">
                                                    <div class="modal-dialog modal-lg">
                                                        <div class="modal-content">
                                                            <div class="modal-header">
                                                                <h5 class="modal-title">{{ symbol }} Trade Details</h5>
                                                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                            </div>
                                                            <div class="modal-body">
                                                                <h6>Strategy Performance:</h6>
                                                                <ul>
                                                                    <li>Win Rate: {{ "%.1f"|format(result.win_rate) }}%</li>
                                                                    <li>Average Profit per Trade: {{ "%.2f"|format(result.avg_profit_per_trade) }}%</li>
                                                                    <li>Buy & Hold Return: {{ "%.2f"|format(result.buy_hold_return) }}%</li>
                                                                </ul>
                                                                
                                                                {% if result.trades %}
                                                                <h6>Sample Trades:</h6>
                                                                <div class="table-responsive">
                                                                    <table class="table table-sm">
                                                                        <thead>
                                                                            <tr>
                                                                                <th>Entry Date</th>
                                                                                <th>Entry Price</th>
                                                                                <th>Exit Date</th>
                                                                                <th>Exit Price</th>
                                                                                <th>Profit/Loss</th>
                                                                            </tr>
                                                                        </thead>
                                                                        <tbody>
                                                                            {% for trade in result.trades %}
                                                                                <tr>
                                                                                    <td>{{ trade.entry_date }}</td>
                                                                                    <td>₹{{ "%.2f"|format(trade.entry_price) }}</td>
                                                                                    <td>{{ trade.exit_date }}</td>
                                                                                    <td>₹{{ "%.2f"|format(trade.exit_price) }}</td>
                                                                                    <td class="{{ 'text-success' if trade.profit_pct > 0 else 'text-danger' }}">
                                                                                        {{ "%.2f"|format(trade.profit_pct) }}%
                                                                                    </td>
                                                                                </tr>
                                                                            {% endfor %}
                                                                        </tbody>
                                                                    </table>
                                                                </div>
                                                                {% else %}
                                                                <p>No trade details available.</p>
                                                                {% endif %}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">Strategy Description</h5>
                    </div>
                    <div class="card-body">
                        <h5>Technical Indicators Used:</h5>
                        <ul>
                            <li><strong>RSI (Relative Strength Index):</strong> Buy when RSI < 30 (oversold), Sell when RSI > 70 (overbought)</li>
                            <li><strong>MACD (Moving Average Convergence Divergence):</strong> Buy on MACD crossing above Signal line, Sell on crossing below</li>
                            <li><strong>Moving Averages:</strong> Buy when price above SMA20 and SMA50, Sell when below</li>
                            <li><strong>Stochastic Oscillator:</strong> Buy when %K and %D < 20, Sell when %K and %D > 80</li>
                        </ul>
                        
                        <h5>Trading Rules:</h5>
                        <ol>
                            <li>Enter position when at least 2 buy signals are triggered</li>
                            <li>Exit position when at least 2 sell signals are triggered</li>
                            <li>Use 3-5% stop loss (adjusted based on volatility)</li>
                            <li>Target 5-8% profit (adjusted based on Fibonacci retracement levels)</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-5">
        <div class="container">
            <p class="mb-0">© 2025 Nifty50 Stock Analysis | <a href="https://t.me/Stockniftybot" class="text-white">Join Telegram Channel</a></p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        
        with open('templates/backtest.html', 'w') as f:
            f.write(backtest_html)
        
        # Daily summary template
        daily_summary_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Market Summary - Nifty50 Stock Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .buy { color: green; font-weight: bold; }
        .sell { color: red; font-weight: bold; }
        .hold { color: orange; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Nifty50 Stock Analysis</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
<a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/backtest">Backtesting</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/daily">Daily Summary</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/refresh">Refresh Data</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4">Daily Market Summary</h1>
                <p class="text-muted">Last updated: {{ last_updated.strftime('%Y-%m-%d %H:%M:%S') }} IST</p>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Market Overview</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h5>Nifty50 Index</h5>
                                <p>Current Value: {{ summary.nifty50_value }}</p>
                                <p class="{{ 'text-success' if summary.nifty50_change > 0 else 'text-danger' }}">
                                    Change: {{ summary.nifty50_change }} ({{ summary.nifty50_change_pct }}%)
                                </p>
                                <p>Market Condition: <strong>{{ summary.market_condition }}</strong></p>
                            </div>
                            <div class="col-md-6">
                                <h5>Sector Performance</h5>
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Sector</th>
                                            <th>Change</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for sector in summary.sector_performance %}
                                            <tr>
                                                <td>{{ sector.name }}</td>
                                                <td class="{{ 'text-success' if sector.change > 0 else 'text-danger' }}">
                                                    {{ sector.change }}%
                                                </td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">Top Gainers and Losers</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h5>Top Gainers</h5>
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Symbol</th>
                                            <th>Current Price</th>
                                            <th>Change</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for stock in summary.top_gainers %}
                                            <tr>
                                                <td><strong>{{ stock.symbol }}</strong></td>
                                                <td>₹{{ "%.2f"|format(stock.price) }}</td>
                                                <td class="text-success">+{{ "%.2f"|format(stock.change_pct) }}%</td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h5>Top Losers</h5>
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Symbol</th>
                                            <th>Current Price</th>
                                            <th>Change</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for stock in summary.top_losers %}
                                            <tr>
                                                <td><strong>{{ stock.symbol }}</strong></td>
                                                <td>₹{{ "%.2f"|format(stock.price) }}</td>
                                                <td class="text-danger">{{ "%.2f"|format(stock.change_pct) }}%</td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">Market Analysis</h5>
                    </div>
                    <div class="card-body">
                        <h5>Technical Analysis Summary</h5>
                        <div class="mb-4">
                            {{ summary.technical_analysis|safe }}
                        </div>
                        
                        <h5>Market Sentiment</h5>
                        <div class="progress mb-3">
                            <div class="progress-bar bg-success" role="progressbar" style="width: {{ summary.bullish_percentage }}%">
                                Bullish: {{ summary.bullish_percentage }}%
                            </div>
                            <div class="progress-bar bg-warning" role="progressbar" style="width: {{ summary.neutral_percentage }}%">
                                Neutral: {{ summary.neutral_percentage }}%
                            </div>
                            <div class="progress-bar bg-danger" role="progressbar" style="width: {{ summary.bearish_percentage }}%">
                                Bearish: {{ summary.bearish_percentage }}%
                            </div>
                        </div>
                        
                        <h5>Key Observations</h5>
                        <ul>
                            {% for observation in summary.key_observations %}
                                <li>{{ observation }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h5 class="mb-0">News Impact</h5>
                    </div>
                    <div class="card-body">
                        <h5>Market-Moving News</h5>
                        <ul>
                            {% for news in summary.market_news %}
                                <li>
                                    <strong>{{ news.title }}</strong><br>
                                    <span class="text-muted">{{ news.source }} - {{ news.time }}</span><br>
                                    <span>{{ news.impact }}</span>
                                </li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-5">
        <div class="container">
            <p class="mb-0">© 2025 Nifty50 Stock Analysis | <a href="https://t.me/Stockniftybot" class="text-white">Join Telegram Channel</a></p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        
        with open('templates/daily_summary.html', 'w') as f:
            f.write(daily_summary_html)
        
        # Loading template
        loading_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading... - Nifty50 Stock Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .loader {
            border: 16px solid #f3f3f3;
            border-radius: 50%;
            border-top: 16px solid #3498db;
            width: 120px;
            height: 120px;
            animation: spin 2s linear infinite;
            margin: 50px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    <script>
        function refreshPage() {
            setTimeout(function() {
                window.location.reload();
            }, 10000); // Refresh every 10 seconds
        }
        window.onload = refreshPage;
    </script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Nifty50 Stock Analysis</a>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row">
            <div class="col-12 text-center">
                <h1 class="mb-4">Loading Data...</h1>
                <div class="loader"></div>
                <p class="mt-4">Please wait while we fetch and analyze the latest market data.</p>
                <p class="text-muted">This page will automatically refresh every 10 seconds.</p>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-5 fixed-bottom">
        <div class="container">
            <p class="mb-0">© 2025 Nifty50 Stock Analysis</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        
        with open('templates/loading.html', 'w') as f:
            f.write(loading_html)
        
        # No summary template
        no_summary_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>No Summary Available - Nifty50 Stock Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Nifty50 Stock Analysis</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/backtest">Backtesting</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/daily">Daily Summary</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/refresh">Refresh Data</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row">
            <div class="col-12 text-center">
                <h1 class="mb-4">No Daily Summary Available</h1>
                <p>The daily market summary has not been generated yet.</p>
                <p>Please check back after market hours when the summary will be available.</p>
                <a href="/refresh" class="btn btn-primary mt-3">Refresh Data</a>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-5 fixed-bottom">
        <div class="container">
            <p class="mb-0">© 2025 Nifty50 Stock Analysis | <a href="https://t.me/Stockniftybot" class="text-white">Join Telegram Channel</a></p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        
        with open('templates/no_summary.html', 'w') as f:
            f.write(no_summary_html)
            
        logger.info("Template files created successfully")
    except Exception as e:
        logger.error(f"Error creating template files: {e}")

def initialize_sample_data():
    """Create sample data for initial display"""
    try:
        # Sample recommendations
        sample_recommendations = [
            {
                "symbol": "RELIANCE",
                "recommendation": "BUY",
                "current_price": 2450.75,
                "percent_change": 1.25,
                "target_price": 2600.00,
                "stop_loss": 2350.00,
                "rsi_14": 62.5,
                "rsi_7": 65.3,
                "rsi_30": 58.7,
                "reasoning": [
                    "Bullish MACD crossover",
                    "Price above 50-day SMA",
                    "Support at recent higher low"
                ]
            },
            {
                "symbol": "INFY",
                "recommendation": "SELL",
                "current_price": 1750.25,
                "percent_change": -0.75,
                "target_price": 1650.00,
                "stop_loss": 1820.00,
                "rsi_14": 72.3,
                "rsi_7": 75.5,
                "rsi_30": 68.2,
                "reasoning": [
                    "Bearish divergence on RSI",
                    "Price below 20-day SMA",
                    "Volume decreasing on rallies"
                ]
            },
            {
                "symbol": "HDFCBANK",
                "recommendation": "HOLD",
                "current_price": 1650.50,
                "percent_change": 0.15,
                "target_price": 1700.00,
                "stop_loss": 1600.00,
                "rsi_14": 54.2,
                "rsi_7": 52.8,
                "rsi_30": 56.5,
                "reasoning": [
                    "Consolidating in range",
                    "Neutral RSI readings",
                    "Waiting for breakout confirmation"
                ]
            }
        ]
        
        # Sample backtest results
        sample_backtest_results = {
            "RELIANCE": {
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "total_trades": 24,
                "win_rate": 62.5,
                "avg_profit_per_trade": 3.75,
                "buy_hold_return": 15.2,
                "trades": [
                    {
                        "entry_date": "2023-01-15",
                        "entry_price": 2200.00,
                        "exit_date": "2023-02-05",
                        "exit_price": 2310.00,
                        "profit_pct": 5.0
                    },
                    {
                        "entry_date": "2023-03-10",
                        "entry_price": 2280.00,
                        "exit_date": "2023-03-28",
                        "exit_price": 2350.00,
                        "profit_pct": 3.07
                    },
                    {
                        "entry_date": "2023-05-22",
                        "entry_price": 2400.00,
                        "exit_date": "2023-06-05",
                        "exit_price": 2320.00,
                        "profit_pct": -3.33
                    }
                ]
            },
            "INFY": {
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "total_trades": 18,
                "win_rate": 55.6,
                "avg_profit_per_trade": 2.45,
                "buy_hold_return": 8.7,
                "trades": [
                    {
                        "entry_date": "2023-02-10",
                        "entry_price": 1500.00,
                        "exit_date": "2023-03-01",
                        "exit_price": 1560.00,
                        "profit_pct": 4.0
                    },
                    {
                        "entry_date": "2023-04-15",
                        "entry_price": 1620.00,
                        "exit_date": "2023-05-02",
                        "exit_price": 1580.00,
                        "profit_pct": -2.47
                    }
                ]
            }
        }
        
        # Sample daily summary
        sample_daily_summary = {
            "nifty50_value": 22150.75,
            "nifty50_change": 156.25,
            "nifty50_change_pct": 0.71,
            "market_condition": "Bullish",
            "sector_performance": [
                {"name": "IT", "change": 1.2},
                {"name": "Banking", "change": 0.8},
                {"name": "Pharma", "change": -0.3},
                {"name": "Auto", "change": 1.5},
                {"name": "Energy", "change": 0.5}
            ],
            "top_gainers": [
                {"symbol": "TATAMOTORS", "price": 875.50, "change_pct": 3.75},
                {"symbol": "TECHM", "price": 1420.25, "change_pct": 2.85},
                {"symbol": "BAJFINANCE", "price": 7250.00, "change_pct": 2.35}
            ],
            "top_losers": [
                {"symbol": "SUNPHARMA", "price": 1180.75, "change_pct": -1.25},
                {"symbol": "ONGC", "price": 245.30, "change_pct": -0.85},
                {"symbol": "HINDALCO", "price": 560.20, "change_pct": -0.65}
            ],
            "technical_analysis": "<p>The Nifty50 index continues its upward momentum, breaking above the previous resistance at 22000. Technical indicators suggest a bullish short-term outlook with the index trading above both the 20 and 50-day moving averages. The RSI stands at 63.5, indicating strong momentum without reaching overbought territory yet.</p>",
            "bullish_percentage": 60,
            "neutral_percentage": 25,
            "bearish_percentage": 15,
            "key_observations": [
                "Market breadth is positive with advancing stocks outnumbering declining ones",
                "Volume has picked up in the last 3 trading sessions",
                "IT and Auto sectors showing strong momentum",
                "Nifty is above all major moving averages"
            ],
            "market_news": [
                {
                    "title": "RBI Maintains Repo Rate at 6.5%",
                    "source": "Economic Times",
                    "time": "10:30 AM",
                    "impact": "Markets reacted positively as the decision was in line with expectations. Banking stocks showed mixed reactions."
                },
                {
                    "title": "Q4 Results: Tech Companies Beat Estimates",
                    "source": "Business Standard",
                    "time": "9:15 AM",
                    "impact": "IT sector rallied on strong results and positive guidance from major companies."
                }
            ]
        }
        
        # Update global data with sample data
        global_data["stock_recommendations"] = sample_recommendations
        global_data["backtest_results"] = sample_backtest_results
        global_data["daily_summary"] = sample_daily_summary
        global_data["last_updated"] = datetime.now()
        
        logger.info("Sample data initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing sample data: {e}")

if __name__ == "__main__":
    try:
        # Create template files
        create_template_files()
        
        # Initialize with sample data
        initialize_sample_data()
        
        # Schedule data refresh
        schedule.every().day.at("09:20").do(fetch_and_analyze_stocks)  # Market opening time
        schedule.every().day.at("15:40").do(fetch_and_analyze_stocks)  # Close to market closing time
        schedule.every().day.at("18:00").do(generate_daily_summary)    # After market hours
        
        # Schedule Telegram updates
        schedule.every().day.at("09:30").do(send_telegram_update)      # Morning update
        schedule.every().day.at("12:30").do(send_telegram_update)      # Mid-day update
        schedule.every().day.at("16:00").do(send_telegram_update)      # Closing update
        
        # Fetch data on startup
        threading.Thread(target=fetch_and_analyze_stocks).start()
        
        # Run the scheduler in a separate thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
    except Exception as e:
        logger.critical(f"Critical error during startup: {e}")
