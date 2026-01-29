import MetaTrader5 as mt5
import config_vps

def inizializza_mt5():
    """Initializes the connection to the MT5 terminal."""
    if not mt5.initialize():
        print("❌ MT5 Initialization failed")
        return False
    print("✅ Connected to MetaTrader 5")
    return True

def apri_operazione(discord_symbol, order_type, sl, tp):
    """Sends a trade request to MT5 based on parsed signal data."""
    # Get the broker-specific symbol from the map
    broker_symbol = config_vps.SYMBOL_MAP.get(discord_symbol, discord_symbol)
    
    # Ensure symbol is visible in Market Watch
    mt5.symbol_select(broker_symbol, True)
    tick = mt5.symbol_info_tick(broker_symbol)
    
    if tick is None:
        return type('obj', (object,), {'retcode': -1, 'comment': 'Symbol not found'})

    # Define order type and entry price
    m_type = mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL
    price = tick.ask if order_type == "BUY" else tick.bid

    # Build the trade request dictionary
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": broker_symbol,
        "volume": config_vps.LOTTO_DEFAULT,
        "type": m_type,
        "price": price,
        "sl": float(sl) if sl != 0 else 0.0,
        "tp": float(tp) if tp != 0 else 0.0,
        "magic": config_vps.MAGIC_NUMBER,
        "comment": "Python Auto Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC, # Change to FOK if your broker requires it
    }

    return mt5.order_send(request)

def chiudi_operazioni_simbolo(discord_symbol):
    """Closes all open positions for a specific symbol with the bot's magic number."""
    broker_symbol = config_vps.SYMBOL_MAP.get(discord_symbol, discord_symbol)
    positions = mt5.positions_get(symbol=broker_symbol)
    if not positions: return 0
    
    closed_count = 0
    for pos in positions:
        # Only close trades opened by this bot (via Magic Number)
        if pos.magic == config_vps.MAGIC_NUMBER:
            # Determine closing type (opposite of current position)
            close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
            tick = mt5.symbol_info_tick(broker_symbol)
            close_price = tick.bid if pos.type == mt5.POSITION_TYPE_BUY else tick.ask
            
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": broker_symbol,
                "volume": pos.volume,
                "type": close_type,
                "position": pos.ticket,
                "price": close_price,
                "magic": config_vps.MAGIC_NUMBER,
                "comment": "Signal Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            mt5.order_send(close_request)
            closed_count += 1
    return closed_count