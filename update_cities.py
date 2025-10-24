"""
Update disaster dataset with real city names instead of generic district names
"""

import pandas as pd
import random

# Read the current dataset
df = pd.read_csv('data/disaster_data.csv')

# Define real city names for each state/region
city_mapping = {
    'California': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'Fresno', 'Oakland', 'Santa Ana', 'Anaheim'],
    'Texas': ['Houston', 'San Antonio', 'Dallas', 'Austin', 'Fort Worth', 'El Paso', 'Arlington', 'Corpus Christi'],
    'Florida': ['Jacksonville', 'Miami', 'Tampa', 'Orlando', 'St. Petersburg', 'Hialeah', 'Tallahassee', 'Fort Lauderdale'],
    'New York': ['New York City', 'Buffalo', 'Rochester', 'Yonkers', 'Syracuse', 'Albany', 'New Rochelle', 'Mount Vernon'],
    'India': ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'],
    'Japan': ['Tokyo', 'Osaka', 'Yokohama', 'Nagoya', 'Sapporo', 'Fukuoka', 'Kobe', 'Hiroshima', 'Sendai', 'Kyoto'],
    'Philippines': ['Manila', 'Quezon City', 'Caloocan', 'Davao City', 'Cebu City', 'Zamboanga', 'Antipolo', 'Taguig', 'Pasig', 'Cagayan de Oro'],
    'Indonesia': ['Jakarta', 'Surabaya', 'Bandung', 'Bekasi', 'Medan', 'Tangerang', 'Depok', 'Semarang', 'Palembang', 'Makassar']
}

def update_district_to_city(row):
    """Update district column with real city names based on state."""
    state = row['state']
    if state in city_mapping:
        # Randomly select a city from the available cities for this state
        return random.choice(city_mapping[state])
    else:
        # Keep original district if state not in mapping
        return row['district']

# Set random seed for reproducibility
random.seed(42)

# Update the district column to city names
print("Updating district names to real city names...")
df['district'] = df.apply(update_district_to_city, axis=1)

# Rename the column from 'district' to 'city' for clarity
df = df.rename(columns={'district': 'city'})

# Save the updated dataset
df.to_csv('data/disaster_data.csv', index=False)

print("Dataset updated successfully!")
print("\nSample of updated data:")
print(df.head(10))

print(f"\nTotal records: {len(df)}")
print("\nCity distribution by state:")
for state in df['state'].unique():
    state_data = df[df['state'] == state]
    cities = state_data['city'].unique()
    print(f"{state}: {len(cities)} cities - {', '.join(cities[:5])}{'...' if len(cities) > 5 else ''}")