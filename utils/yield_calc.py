# yield_calc.py
def calculate_gross_yield(price, monthly_rent):
    """
    Calculate gross rental yield as a percentage.
    :param price: Purchase price of the property (numeric).
    :param monthly_rent: Expected monthly rent (numeric).
    :return: Gross rental yield in percent (float).
    """
    if price and monthly_rent:
        annual_rent = monthly_rent * 12
        yield_pct = (annual_rent / price) * 100
        return round(yield_pct, 2)
    return None

# Example:
# price = 400000; monthly_rent = 2000  -> yield = 6.00%