import os
import requests
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging
import numpy as np

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
API_KEY = os.getenv('API_KEY')

# Connect to the PostgreSQL database
def get_db_connection():
    return psycopg2.connect(
        user=DB_USER,
        host=DB_HOST,
        database=DB_NAME,
        password=DB_PASSWORD,
        port=DB_PORT
    )

# Fetch token balances for a wallet
def get_wallet_balances(address):
    url = 'https://api.allium.so/api/v1/explorer/queries/UWHFUe3BPTFpd7EDVIiI/run'
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY
    }
    response = requests.post(url, json={'address': address}, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data['data']

# Fetch historical prices from the database
def get_historical_prices(token_id, start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT timestamp, price
        FROM token_prices
        WHERE token_id = %s AND timestamp BETWEEN %s AND %s
        ORDER BY timestamp
    '''
    cursor.execute(query, (token_id, start_date, end_date))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# Round down to the nearest hour
def round_down_to_hour(dt):
    return dt.replace(minute=0, second=0, microsecond=0)

# Convert historical prices to DataFrame and round down timestamps
def historical_prices_to_df(token_id, start_date, end_date):
    prices = get_historical_prices(token_id, start_date, end_date)
    df = pd.DataFrame(prices, columns=['timestamp', f'{token_id}_price'])
    df['timestamp'] = df['timestamp'].apply(round_down_to_hour)
    return df

# Merge historical prices into a single DataFrame
def merge_historical_prices(token_ids, start_date, end_date):
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

    df_list = [historical_prices_to_df(token_id, start_date_dt, end_date_dt) for token_id in token_ids]
    
    # Initialize merged_df with the first DataFrame
    merged_df = df_list[0]
    for df in df_list[1:]:
        merged_df = pd.merge(merged_df, df, on='timestamp', how='outer')

    merged_df = merged_df.sort_values(by='timestamp')
    return merged_df

def create_holdings_df(balances, timestamps):
    balances_sorted = sorted(balances, key=lambda x: datetime.strptime(x['block_timestamp'], '%Y-%m-%dT%H:%M:%S'))
    
    # Initialize current_holdings with the balances before the first timestamp
    current_holdings = {balance['token_id']: 0 for balance in balances}
    first_timestamp = timestamps[0]
    for balance in balances_sorted:
        balance_timestamp = datetime.strptime(balance['block_timestamp'], '%Y-%m-%dT%H:%M:%S')
        if balance_timestamp <= first_timestamp:
            current_holdings[balance['token_id']] = balance['balance']
        else:
            break

    # Create holdings DataFrame
    holdings = []
    balance_index = 0
    num_balances = len(balances_sorted)

    for timestamp in timestamps:
        # Update current_holdings based on the timestamp
        while balance_index < num_balances:
            balance = balances_sorted[balance_index]
            balance_timestamp = datetime.strptime(balance['block_timestamp'], '%Y-%m-%dT%H:%M:%S')
            if balance_timestamp <= timestamp:
                current_holdings[balance['token_id']] = balance['balance']
                balance_index += 1
            else:
                break

        holding_entry = {'timestamp': timestamp}
        holding_entry.update(current_holdings)
        holdings.append(holding_entry)

    df_holdings = pd.DataFrame(holdings)
    return df_holdings

# Calculate value and PnL
def calculate_value_and_pnl_df(df, balances):
    df['Value'] = 0.0
    for balance in balances:
        token_id = balance['token_id']
        df['Value'] += df[f'{token_id}_price'].astype(float) * df[token_id].astype(float)

    initial_value = df['Value'].iloc[0]
    df['PnL'] = df['Value'] - initial_value
    return df

# Main
def main_calculate_pnls(wallet_address, start_time = None, end_time = None, detail = False):
    try:
        
        if not start_time:
            start_time = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        
        if not end_time:
            end_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')

        # Check if start date is after end date
        if start_time > end_time:
            raise ValueError("Start date cannot be after end date")
              
        # Fetch wallet balances
        balances = get_wallet_balances(wallet_address)
        print(balances)
        # Extract token IDs from balances
        token_ids = list(set(balance['token_id'] for balance in balances))

        # Fetch historical prices and merge into a single DataFrame
        price_df = merge_historical_prices(token_ids, start_time, end_time)

        # Fill NaN values in the price columns
        price_df = price_df.fillna(method='ffill')
        price_df = price_df.fillna(method='bfill')

        # Create holdings DataFrame
        holdings_df = create_holdings_df(balances, price_df['timestamp'])
        print(holdings_df)

        # Merge holdings with prices
        price_holding_df = pd.merge(price_df, holdings_df, on='timestamp', how='left')
        print(price_holding_df)

        # Calculate value and PnL
        final_df = calculate_value_and_pnl_df(price_holding_df, balances)

        # Output
        if detail:
            output_df = final_df
        else:
            output_df = final_df[['timestamp', 'PnL']] # Extract only timestamp and PnL columns for the output

        # print(output_df)

        return output_df
    except Exception as e:
        logging.error(f"Error calculating PnL: {e}")
        raise

app = FastAPI()

class WalletRequest(BaseModel):
    address: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    detail: Optional[bool] = False

@app.post("/calculate_pnl")
def calculate_pnl(request: WalletRequest):
    try:
        pnl_df = main_calculate_pnls(request.address, request.start_time, request.end_time, request.detail)
        pnl_list = pnl_df.to_dict(orient='records')
        return pnl_list
        
    except ValueError as ve:
        logging.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Error in API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
