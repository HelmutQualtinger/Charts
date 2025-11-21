import yfinance as yf
import pandas as pd
import numpy as np

def generate_smic_csv():
    print("--- Generating SMI Total Return (Synthetic) CSV ---")
    
    # 1. Fetch SMI Price Index Data (^SSMI)
    # Note: ^SSMI is the standard ticker on Yahoo and has data back to 1990s.
    ticker = "^SSMI"
    print(f"Fetching data for {ticker} (Price Index) from Yahoo Finance...")
    
    try:
        # Download daily data
        df = yf.download(ticker, start="2000-01-01", progress=True)
        
        if df.empty:
            print("Error: No data downloaded. Check your internet connection.")
            return

        # 2. Resample to Month-End
        # We use 'ME' (Month End) or 'M' depending on pandas version.
        df_monthly = df['Close'].resample('ME').last()
        
        # 3. Create a DataFrame
        smic_df = pd.DataFrame(df_monthly)
        smic_df.columns = ['SMI_Price_Index']
        
        # 4. Calculate Synthetic Total Return
        # The SMI Price index excludes dividends. To get SMIC (Total Return),
        # we must reinvest estimated dividends.
        # Historical average dividend yield for SMI is approx 2.8% - 3.0%
        ANNUAL_DIVIDEND_YIELD = 0.03  # 3.0% conservative average
        MONTHLY_YIELD_FACTOR = (1 + ANNUAL_DIVIDEND_YIELD) ** (1/12)
        
        # Create a list of accumulated values starting from the first price
        synthetic_tr = [smic_df['SMI_Price_Index'].iloc[0]]
        
        # Iterate and apply price change + dividend yield
        for i in range(1, len(smic_df)):
            prev_price = smic_df['SMI_Price_Index'].iloc[i-1]
            curr_price = smic_df['SMI_Price_Index'].iloc[i]
            
            # Price return for the month
            price_return = curr_price / prev_price
            
            # Total return = Price Return * Dividend Factor
            # (reinvesting the dividend into the index)
            tr_return = price_return * MONTHLY_YIELD_FACTOR
            
            # Calculate new TR value
            new_val = synthetic_tr[-1] * tr_return
            synthetic_tr.append(new_val)
            
        smic_df['SMI_Total_Return_Synthetic'] = synthetic_tr
        
        # 5. Format and Save to CSV
        output_filename = "smi_total_return_2000_2024.csv"
        
        # Format to 2 decimal places for cleaner CSV
        smic_df = smic_df.round(2)
        
        smic_df.to_csv(output_filename)
        
        print("\n✅ Success!")
        print(f"File saved as: {output_filename}")
        print(f"Records: {len(smic_df)} months")
        print(f"Timeframe: {smic_df.index[0].date()} to {smic_df.index[-1].date()}")
        
        # Preview
        print("\n--- Preview (Head) ---")
        print(smic_df.head())
        print("\n--- Preview (Tail) ---")
        print(smic_df.tail())

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_smic_csv()