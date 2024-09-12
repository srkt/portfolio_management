import pandas as pd
import src.db.stock_repository as sr


def calculate_sma(df, window):
    if "Close" not in df.columns:
        raise ValueError("DataFrame must contain 'Close' column")

    # Ensure the index is a datetime index
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        raise ValueError("Index must be a datetime index")

    # Calculate the Simple Moving Average (SMA)
    df[str(window) + "SMA"] = df["Close"].rolling(window=window, min_periods=1).mean()

    return df


def calculate_multi_sma(df, windows=[5, 10, 21, 50, 100, 200]):
    if "Close" not in df.columns:
        raise ValueError("DataFrame must contain 'Close' column")

    # Ensure the index is a datetime index
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        raise ValueError("Index must be a datetime index")

    # Calculate the Simple Moving Average (SMA)
    for window in windows:
        df["SMA_" + str(window)] = (
            df["Close"].rolling(window=window, min_periods=1).mean()
        )

    return df


def VWAP(df):
    df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum()
    return df


def Anchored_VWAP(df, anchor_date):
    # Ensure anchor_date is a datetime
    anchor_date = pd.to_datetime(anchor_date)

    # Filter DataFrame to include only data from the anchor_date onwards
    df_filtered = df[df.index >= anchor_date]

    # Calculate VWAP
    vwap = (df_filtered["Close"] * df_filtered["Volume"]).cumsum() / df_filtered[
        "Volume"
    ].cumsum()

    # Add VWAP to the DataFrame
    df_filtered["AVWAP"] = vwap

    return df_filtered


def get_technical_analysis(ticker):
    df = sr.get_stock_dataframe(ticker)
    df = calculate_multi_sma(df)
    df = VWAP(df)
    return df


def update_technical_analysis(ticker):
    df = get_technical_analysis(ticker)
    sr.update_technical_analysis(ticker, df)
    print("Updated technical analysis for " + ticker)


def saveAvwapData(ticker, anchor_date, notes=None):
    id = sr.saveAvwapDataPoint(ticker, anchor_date, notes)
    df = sr.get_stock_dataframe(ticker)
    vwap_data = Anchored_VWAP(df, anchor_date)
    vwap_data.insert(0, "POINT_ID", id)
    result = vwap_data[["POINT_ID", "Close", "AVWAP"]]
    print(result.tail())
    sr.saveAvawpData(result)
