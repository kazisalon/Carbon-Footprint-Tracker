import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json

class CarbonFootprintTracker:
    def __init__(self, filename='carbon_data.json'):
        self.filename = filename
        self.data = self._load_data()
        
        # CO2 emission factors (kg CO2 per unit)
        self.emission_factors = {
            'electricity': 0.4,  # per kWh
            'transportation': 0.2,  # per km
            'heating': 0.2,  # per m³ of natural gas
            'waste': 0.5  # per kg of waste
        }

    def _load_data(self):
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def _save_data(self):
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def add_entry(self, electricity=0, transportation=0, heating=0, waste=0, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # Calculate CO2 emissions for each category
        emissions = {
            'electricity': electricity * self.emission_factors['electricity'],
            'transportation': transportation * self.emission_factors['transportation'],
            'heating': heating * self.emission_factors['heating'],
            'waste': waste * self.emission_factors['waste']
        }
        
        # Calculate total emissions
        total_emissions = sum(emissions.values())

        entry = {
            'date': date,
            'inputs': {
                'electricity': electricity,
                'transportation': transportation,
                'heating': heating,
                'waste': waste
            },
            'emissions': emissions,
            'total_emissions': total_emissions
        }

        self.data.append(entry)
        self._save_data()
        return entry

    def get_summary(self):
        if not self.data:
            return "No data available"
        
        df = pd.DataFrame([
            {
                'date': entry['date'],
                'total_emissions': entry['total_emissions'],
                **entry['emissions']
            }
            for entry in self.data
        ])
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        summary = {
            'total_emissions': df['total_emissions'].sum(),
            'average_daily_emissions': df['total_emissions'].mean(),
            'highest_emission_day': df.loc[df['total_emissions'].idxmax()]['date'].strftime('%Y-%m-%d'),
            'lowest_emission_day': df.loc[df['total_emissions'].idxmin()]['date'].strftime('%Y-%m-%d'),
            'number_of_entries': len(df)
        }
        
        return summary

    def visualize_emissions(self):
        if not self.data:
            print("No data available to visualize")
            return

        df = pd.DataFrame([
            {
                'date': entry['date'],
                **entry['emissions']
            }
            for entry in self.data
        ])
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Create the visualization
        plt.figure(figsize=(12, 6))
        
        # Plot stacked area chart
        plt.stackplot(df['date'], 
                     df['electricity'], 
                     df['transportation'],
                     df['heating'],
                     df['waste'],
                     labels=['Electricity', 'Transportation', 'Heating', 'Waste'])
        
        plt.title('Carbon Emissions Over Time')
        plt.xlabel('Date')
        plt.ylabel('CO₂ Emissions (kg)')
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()

    def get_recommendations(self):
        if not self.data:
            return "No data available for recommendations"

        df = pd.DataFrame([
            {
                'date': entry['date'],
                **entry['emissions']
            }
            for entry in self.data
        ])

        # Calculate average emissions for each category
        averages = df.mean()
        recommendations = []

        # Generate recommendations based on highest emission sources
        highest_category = averages.nlargest(1).index[0]
        
        recommendations_map = {
            'electricity': [
                "Consider switching to LED bulbs",
                "Use natural light when possible",
                "Upgrade to energy-efficient appliances"
            ],
            'transportation': [
                "Use public transportation when possible",
                "Consider carpooling",
                "Plan efficient routes to reduce distance"
            ],
            'heating': [
                "Improve home insulation",
                "Use a programmable thermostat",
                "Service heating system regularly"
            ],
            'waste': [
                "Increase recycling efforts",
                "Start composting organic waste",
                "Reduce single-use items"
            ]
        }

        recommendations.extend(recommendations_map[highest_category])
        return recommendations

# Example usage
def main():
    # Create tracker instance
    tracker = CarbonFootprintTracker()
    
    while True:
        print("\nCarbon Footprint Tracker")
        print("1. Add new entry")
        print("2. View summary")
        print("3. Visualize emissions")
        print("4. Get recommendations")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            try:
                electricity = float(input("Enter electricity usage (kWh): "))
                transportation = float(input("Enter transportation distance (km): "))
                heating = float(input("Enter heating usage (m³): "))
                waste = float(input("Enter waste produced (kg): "))
                
                entry = tracker.add_entry(
                    electricity=electricity,
                    transportation=transportation,
                    heating=heating,
                    waste=waste
                )
                print("\nEntry added successfully!")
                print(f"Total emissions for this entry: {entry['total_emissions']:.2f} kg CO2")
                
            except ValueError:
                print("Please enter valid numbers")
                
        elif choice == '2':
            summary = tracker.get_summary()
            print("\nEmissions Summary:")
            for key, value in summary.items():
                if isinstance(value, (int, float)):
                    print(f"{key.replace('_', ' ').title()}: {value:.2f}")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value}")
                    
        elif choice == '3':
            tracker.visualize_emissions()
            
        elif choice == '4':
            recommendations = tracker.get_recommendations()
            print("\nRecommendations for reducing your carbon footprint:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
                
        elif choice == '5':
            print("Thank you for using the Carbon Footprint Tracker!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()