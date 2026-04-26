def convert_to_usd(amount: float, from_currency: str) -> float:
    """
    Converts local currency to USD using a static exchange rate map.
    In a production app, this would call a real-time FX API.
    """
    rates = {
        "JPY": 150.0,  # 150 Yen = 1 USD
        "EUR": 0.92,   # 0.92 Euro = 1 USD
        "GBP": 0.79,   # 0.79 Pound = 1 USD
        "THB": 36.0,   # 36 Baht = 1 USD
        "INR": 83.0,   # 83 Rupee = 1 USD
        "USD": 1.0
    }
    
    rate = rates.get(from_currency.upper(), 1.0)
    return amount / rate
