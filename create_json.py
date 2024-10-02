import requests
import pandas as pd

# API URLs and corresponding payloads
api_details = [
    {
        "url": "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/BE/BE0101/BE0101A/BefolkningNy",  # Population by civil status, gender
        "payload": {
            "query": [
                {"code": "Civilstand", "selection": {"filter": "item", "values": ["OG", "G", "SK"]}},
                {"code": "Alder", "selection": {"filter": "vs:ÅlderTotA", "values": []}},
                {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
                {"code": "ContentsCode", "selection": {"filter": "item", "values": ["BE0101N1"]}}
            ],
            "response": {"format": "json"}
        },
        "type": "civilstand"
    },
    {
        "url": "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/BE/BE0101/BE0101H/FoddaK",  # Births by gender
        "payload": {
            "query": [
                {"code": "Region", "selection": {"filter": "vs:RegionRiket99", "values": []}},
                {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}}
            ],
            "response": {"format": "json"}
        },
        "type": "levande_fodda"
    },
    {
        "url": "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/BE/BE0101/BE0101I/DodaHandelseK",  # Deaths by gender
        "payload": {
            "query": [
                {"code": "Region", "selection": {"filter": "vs:RegionRiket99", "values": []}},
                {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}}
            ],
            "response": {"format": "json"}
        },
        "type": "doda"
    },
    {
        "url": "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/BE/BE0101/BE0101A/BefolkningNy",  # Population by gender
        "payload": {
            "query": [
                {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
                {"code": "ContentsCode", "selection": {"filter": "item", "values": ["BE0101N1"]}}
            ],
            "response": {"format": "json"}
        },
        "type": "folkmangd"
    }
]

# Function to process the civil status data (married, unmarried, divorced)
def process_civilstand_data(data):
    df = pd.DataFrame(data)
    df[['civilstand', 'kon', 'ar']] = pd.DataFrame(df['key'].tolist(), index=df.index)
    df['population'] = df['values'].apply(lambda x: int(x[0]))
    df.drop(columns=['key', 'values'], inplace=True)
    
    # Pivot to get civil status as columns
    df_pivot = df.pivot_table(index=['kon', 'ar'], columns='civilstand', values='population').reset_index()
    return df_pivot

# Function to process the births or deaths data
def process_births_and_deaths_data(data, data_type):
    df = pd.DataFrame(data)
    df[['kon', 'ar']] = pd.DataFrame(df['key'].tolist(), index=df.index)
    
    if data_type == 'levande_fodda':
        df['levande_fodda'] = df['values'].apply(lambda x: int(x[0]))
    elif data_type == 'doda':
        df['doda'] = df['values'].apply(lambda x: int(x[0]))
    
    df.drop(columns=['key', 'values'], inplace=True)
    return df

# Function to process total population data
def process_folkmangd_data(data):
    df = pd.DataFrame(data)
    df[['kon', 'ar']] = pd.DataFrame(df['key'].tolist(), index=df.index)
    df['folkmangd'] = df['values'].apply(lambda x: int(x[0]))
    df.drop(columns=['key', 'values'], inplace=True)
    return df

# General function that calls the appropriate processing function based on the data type
def process_data(data, data_type):
    if data_type == 'civilstand':
        return process_civilstand_data(data)
    elif data_type == 'levande_fodda' or data_type == 'doda':
        return process_births_and_deaths_data(data, data_type)
    elif data_type == 'folkmangd':
        return process_folkmangd_data(data)
    else:
        raise ValueError(f"Unknown data type: {data_type}")

# Fetch data from APIs and store the processed data
data_frames = []
for api in api_details:
    response = requests.post(api['url'], json=api['payload'])
    if response.status_code == 200:
        processed_df = process_data(response.json()['data'], api['type'])
        data_frames.append(processed_df)
    else:
        print(f"Failed to fetch data from {api['url']}")

# Merge all DataFrames using a full outer join
df_combined = data_frames[0]
for df in data_frames[1:]:
    df_combined = pd.merge(df_combined, df, on=['kon', 'ar'], how='outer')

# Rename columns for civil status
df_combined.rename(columns={'OG': 'ogifta', 'G': 'gifta', 'SK': 'skilda'}, inplace=True)

# Ensure all columns are integers
df_combined = df_combined.apply(lambda x: x.fillna(0).astype(int))

# Save the final combined data to JSON
output_path = "final_population_data.json"
df_combined.to_json(output_path, orient='records', indent=4)

print(f"Combined data saved successfully to {output_path}")
