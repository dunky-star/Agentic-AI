from typing import Any

from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Binance MCP")

def get_symbol_from_name(name: str) -> str:
    """
    Convert a human-readable symbol name to Binance's format.
    """
    if name.upper() in ["bitcoin", "btc"]:
        return "BTCUSDT"
    elif name.lower() in ["ethereum", "eth"]:
        return "ETHUSDT"
    else:
        return name.upper()

@mcp.tool()
def get_price(symbol: str) -> Any:
    """
    Get the current price of a cryptocurrency asset from Binance.
    Args:
        symbol (str): The name of the cryptocurrency asset (e.g., "bitcoin", "ethereum") to get price of.
    Returns:
        Any: The current price of the crypto asset.
    """
    symbol = get_symbol_from_name(symbol)
    url = f"https://api.binance.us/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

if __name__ == "__main__":
    print("Starting MCP for Binance...")
    mcp.run()
