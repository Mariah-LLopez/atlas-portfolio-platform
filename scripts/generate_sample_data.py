from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2022-01-03", periods=900)
    tickers = ["SPY", "VXUS", "IEF", "LQD", "VNQ", "GLD", "BIL"]

    annual_mu = np.array([0.08, 0.07, 0.035, 0.045, 0.065, 0.04, 0.025])
    annual_sigma = np.array([0.18, 0.20, 0.08, 0.09, 0.20, 0.16, 0.01])

    daily_mu = annual_mu / 252
    daily_sigma = annual_sigma / np.sqrt(252)
    shocks = rng.normal(daily_mu, daily_sigma, size=(len(dates), len(tickers)))
    prices = 100 * np.exp(np.cumsum(shocks, axis=0))

    frame = pd.DataFrame(prices, index=dates, columns=tickers)
    output = Path("data/sample/sample_market_prices.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
