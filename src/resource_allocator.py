"""
Resource allocation algorithm for disaster relief optimization.
Implements priority-based distribution of relief resources.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class ResourceAllocator:
    def __init__(self):
        """Initialize resource allocator with default settings."""
        self.severity_weights = {
            'High': 0.5,    # 50% of resources
            'Medium': 0.3,  # 30% of resources
            'Low': 0.2      # 20% of resources
        }
        
        self.resource_types = ['Food Kits', 'Water Packs', 'Medicine Kits', 'Shelter Units']
        
        # Default resource ratios (can be adjusted based on disaster type)
        self.default_resource_ratios = {
            'Food Kits': 0.3,
            'Water Packs': 0.35,
            'Medicine Kits': 0.15,
            'Shelter Units': 0.2
        }
        
        # Disaster type specific adjustments
        self.disaster_adjustments = {
            'flood': {'Water Packs': 1.2, 'Shelter Units': 1.3, 'Medicine Kits': 1.1},
            'earthquake': {'Shelter Units': 1.5, 'Medicine Kits': 1.3, 'Food Kits': 1.1},
            'cyclone': {'Shelter Units': 1.4, 'Water Packs': 1.2, 'Food Kits': 1.1},
            'drought': {'Water Packs': 1.6, 'Food Kits': 1.3, 'Medicine Kits': 0.8},
            'landslide': {'Medicine Kits': 1.4, 'Shelter Units': 1.2, 'Food Kits': 1.1},
            'wildfire': {'Medicine Kits': 1.3, 'Water Packs': 1.2, 'Shelter Units': 1.1}
        }
    
    def calculate_base_need(self, people_affected: int, severity: str) -> Dict[str, int]:
        """Calculate base resource needs based on people affected and severity."""
        # Base ratios per person (can be adjusted based on domain expertise)
        base_per_person = {
            'Food Kits': 0.8,      # Less than 1 kit per person (family sharing)
            'Water Packs': 1.2,    # More water needed
            'Medicine Kits': 0.3,  # Less medicine kits needed
            'Shelter Units': 0.25  # Multiple people per shelter unit
        }
        
        # Severity multipliers
        severity_multipliers = {
            'High': 1.5,
            'Medium': 1.2,
            'Low': 1.0
        }
        
        multiplier = severity_multipliers.get(severity, 1.0)
        
        base_needs = {}
        for resource, ratio in base_per_person.items():
            base_needs[resource] = max(1, int(people_affected * ratio * multiplier))
        
        return base_needs
    
    def adjust_for_disaster_type(self, base_needs: Dict[str, int], disaster_type: str) -> Dict[str, int]:
        """Adjust resource needs based on disaster type."""
        disaster_type_lower = disaster_type.lower()
        
        # Find matching disaster type (partial match)
        adjustments = {}
        for disaster_key, adjustment_factors in self.disaster_adjustments.items():
            if disaster_key in disaster_type_lower or disaster_type_lower in disaster_key:
                adjustments = adjustment_factors
                break
        
        # Apply adjustments
        adjusted_needs = base_needs.copy()
        for resource, factor in adjustments.items():
            if resource in adjusted_needs:
                adjusted_needs[resource] = int(adjusted_needs[resource] * factor)
        
        return adjusted_needs
    
    def allocate_resources(self, 
                          disasters: List[Dict], 
                          available_resources: Dict[str, int]) -> Dict:
        """
        Allocate resources across multiple disasters based on priority.
        
        Args:
            disasters: List of disaster dictionaries with keys:
                      'severity', 'people_affected', 'disaster_type', 'location'
            available_resources: Dictionary of available resources
        
        Returns:
            Dictionary with allocation results
        """
        
        # Step 1: Calculate needs for each disaster
        disaster_needs = []
        total_needs = {resource: 0 for resource in self.resource_types}
        
        for i, disaster in enumerate(disasters):
            # Calculate base needs
            base_needs = self.calculate_base_need(
                disaster['people_affected'], 
                disaster['severity']
            )
            
            # Adjust for disaster type
            adjusted_needs = self.adjust_for_disaster_type(
                base_needs, 
                disaster['disaster_type']
            )
            
            disaster_info = {
                'index': i,
                'severity': disaster['severity'],
                'people_affected': disaster['people_affected'],
                'disaster_type': disaster['disaster_type'],
                'location': disaster.get('location', 'Unknown'),
                'needs': adjusted_needs,
                'priority_score': self._calculate_priority_score(disaster)
            }
            
            disaster_needs.append(disaster_info)
            
            # Add to total needs
            for resource, amount in adjusted_needs.items():
                total_needs[resource] += amount
        
        # Step 2: Sort disasters by priority (severity and people affected)
        disaster_needs.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Step 3: Allocate resources based on priority and availability
        allocations = []
        remaining_resources = available_resources.copy()
        
        for disaster_info in disaster_needs:
            allocation = self._allocate_to_single_disaster(
                disaster_info, 
                remaining_resources,
                total_needs
            )
            
            allocations.append(allocation)
            
            # Update remaining resources
            for resource, amount in allocation['allocated'].items():
                remaining_resources[resource] -= amount
        
        # Step 4: Prepare summary
        summary = self._prepare_allocation_summary(
            disasters, 
            allocations, 
            available_resources, 
            remaining_resources,
            total_needs
        )
        
        return summary
    
    def _calculate_priority_score(self, disaster: Dict) -> float:
        """Calculate priority score for disaster ranking."""
        severity_scores = {'High': 3, 'Medium': 2, 'Low': 1}
        
        severity_score = severity_scores.get(disaster['severity'], 1)
        people_affected = disaster['people_affected']
        
        # Normalize people affected (log scale to prevent extreme values)
        normalized_people = np.log10(max(1, people_affected))
        
        # Combined score
        priority_score = severity_score * 100 + normalized_people
        
        return priority_score
    
    def _allocate_to_single_disaster(self, 
                                   disaster_info: Dict, 
                                   available_resources: Dict[str, int],
                                   total_needs: Dict[str, int]) -> Dict:
        """Allocate resources to a single disaster."""
        allocated = {}
        unmet_needs = {}
        
        severity = disaster_info['severity']
        needs = disaster_info['needs']
        
        for resource in self.resource_types:
            needed = needs.get(resource, 0)
            available = available_resources.get(resource, 0)
            
            if needed <= available:
                # Can fulfill complete need
                allocated[resource] = needed
                unmet_needs[resource] = 0
            else:
                # Partial allocation based on severity priority
                severity_weight = self.severity_weights[severity]
                
                # Calculate fair share based on proportion of total need
                if total_needs[resource] > 0:
                    proportion = needed / total_needs[resource]
                    fair_allocation = int(available * proportion * severity_weight)
                    allocated[resource] = min(fair_allocation, available, needed)
                else:
                    allocated[resource] = 0
                
                unmet_needs[resource] = needed - allocated[resource]
        
        return {
            'disaster_index': disaster_info['index'],
            'severity': severity,
            'people_affected': disaster_info['people_affected'],
            'disaster_type': disaster_info['disaster_type'],
            'location': disaster_info['location'],
            'needed': needs,
            'allocated': allocated,
            'unmet_needs': unmet_needs,
            'fulfillment_rate': self._calculate_fulfillment_rate(needs, allocated)
        }
    
    def _calculate_fulfillment_rate(self, needs: Dict, allocated: Dict) -> float:
        """Calculate overall fulfillment rate for a disaster."""
        total_need = sum(needs.values())
        total_allocated = sum(allocated.values())
        
        if total_need == 0:
            return 1.0
        
        return total_allocated / total_need
    
    def _prepare_allocation_summary(self, 
                                  disasters: List[Dict],
                                  allocations: List[Dict],
                                  available_resources: Dict[str, int],
                                  remaining_resources: Dict[str, int],
                                  total_needs: Dict[str, int]) -> Dict:
        """Prepare comprehensive allocation summary."""
        
        # Calculate total allocated by resource type
        total_allocated = {resource: 0 for resource in self.resource_types}
        for allocation in allocations:
            for resource, amount in allocation['allocated'].items():
                total_allocated[resource] += amount
        
        # Calculate utilization rates
        utilization_rates = {}
        for resource in self.resource_types:
            available = available_resources.get(resource, 0)
            if available > 0:
                utilization_rates[resource] = (total_allocated[resource] / available) * 100
            else:
                utilization_rates[resource] = 0
        
        # Calculate overall fulfillment by severity
        severity_stats = {'High': [], 'Medium': [], 'Low': []}
        for allocation in allocations:
            severity = allocation['severity']
            severity_stats[severity].append(allocation['fulfillment_rate'])
        
        avg_fulfillment_by_severity = {}
        for severity, rates in severity_stats.items():
            if rates:
                avg_fulfillment_by_severity[severity] = np.mean(rates) * 100
            else:
                avg_fulfillment_by_severity[severity] = 0
        
        return {
            'allocations': allocations,
            'summary_stats': {
                'total_disasters': len(disasters),
                'total_people_affected': sum(d['people_affected'] for d in disasters),
                'resource_utilization': utilization_rates,
                'avg_fulfillment_by_severity': avg_fulfillment_by_severity,
                'total_allocated': total_allocated,
                'remaining_resources': remaining_resources,
                'total_needs': total_needs
            }
        }
    
    def allocate_single_disaster(self, 
                               severity: str,
                               people_affected: int,
                               disaster_type: str,
                               available_resources: Dict[str, int]) -> Dict:
        """Allocate resources for a single disaster (simplified interface)."""
        
        disaster = {
            'severity': severity,
            'people_affected': people_affected,
            'disaster_type': disaster_type,
            'location': 'Single Location'
        }
        
        result = self.allocate_resources([disaster], available_resources)
        
        if result['allocations']:
            return result['allocations'][0]
        else:
            return {}

# Example usage and testing
if __name__ == "__main__":
    # Test the resource allocator
    allocator = ResourceAllocator()
    
    # Example disasters
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
    test_resources = {
        'Food Kits': 10000,
        'Water Packs': 15000,
        'Medicine Kits': 5000,
        'Shelter Units': 3000
    }
    
    # Allocate resources
    result = allocator.allocate_resources(test_disasters, test_resources)
    
    print("Resource Allocation Results:")
    print(f"Total disasters: {result['summary_stats']['total_disasters']}")
    print(f"Total people affected: {result['summary_stats']['total_people_affected']}")
    print("\nResource Utilization:")
    for resource, rate in result['summary_stats']['resource_utilization'].items():
        print(f"{resource}: {rate:.1f}%")