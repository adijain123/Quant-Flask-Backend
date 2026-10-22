
import finnhub
import json

# Enter your Finnhub API key
API_KEY = "cpe4ie1r01qh24fmfqj0cpe4ie1r01qh24fmfqjg"

finnhub_client = finnhub.Client(api_key=API_KEY)


def company_Info(symbol):
    try:
        response = finnhub_client.company_profile2(symbol=symbol)

        if response:
            print("API is working!")
            print(f"\nCompany Information for {symbol}:")
            print(json.dumps(response, indent=4))
        else:
            print(f"No company information found for {symbol}.")
            print("API request completed, but the response is empty.")

    except Exception as e:
        print("API request failed!")
        print("Error:", str(e))


if __name__ == "__main__":
    company_Info("AAPL")
