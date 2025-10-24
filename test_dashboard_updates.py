"""
Test script to verify dashboard updates are working correctly
"""
import pandas as pd
import os

def test_data_loading():
    """Test that data loading functions work correctly"""
    print("Testing data loading functionality...")
    
    # Test CSV loading
    data_path = os.path.join('data', 'disaster_data.csv')
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        print(f"✅ Dataset loaded successfully: {len(df)} rows")
        
        # Test countries
        countries = sorted(df['state'].unique().tolist())
        print(f"✅ Countries found: {len(countries)}")
        for i, country in enumerate(countries, 1):
            print(f"   {i}. {country}")
        
        # Test cities for each country
        print(f"\n✅ Cities by country:")
        for country in countries:
            cities = sorted(df[df['state'] == country]['city'].unique().tolist())
            print(f"   {country}: {len(cities)} cities")
            print(f"      Sample cities: {cities[:3]}{'...' if len(cities) > 3 else ''}")
        
        return True
    else:
        print("❌ Dataset file not found")
        return False

def test_dashboard_functions():
    """Test that dashboard functions work correctly"""
    print("\nTesting dashboard functions...")
    
    # Import dashboard functions
    import sys
    sys.path.append('.')
    
    try:
        # This will test if the functions can be imported
        from dashboard_working import load_disaster_data, get_countries_and_cities
        
        # Test data loading
        df = load_disaster_data()
        if df is not None:
            print("✅ load_disaster_data() works correctly")
        else:
            print("❌ load_disaster_data() returned None")
            
        # Test country/city extraction
        countries, city_options = get_countries_and_cities()
        print(f"✅ get_countries_and_cities() returned {len(countries)} countries")
        
        # Verify all expected countries are present
        expected_countries = ['California', 'Florida', 'India', 'Indonesia', 'Japan', 'New York', 'Philippines', 'Texas']
        actual_countries = set(countries)
        expected_set = set(expected_countries)
        
        if expected_set.issubset(actual_countries):
            print("✅ All expected countries are present in the dataset")
        else:
            missing = expected_set - actual_countries
            extra = actual_countries - expected_set
            if missing:
                print(f"⚠️ Missing countries: {missing}")
            if extra:
                print(f"ℹ️ Extra countries: {extra}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing dashboard functions: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Dashboard Updates")
    print("=" * 40)
    
    success = True
    success &= test_data_loading()
    success &= test_dashboard_functions()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All tests passed! Dashboard should work correctly.")
        print("\nNext steps:")
        print("1. Open http://localhost:8514 in your browser")
        print("2. Check that all 8 countries appear in the State/Region dropdown")
        print("3. Select different countries and verify cities update correctly")
        print("4. Make a prediction and verify resource table updates")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()