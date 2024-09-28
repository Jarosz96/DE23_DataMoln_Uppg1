import requests
import json
import pandas as pd

# The API URLs
urls = [
    "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/BE/BE0101/BE0101A/BefolkningNy",  # Folkmängd efter civilstånd, ålder, kön och år
    "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/BE/BE0101/BE0101H/FoddaK",        # Levande födda efter kön och år
    "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/BE/BE0101/BE0101I/DodaHandelseK", # Döda efter kön och år
    "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/BE/BE0101/BE0101A/BefolkningNy"   # Folkmängd efter kön
]

# The query payloads
payloads = [
    {
        "query": [
            {
                "code": "Civilstand",
                "selection": {
                    "filter": "item",
                    "values": ["OG", "G", "SK"]
                }
            },
            {
                "code": "Alder",
                "selection": {
                    "filter": "vs:ÅlderTotA",
                    "values": []
                }
            },
            {
                "code": "Kon",
                "selection": {
                    "filter": "item",
                    "values": ["1", "2"]
                }
            },
            {
                "code": "ContentsCode",
                "selection": {
                    "filter": "item",
                    "values": ["BE0101N1"]
                }
            }
        ],
        "response": {
            "format": "json"
        }
    },
    {
        "query": [
            {
                "code": "Region",
                "selection": {
                    "filter": "vs:RegionRiket99",
                    "values": []
                }
            },
            {
                "code": "Kon",
                "selection": {
                    "filter": "item",
                    "values": ["1", "2"]
                }
            }
        ],
        "response": {
            "format": "json"
        }
    },
    {
        "query": [
            {
                "code": "Region",
                "selection": {
                    "filter": "vs:RegionRiket99",
                    "values": []
                }
            },
            {
                "code": "Kon",
                "selection": {
                    "filter": "item",
                    "values": ["1", "2"]
                }
            }
        ],
        "response": {
            "format": "json"
        }
    },
    {
        "query": [
            {
                "code": "Kon",
                "selection": {
                    "filter": "item",
                    "values": ["1", "2"]
                }
            },
            {
                "code": "ContentsCode",
                "selection": {
                    "filter": "item",
                    "values": ["BE0101N1"]
                }
            }
        ],
        "response": {
            "format": "json"
        }
    }
]

# Fetch data from each URL and store in a list of DataFrames
data_frames = []

for i in range(len(urls)):
    response = requests.post(urls[i], json=payloads[i])
    if response.status_code == 200:
        data = response.json()['data']
        # Process the fetched data and store in the corresponding DataFrame
        if i == 0:  # Civilstand
            df = pd.DataFrame(data)
            df[['civilstand', 'kon', 'ar']] = pd.DataFrame(df['key'].tolist(), index=df.index)
            df['population'] = df['values'].apply(lambda x: int(x[0]))
            df.drop(columns=['key', 'values'], inplace=True)
            df_pivot = df.pivot_table(index=['kon', 'ar'], columns='civilstand', values='population').reset_index()
            data_frames.append(df_pivot)
        else:  # Folkmängd, Levande födda, Döda
            df = pd.DataFrame(data)
            df[['kon', 'ar']] = pd.DataFrame(df['key'].tolist(), index=df.index)
            if i == 1:
                df['levande_fodda'] = df['values'].apply(lambda x: int(x[0]))
            elif i == 2:
                df['doda'] = df['values'].apply(lambda x: int(x[0]))
            else:
                df['folkmangd'] = df['values'].apply(lambda x: int(x[0]))
            df.drop(columns=['key', 'values'], inplace=True)
            data_frames.append(df)

# Merge all the DataFrames using full outer join
df_combined = data_frames[0]
for df in data_frames[1:]:
    df_combined = pd.merge(df_combined, df, on=['kon', 'ar'], how='outer')

# Rename columns for civilstand
df_combined.rename(columns={'OG': 'ogifta', 'G': 'gifta', 'SK': 'skilda'}, inplace=True)

# Save the combined DataFrame to a new JSON file
output_path = "final_population_data.json"
df_combined.to_json(output_path, orient='records', indent=4)

print(f"Combined data saved successfully to {output_path}")
