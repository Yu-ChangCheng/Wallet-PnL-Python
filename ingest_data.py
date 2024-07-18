import os
import requests
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')


# Create table if it does not exist
def create_table_if_not_exists():
    conn = get_db_connection()
    cursor = conn.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS token_prices (
        id SERIAL PRIMARY KEY,
        token_id VARCHAR(50) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        price NUMERIC(20, 15) NOT NULL,
        UNIQUE(token_id, timestamp)
    );
    CREATE INDEX IF NOT EXISTS idx_token_timestamp ON token_prices(token_id, timestamp);
    '''
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

# Connect to the PostgreSQL database
def get_db_connection():
    return psycopg2.connect(
        user=DB_USER,
        host=DB_HOST,
        database=DB_NAME,
        password=DB_PASSWORD,
        port=DB_PORT
    )

# Get top 10 tokens by market cap
def get_top_10_tokens():
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 10,
        'page': 1,
        'sparkline': False
    }
    headers = {
        'x-cg-demo-api-key': COINGECKO_API_KEY
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    return [token['id'] for token in data]

# Get hourly data for a token for the past 7 days
def get_hourly_data(token_id):
    url = f'https://api.coingecko.com/api/v3/coins/{token_id}/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': '7'
    }
    headers = {
        'x-cg-demo-api-key': COINGECKO_API_KEY
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data['prices']

# Store data in PostgreSQL
def store_data(token_id, prices):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('BEGIN')
        for timestamp, price in prices:
            timestamp = datetime.utcfromtimestamp(timestamp / 1000)  # Convert milliseconds to datetime
            cursor.execute(
                '''
                INSERT INTO token_prices (token_id, timestamp, price)
                VALUES (%s, %s, %s)
                ON CONFLICT (token_id, timestamp) DO UPDATE
                SET price = EXCLUDED.price
                ''',
                (token_id, timestamp, price)
            )
        cursor.execute('COMMIT')
    except Exception as e:
        cursor.execute('ROLLBACK')
        raise e
    finally:
        cursor.close()
        conn.close()

# Ingest data for the top 10 tokens
def ingest_data():
    try:
        top_10_tokens = get_top_10_tokens()
        for token_id in top_10_tokens:
            hourly_data = get_hourly_data(token_id)
            store_data(token_id, hourly_data)
            print(f'Data ingested for {token_id}')
    except Exception as error:
        print(f'Error ingesting data: {error}')

# Run the ingestion process
if __name__ == '__main__':
    create_table_if_not_exists()
    ingest_data()
    