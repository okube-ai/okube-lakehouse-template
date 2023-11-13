import os
import yfinance as yf
from datetime import datetime
from datetime import date
from datetime import timedelta

from laktory.models import DataEvent
from laktory.models import Producer


# --------------------------------------------------------------------------- #
# Setup                                                                       #
# --------------------------------------------------------------------------- #

symbols = [
    "AAPL",
    "AMZN",
    "GOOGL",
    "MSFT",
]

for s in symbols:
    print(s)
    ticker = yf.Ticker(s)

    data = ticker.history_metadata
    del data["tradingPeriods"]

    event = DataEvent(
        name="stock_metadata",
        producer=Producer(name="yahoo-finance"),
        data=data,
        tstamp_in_path=False
    )
    event.to_databricks(overwrite=True, suffix=s)

