import pandas as pd

##########__________________________________________________________##########
##########__________Creation of the 1st default input file__________##########
##########__________________________________________________________##########

# Define the time period for filtering the data
start_of_time_period = "2015-01-01 00:00:00"
end_of_time_period = "2015-01-07 23:00:00"

# Define the path to the source CSV file
path_to_source = "input_data/hourly_electricity_price.csv"

# Read the CSV file into a DataFrame
try:
    df = pd.read_csv(path_to_source)
except FileNotFoundError:
    print(f"Error: The file {path_to_source} was not found.")
    raise
except pd.errors.ParserError:
    print(f"Error: There was a parsing error while reading {path_to_source}.")
    raise

# Ensure the index is in datetime format
df.index = pd.to_datetime(df.index)

# Divide the second column by 1000
df.iloc[:, 1] = df.iloc[:, 1] / 1000.0

# Save the modified DataFrame to a new CSV file
df.to_csv(path_to_source, index=False)

print(f"Modified data saved to {path_to_source}")