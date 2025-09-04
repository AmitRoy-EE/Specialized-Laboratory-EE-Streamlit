import pandas as pd

##########__________________________________________________________##########
##########__________Creation of the 1st default input file__________##########
##########__________________________________________________________##########

# Define the time period for filtering the data
start_of_time_period = "2015-01-01 00:00:00"
end_of_time_period = "2015-01-08 00:00:00"

# Define the path to the source CSV file
path_to_source_1 = "input_data/flows_and_storage_RAW.csv"

# Read the CSV file into a DataFrame
try:
    df1 = pd.read_csv(path_to_source_1, index_col=0)
except FileNotFoundError:
    print(f"Error: The file {path_to_source_1} was not found.")
    raise
except pd.errors.ParserError:
    print(f"Error: There was a parsing error while reading {path_to_source_1}.")
    raise

# Filter the DataFrame for the specified time period
df1 = df1.loc[start_of_time_period:end_of_time_period]

# Ensure the index is in datetime format
df1.index = pd.to_datetime(df1.index)
print("Index after conversion to datetime:", df1.index)

# Rename the index
df1 = df1.rename_axis("time")

# Rename the columns
rename_mapping = {"electricity_demand_kW": "electricity_demand", "rooftop pv->electricity_bus": "pv_generation"}

df1 = df1.rename(columns=rename_mapping)

# Define the path to export the filtered data
path_to_source_1_export = path_to_source_1.replace("_RAW.csv", "_1H.csv")

# Check if the renamed columns exist and then export them
columns_to_export = ["electricity_demand", "pv_generation"]
missing_columns = [col for col in columns_to_export if col not in df1.columns]

if missing_columns:
    print(f"Warning: The following columns are missing in the source data and will not be exported: {missing_columns}")

# Export the desired columns to a new CSV file, handling only available columns
available_columns_to_export = [col for col in columns_to_export if col in df1.columns]
df1[available_columns_to_export].to_csv(path_to_source_1_export, float_format="%.2f", index=True)


##########__________________________________________________________##########
##########__________Creation of the 2nd default input file__________##########
##########__________________________________________________________##########

# Define the time period for filtering the data
start_of_time_period = "2015-01-01T00:00:00"
end_of_time_period = "2015-01-08T00:00:00"

# Define the path to the source CSV file
path_to_source_2 = "input_data/strompreis_und_co2-emissionen_RAW.csv"

# Read the CSV file into a DataFrame
try:
    df2 = pd.read_csv(path_to_source_2, index_col="date_id", parse_dates=["date_id"])
except FileNotFoundError:
    print(f"Error: The file {path_to_source_2} was not found.")
    raise
except pd.errors.ParserError:
    print(f"Error: There was a parsing error while reading {path_to_source_2}.")
    raise

# Filter the DataFrame for the specified time period
df2 = df2.loc[start_of_time_period:end_of_time_period]

# Ensure the index is in datetime format
df2.index = pd.to_datetime(df2.index)
print("Index after conversion to datetime:", df2.index)

# Rename the index
df2 = df2.rename_axis("time")

# Rename the columns
rename_mapping = {"CO₂-Emissionsfaktor des Strommix": "CO2_emissions", "Strompreis": "electricity_price"}

df2 = df2.rename(columns=rename_mapping)

# Define the path to export the filtered data
path_to_source_2_export = path_to_source_2.replace("_RAW.csv", "_1H.csv")

# Check if the renamed columns exist and then export them
columns_to_export = ["electricity_price", "CO2_emissions"]
missing_columns = [col for col in columns_to_export if col not in df2.columns]

if missing_columns:
    print(f"Warning: The following columns are missing in the source data and will not be exported: {missing_columns}")

# Export the desired columns to a new CSV file, handling only available columns
available_columns_to_export = [col for col in columns_to_export if col in df2.columns]
df2[available_columns_to_export].to_csv(path_to_source_2_export, float_format="%.2f", index=True)

print("Created all input files for import in App")
