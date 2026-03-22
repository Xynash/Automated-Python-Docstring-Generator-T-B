def process_invoice(price, discount_pct, tax_rate=0.05):
    discount_amount = price * (discount_pct / 100)
    subtotal = price - discount_amount
    total = subtotal * (1 + tax_rate)
    return round(total, 2)