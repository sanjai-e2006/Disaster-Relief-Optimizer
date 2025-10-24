import pandas as pd

# Load the dataset
df = pd.read_csv('data/disaster_data.csv')

print("Countries in dataset:")
countries = df['state'].unique()
for country in countries:
    print(f"- {country}")

print(f"\nTotal countries: {len(countries)}")

print("\nCities by country:")
for country in countries:
    cities = df[df['state'] == country]['city'].unique()
    print(f"{country}: {list(cities)}")