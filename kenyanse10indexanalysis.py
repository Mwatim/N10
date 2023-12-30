import os
import pandas as pd
import itertools
import logging
import time
import traceback

logging.basicConfig(level=logging.INFO)

def time_calculator(timevalue_int):
    """
    This function to measure time units
    """
    return f"{int(timevalue_int/3600)}H {int((timevalue_int/60)%60) if timevalue_int/3600>0 else int(timevalue_int/60)}M {int(timevalue_int%60)}S"

def load_and_clean_data(file_path):
    """
    This function loads and cleans the data
    """
    logging.info("Loading and cleaning data...")
    start_time = time.time()

    try:
        df = pd.read_csv(file_path)
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df = df.T.drop_duplicates().T
        df["Date"] = df[" Date"].str.strip()
        df["Date"] = pd.to_datetime(df["Date"])
    except Exception as e:
        logging.error(f"Error loading and cleaning data: {str(e)}")
        traceback.print_exc()
        raise e

    elapsed_time = time.time() - start_time
    logging.info(f"Loading and cleaning data completed, time taken: {time_calculator(elapsed_time)}")

    return df

def extract_stock_data(df):
    """
    This function extracts the cleaned data
    """
    logging.info("Extracting stock data...")
    start_time = time.time()

    try:
        stocks = {}
        for col in df.columns[1:]:
            stock_name = col.split(" Adj. Close")[0]
            stock_data = list(zip(df["Date"], df[col]))
            stocks[stock_name] = stock_data
    except Exception as e:
        logging.error(f"Error extracting stock data: {str(e)}")
        traceback.print_exc()
        raise e

    elapsed_time = time.time() - start_time
    logging.info(f"Extracting stock data completed, time taken: {time_calculator(elapsed_time)}")

    return stocks

def calculate_portfolio_performance(portfolio):
    """
    This function calculates the performance of the portfolio
    """
    first_close = sum([data[0][1] for data in portfolio.values()]) / len(portfolio) if len(portfolio) != 0 else 0
    last_close = sum([data[-1][1] for data in portfolio.values()]) / len(portfolio) if len(portfolio) != 0 else 0
    performance = ((last_close - first_close) / first_close) * 100 if first_close != 0 else 0
    return performance

def generate_portfolios(stocks, max_size=10):
    """
    This function generates the actual portfolios from the cleaned stock data
    """
    logging.info("Generating portfolios...")
    start_time = time.time()

    try:
        portfolios = []
        for portfolio_size in range(2, max_size + 1):
            stock_combinations = itertools.combinations(stocks.keys(), portfolio_size)
            for stock_combo in stock_combinations:
                portfolio = {stock_name: stocks[stock_name] for stock_name in stock_combo}
                portfolio_name = ", ".join(stock_combo)
                performance = calculate_portfolio_performance(portfolio)
                portfolios.append((portfolio_name, performance))
    except Exception as e:
        logging.error(f"Error generating portfolios: {str(e)}")
        traceback.print_exc()
        raise e

    elapsed_time = time.time() - start_time
    logging.info(f"Generating portfolios completed, time taken: {time_calculator(elapsed_time)}")

    portfolios.sort(key=lambda x: abs(x[1]), reverse=True)
    return portfolios

def main():
    """
    The main function runs the entire script
    """
    logging.info("Script started.")
    file_path = os.path.join(os.getcwd(), "dataset.csv")
    
    try:
        df = load_and_clean_data(file_path)
        stocks = extract_stock_data(df)
        portfolios = generate_portfolios(stocks)
        
        logging.info("Top portfolios:")
        for portfolio in portfolios:
            logging.info(f"{portfolio[0]} - Performance: {portfolio[1]:.2f}%")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

    finally:
        logging.info("Script completed.")

if __name__ == "__main__":
    main()