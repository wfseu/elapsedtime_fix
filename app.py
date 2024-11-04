import pandas as pd
import requests
import json  # Import json to parse the timings

# Load the CSV file
file_name = 'output_A_9592488.csv'
df = pd.read_csv(file_name)
print("Initial DataFrame:\n", df)

# Step 2: Find the row where Tenth % is 100
tenth_row = df[df['Tenth %'] == 100]
if tenth_row.empty:
    print("No row found with Tenth % = 100")
else:
    tenth_row = tenth_row.iloc[0]
    elapsed_time = tenth_row['Elapsed Time (s)']
    print(f"Elapsed Time for Tenth % = 100: {elapsed_time}")

    # Step 3: Extract Race Track and Term
    race_track = tenth_row['RaceTrack']
    term = tenth_row['Term']
    print(f"Race Track: {race_track}, Term: {term}")

    # Step 4: Make API call
    api_url = f'https://api.kaj789.com/api/marble/{race_track}/{term}'
    print(f"API URL: {api_url}")
    response = requests.get(api_url)

    # Check if the API call was successful
    if response.status_code == 200:
        api_data = response.json()
        print("API Response:\n", api_data)

        # Parse the timings to find the time for pm 10
        timings_str = api_data.get('timings')
        print("Raw timings string:", timings_str)

        if timings_str:
            try:
                timings = json.loads(timings_str)  # Parse the string to a list of dicts
                pm_10_time = next((item['time'] for item in timings if item['pm'] == 10), None)
                print(f"pm_10_time extracted: {pm_10_time}")
            except json.JSONDecodeError:
                print("Error decoding the timings JSON.")
                pm_10_time = None
        else:
            print("Timings data not found in the API response.")
            pm_10_time = None

        # Check if pm_10_time is valid
        if pm_10_time is None:
            print("pm_10_time is not present in the API response.")
        else:
            # Step 5: Calculate the deducted time
            deducted_time = elapsed_time - pm_10_time
            print(f"Deducted Time: {deducted_time}")

            # Calculate the percentage of deducted_time from elapsed_time
            percentage = (deducted_time / elapsed_time) * 100
            print(f"Deducted Time as Percentage of Original: {percentage}%")

            # Step 6: Update elapsed times in the DataFrame
            num_rows = len(df)
            for index in range(num_rows):
                if index == 0:
                    df.loc[index, 'Elapsed Time (s)'] = 0
                else:
                    adjustment = ((percentage / num_rows) * (index + 1)) 
                    df.loc[index, 'Elapsed Time (s)'] = df.loc[index, 'Elapsed Time (s)'] - (df.loc[index, 'Elapsed Time (s)'] * (adjustment/100) )

            print("Updated DataFrame:\n", df)

            # Save the updated DataFrame back to the CSV
            df.to_csv(file_name, index=False)
            print(f"Data saved to {file_name}")
    else:
        print(f"API call failed with status code: {response.status_code}")
