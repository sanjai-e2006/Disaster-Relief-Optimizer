"""
Test script to demonstrate the resource allocation algorithm.
"""

import sys
import os
sys.path.append('src')

from resource_allocator import ResourceAllocator

def test_resource_allocation():
    """Test the resource allocation algorithm with sample disasters."""
    
    print('🚨 RESOURCE ALLOCATION ALGORITHM TEST')
    print('=' * 50)
    
    # Initialize allocator
    allocator = ResourceAllocator()
    
    # Example disasters with different severities
    test_disasters = [
        {
            'severity': 'High',
            'people_affected': 5000,
            'disaster_type': 'earthquake',
            'location': 'City A'
        },
        {
            'severity': 'Medium', 
            'people_affected': 2000,
            'disaster_type': 'flood',
            'location': 'City B'
        },
        {
            'severity': 'Low',
            'people_affected': 800,
            'disaster_type': 'drought', 
            'location': 'City C'
        }
    ]
    
    # Available resources
    available_resources = {
        'Food Kits': 10000,
        'Water Packs': 15000,
        'Medicine Kits': 5000,
        'Shelter Units': 3000
    }
    
    print('AVAILABLE RESOURCES:')
    for resource, amount in available_resources.items():
        print(f'  {resource}: {amount:,}')
    print()
    
    # Allocate resources
    result = allocator.allocate_resources(test_disasters, available_resources)
    
    print('ALLOCATION RESULTS BY DISASTER:')
    print('-' * 40)
    for i, allocation in enumerate(result['allocations']):
        severity = allocation['severity']
        location = allocation['location']
        people = allocation['people_affected']
        
        print(f'Disaster {i+1}: {severity} Severity - {location}')
        print(f'  People Affected: {people:,}')
        print(f'  Allocated Resources:')
        print(f'    Food Kits: {allocation["allocated"]["Food Kits"]:,}')
        print(f'    Water Packs: {allocation["allocated"]["Water Packs"]:,}') 
        print(f'    Medicine Kits: {allocation["allocated"]["Medicine Kits"]:,}')
        print(f'    Shelter Units: {allocation["allocated"]["Shelter Units"]:,}')
        print(f'  Fulfillment Rate: {allocation["fulfillment_rate"]*100:.1f}%')
        print()
    
    print('SUMMARY STATISTICS:')
    print('-' * 30)
    stats = result['summary_stats']
    print(f'Total Disasters: {stats["total_disasters"]}')
    print(f'Total People Affected: {stats["total_people_affected"]:,}')
    print()
    
    print('Resource Utilization Rates:')
    for resource, rate in stats['resource_utilization'].items():
        print(f'  {resource}: {rate:.1f}%')
    
    print()
    print('Average Fulfillment by Severity:')
    for severity, rate in stats['avg_fulfillment_by_severity'].items():
        print(f'  {severity}: {rate:.1f}%')

if __name__ == "__main__":
    test_resource_allocation()