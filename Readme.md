## Part I: Ingesting and Storing Token Prices
The code ingests hourly token prices data for the top 10 tokens by market cap from the Coingecko API from past 7 days and stores it in a PostgreSQL database.

### PostgreSQL database setup
### Assuming PostgreSQL is installed and running
#### Step 1: Create a new database us PGadmin
Name your database: token_prices_db

#### Step 2: Create a .env file with the following content
```
DB_USER=your_db_user
DB_HOST=localhost
DB_NAME=token_prices_db
DB_PASSWORD=your_db_password
DB_PORT=5432
COINGECKO_API_KEY=your_coingecko_api_key
```

#### Step 3: Install the required Python packages
```sh
pip install -r requirements.txt
```

#### Step 4: Run the Python script to create the table and ingest data
```sh
python ingest_data.py
```

#### Options: input for how many days from now and how many tokens that you want to ingest
```sh
python ingest_data.py --days 7 --n_tokens 10
```

---------------------------------------------------------------------------------------------------

## Part II: PnL Calculation
### Step 1: Run API Server
```sh
python index.py
```

### Step 2: Call API with Terminal
#### Method 1 curl request with default - return past 7 days PnL
```sh
curl -X POST "http://localhost:8000/calculate_pnl" -H "Content-Type: application/json" -d '{"address": "YourWalletAddress"}'
```

#### Method 2 curl request with desired start_time and end_time - return PnL from start_time to end_time
```sh
curl -X POST "http://localhost:8000/calculate_pnl" -H "Content-Type: application/json" -d '{"address": "YourWalletAddress", "start_time": "2024-07-15 00:00:00", "end_time": "2024-07-19 23:59:59"}'
```

#### Method 3 curl request with desired start_time and end_time and details - return prices, balance, total_value and PnL from start_time to end_time
```sh
curl -X POST "http://localhost:8000/calculate_pnl" -H "Content-Type: application/json" -d '{"address": "0x26a016De7Db2A9e449Fe5b6D13190558d6bBCd5F", "start_time": "2024-07-15 23:59:59", "end_time": "2024-07-17 00:00:00", "detail": "True"}'
```

#### Example for Method 2
#### Input
```sh
curl -X POST "http://localhost:8000/calculate_pnl" -H "Content-Type: application/json" -d '{"address": "0x26a016De7Db2A9e449Fe5b6D13190558d6bBCd5F", "start_time": "2024-07-15 23:59:59", "end_time": "2024-07-17 00:00:00"}'
```

#### Output
```sh
[{"timestamp":"2024-07-16T00:00:00","PnL":0.0},
{"timestamp":"2024-07-16T01:00:00","PnL":-6.699949044984123},
{"timestamp":"2024-07-16T02:00:00","PnL":-4.667898056088916},
{"timestamp":"2024-07-16T03:00:00","PnL":-7.236441433503842},
{"timestamp":"2024-07-16T04:00:00","PnL":-7.452453496643784},
{"timestamp":"2024-07-16T05:00:00","PnL":-10.571969163360336},
{"timestamp":"2024-07-16T06:00:00","PnL":-23.985320725329757},
{"timestamp":"2024-07-16T07:00:00","PnL":-38.478681058663824},
{"timestamp":"2024-07-16T08:00:00","PnL":-41.23262906353966},
{"timestamp":"2024-07-16T09:00:00","PnL":-42.89291865086693},
{"timestamp":"2024-07-16T10:00:00","PnL":-33.46577429935178},
{"timestamp":"2024-07-16T11:00:00","PnL":-27.67939991589651},
{"timestamp":"2024-07-16T12:00:00","PnL":-25.383488347860748},
{"timestamp":"2024-07-16T13:00:00","PnL":-29.972499769858132},
{"timestamp":"2024-07-16T14:00:00","PnL":-29.27711362302648},
{"timestamp":"2024-07-16T15:00:00","PnL":-26.331488779748042},
{"timestamp":"2024-07-16T16:00:00","PnL":2.9065930484894125},
{"timestamp":"2024-07-16T17:00:00","PnL":-9.450134848548032},
{"timestamp":"2024-07-16T18:00:00","PnL":-11.264376187393282},
{"timestamp":"2024-07-16T19:00:00","PnL":-9.7614754792437},
{"timestamp":"2024-07-16T20:00:00","PnL":-3.1946099146450706},
{"timestamp":"2024-07-16T21:00:00","PnL":-16.103172875084965},
{"timestamp":"2024-07-16T22:00:00","PnL":-18.785365527644444},
{"timestamp":"2024-07-16T23:00:00","PnL":-21.875129585973127}]
```

#### Example for Method 3
#### Input
```sh
curl -X POST "http://localhost:8000/calculate_pnl" -H "Content-Type: application/json" -d '{"address": "0x26a016De7Db2A9e449Fe5b6D13190558d6bBCd5F", "start_time": "2024-07-15 23:59:59", "end_time": "2024-07-17 00:00:00", "detail": "True"}';
```

#### Output
```sh
[{"timestamp":"2024-07-16T00:00:00","ethereum_price":3489.548516604077,"ethereum":0.09312087735100151,"Value":1299.79927770023,"PnL":0.0},
{"timestamp":"2024-07-16T01:00:00","ethereum_price":3471.561279918876,"ethereum":0.09312087735100151,"Value":1293.099328655246,"PnL":-6.699949044984123},
{"timestamp":"2024-07-16T02:00:00","ethereum_price":3477.0166918702575,"ethereum":0.09312087735100151,"Value":1295.1313796441411,"PnL":-4.667898056088916},
{"timestamp":"2024-07-16T03:00:00","ethereum_price":3470.1209681333203,"ethereum":0.09312087735100151,"Value":1292.5628362667262,"PnL":-7.236441433503842},
{"timestamp":"2024-07-16T04:00:00","ethereum_price":3469.5410443039796,"ethereum":0.09312087735100151,"Value":1292.3468242035863,"PnL":-7.452453496643784},
{"timestamp":"2024-07-16T05:00:00","ethereum_price":3461.166134843671,"ethereum":0.09312087735100151,"Value":1289.2273085368697,"PnL":-10.571969163360336},
{"timestamp":"2024-07-16T06:00:00","ethereum_price":3425.1555431709508,"ethereum":0.09312087735100151,"Value":1275.8139569749003,"PnL":-23.985320725329757},
{"timestamp":"2024-07-16T07:00:00","ethereum_price":3386.2454707317056,"ethereum":0.09312087735100151,"Value":1261.3205966415662,"PnL":-38.478681058663824},
{"timestamp":"2024-07-16T08:00:00","ethereum_price":3378.8519944157147,"ethereum":0.09312087735100151,"Value":1258.5666486366904,"PnL":-41.23262906353966},
{"timestamp":"2024-07-16T09:00:00","ethereum_price":3374.394643833983,"ethereum":0.09312087735100151,"Value":1256.9063590493631,"PnL":-42.89291865086693},
{"timestamp":"2024-07-16T10:00:00","ethereum_price":3399.7035343311736,"ethereum":0.09312087735100151,"Value":1266.3335034008783,"PnL":-33.46577429935178},
{"timestamp":"2024-07-16T11:00:00","ethereum_price":3415.2381130101435,"ethereum":0.09312087735100151,"Value":1272.1198777843335,"PnL":-27.67939991589651},
{"timestamp":"2024-07-16T12:00:00","ethereum_price":3421.4019068696603,"ethereum":0.09312087735100151,"Value":1274.4157893523693,"PnL":-25.383488347860748},
{"timestamp":"2024-07-16T13:00:00","ethereum_price":3409.081867710504,"ethereum":0.09312087735100151,"Value":1269.826777930372,"PnL":-29.972499769858132},
{"timestamp":"2024-07-16T14:00:00","ethereum_price":3410.948758805748,"ethereum":0.09312087735100151,"Value":1270.5221640772036,"PnL":-29.27711362302648},
{"timestamp":"2024-07-16T15:00:00","ethereum_price":3418.8568265964313,"ethereum":0.09312087735100151,"Value":1273.467788920482,"PnL":-26.331488779748042},
{"timestamp":"2024-07-16T16:00:00","ethereum_price":3497.351796414075,"ethereum":0.09312087735100151,"Value":1302.7058707487195,"PnL":2.9065930484894125},
{"timestamp":"2024-07-16T17:00:00","ethereum_price":3464.17790391932,"ethereum":0.09312087735100151,"Value":1290.349142851682,"PnL":-9.450134848548032},
{"timestamp":"2024-07-16T18:00:00","ethereum_price":3459.3072417475955,"ethereum":0.09312087735100151,"Value":1288.5349015128368,"PnL":-11.264376187393282},
{"timestamp":"2024-07-16T19:00:00","ethereum_price":3463.3420531424795,"ethereum":0.09312087735100151,"Value":1290.0378022209864,"PnL":-9.7614754792437},
{"timestamp":"2024-07-16T20:00:00","ethereum_price":3480.972002922286,"ethereum":0.09312087735100151,"Value":1296.604667785585,"PnL":-3.1946099146450706},
{"timestamp":"2024-07-16T21:00:00","ethereum_price":3446.3166084295353,"ethereum":0.09312087735100151,"Value":1283.696104825145,"PnL":-16.103172875084965},
{"timestamp":"2024-07-16T22:00:00","ethereum_price":3439.115772460042,"ethereum":0.09312087735100151,"Value":1281.0139121725856,"PnL":-18.785365527644444},
{"timestamp":"2024-07-16T23:00:00","ethereum_price":3430.8207366253755,"ethereum":0.09312087735100151,"Value":1277.924148114257,"PnL":-21.875129585973127}]
```
---------------------------------------------------------------------------------------------------
## Part III: Scaling

Suppose that this prototype is a success, and we wish to scale this API to:

1. Include 10,000 tokens.
2. Calculate PnL with 5-minute granularity (instead of hourly).
3. Show PnLs up to the start of the coins (e.g., 2009 for Bitcoin, 2015 for Ethereum), instead of just the past week.

### Suggestions for Scaling

1. **Database Scaling**:
    - Consider using a master-slave (write/read) database setup to avoid locking issues.
    - Use a time-series database to store price data efficiently.
    - Partition the database by token_id and time range (e.g., by month or year) to improve query performance.
    - Index the timestamp and token_id columns.
    - Use batch inserts for large data ingestion.

2. **Data Ingestion**:
    - Fetch data for multiple tokens in parallel using asynchronous programming or multi-threading to speed up the ingestion process.

3. **5-Minute Granularity**:
    - Ensure 5-minute granularity price data for each token.
    - Implement a function to round down to the nearest 5-minute interval:
      ```python
      def round_down_to_five_minutes(dt):
          return dt - timedelta(minutes=dt.minute % 5, seconds=dt.second, microseconds=dt.microsecond)
      ```
    - Vectorize calculations using NumPy arrays for better performance, though this will require more memory.

4. **Extended PnL Calculation Period**:
    - Source historical price data from providers that offer longer time spans.
    - Use forward-fill (ffill) to handle missing data points in long-term historical data.


