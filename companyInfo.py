import finnhub
finnhub_client = finnhub.Client(api_key="cpe4ie1r01qh24fmfqj0cpe4ie1r01qh24fmfqjg")

def company_Info(symbol):
    return finnhub_client.company_profile2(symbol=symbol)
