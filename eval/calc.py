def calculate_cost(
    requests_per_day: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    input_price_per_m: float,
    output_price_per_m: float,
    cache_ratio: float = 0.0,
    cache_discount: float = 0.9
) -> dict:
    days_in_month = 30

    requests_month = requests_per_day * days_in_month

    total_input = requests_month * avg_input_tokens
    total_output = requests_month * avg_output_tokens

    cached_input = total_input * cache_ratio
    uncached_input = total_input * (1 - cache_ratio)

    input_cost = (
        uncached_input * input_price_per_m / 1_000_000 +
        cached_input * input_price_per_m * (1 - cache_discount) / 1_000_000
    )

    output_cost = total_output * output_price_per_m / 1_000_000

    total = input_cost + output_cost

    return {
        "requests_month": requests_month,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "input_cost": round(input_cost, 2),
        "output_cost": round(output_cost, 2),
        "total_monthly": round(total, 2),
        "cost_per_request": round(total / requests_month, 6)
    }