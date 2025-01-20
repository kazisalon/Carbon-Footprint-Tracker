import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import csv
import os
import calendar

class EnhancedCarbonTracker:
    def __init__(self, data_file='carbon_data.json', goals_file='carbon_goals.json'):
        self.data_file = data_file
        self.goals_file = goals_file
        self.data = self._load_data(data_file)
        self.goals = self._load_data(goals_file)
        
        # Emission factors (kg CO2 per unit)
        self.emission_factors = {
            'electricity': 0.4,  # per kWh
            'transportation': 0.2,  # per km
            'heating': 0.2,  # per m³
            'waste': 0.5,  # per kg
            'water': 0.3,  # per m³
            'food': 1.2,  # per kg
            'electronics': 0.8  # per hour
        }

    def _load_data(self, filename):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def _save_data(self, data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    def set_goal(self, category, target_value, target_date):
        """Set a reduction goal for a specific category"""
        goal = {
            'category': category,
            'target_value': target_value,
            'target_date': target_date,
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'start_value': self.get_average_emissions(category)
        }
        self.goals.append(goal)
        self._save_data(self.goals, self.goals_file)

    def track_goals(self):
        """Track progress towards goals"""
        progress_report = []
        for goal in self.goals:
            current_value = self.get_average_emissions(goal['category'])
            total_reduction = goal['start_value'] - current_value
            target_reduction = goal['start_value'] - goal['target_value']
            if target_reduction == 0:
                progress = 100
            else:
                progress = (total_reduction / target_reduction) * 100
            
            progress_report.append({
                'category': goal['category'],
                'progress': min(100, max(0, progress)),
                'target_date': goal['target_date'],
                'current_value': current_value,
                'target_value': goal['target_value']
            })
        return progress_report

    def add_entry(self, date=None, **kwargs):
        """Add a new entry with flexible categories"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        emissions = {}
        for category, value in kwargs.items():
            if category in self.emission_factors:
                emissions[category] = value * self.emission_factors[category]

        entry = {
            'date': date,
            'inputs': kwargs,
            'emissions': emissions,
            'total_emissions': sum(emissions.values())
        }

        self.data.append(entry)
        self._save_data(self.data, self.data_file)
        return entry

    def get_monthly_report(self, year, month):
        """Generate a detailed monthly report"""
        df = self._get_dataframe()
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter for specific month
        monthly_data = df[
            (df['date'].dt.year == year) & 
            (df['date'].dt.month == month)
        ]

        if monthly_data.empty:
            return "No data available for specified month"

        report = {
            'total_emissions': monthly_data['total_emissions'].sum(),
            'daily_average': monthly_data['total_emissions'].mean(),
            'highest_day': {
                'date': monthly_data.loc[monthly_data['total_emissions'].idxmax()]['date'].strftime('%Y-%m-%d'),
                'emissions': monthly_data['total_emissions'].max()
            },
            'by_category': {
                category: monthly_data[f'emissions_{category}'].sum()
                for category in self.emission_factors.keys()
                if f'emissions_{category}' in monthly_data.columns
            }
        }
        return report

    def export_data(self, format='csv', filename=None):
        """Export data in various formats"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'carbon_data_export_{timestamp}'

        df = self._get_dataframe()

        if format == 'csv':
            df.to_csv(f'{filename}.csv', index=False)
        elif format == 'excel':
            df.to_excel(f'{filename}.xlsx', index=False)
        elif format == 'json':
            df.to_json(f'{filename}.json', orient='records')
        return f'Data exported to {filename}.{format}'

    def import_data(self, filename):
        """Import data from CSV file"""
        _, ext = os.path.splitext(filename)
        if ext == '.csv':
            df = pd.read_csv(filename)
        elif ext == '.xlsx':
            df = pd.read_excel(filename)
        else:
            raise ValueError("Unsupported file format")

        for _, row in df.iterrows():
            self.add_entry(**row.to_dict())

    def get_average_emissions(self, category):
        """Calculate average emissions for a category"""
        df = self._get_dataframe()
        if f'emissions_{category}' in df.columns:
            return df[f'emissions_{category}'].mean()
        return 0

    def _get_dataframe(self):
        """Convert data to DataFrame for analysis"""
        if not self.data:
            return pd.DataFrame()

        records = []
        for entry in self.data:
            record = {
                'date': entry['date'],
                'total_emissions': entry['total_emissions']
            }
            for category, value in entry['inputs'].items():
                record[f'input_{category}'] = value
            for category, value in entry['emissions'].items():
                record[f'emissions_{category}'] = value
            records.append(record)
        
        return pd.DataFrame(records)

    def visualize_trends(self, period='month'):
        """Create advanced visualizations"""
        df = self._get_dataframe()
        if df.empty:
            return "No data available for visualization"

        df['date'] = pd.to_datetime(df['date'])
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Plot 1: Total emissions trend
        sns.lineplot(data=df, x='date', y='total_emissions', ax=ax1)
        ax1.set_title('Total Emissions Over Time')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('CO₂ Emissions (kg)')

        # Plot 2: Emissions by category
        emissions_cols = [col for col in df.columns if col.startswith('emissions_')]
        df[emissions_cols].boxplot(ax=ax2)
        ax2.set_title('Emissions Distribution by Category')
        ax2.set_xlabel('Category')
        ax2.set_ylabel('CO₂ Emissions (kg)')
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    def get_insights(self):
        """Generate intelligent insights from the data"""
        df = self._get_dataframe()
        if df.empty:
            return "No data available for insights"

        df['date'] = pd.to_datetime(df['date'])
        insights = []

        # Trend analysis
        recent_trend = df.sort_values('date').tail(7)['total_emissions'].diff().mean()
        if recent_trend > 0:
            insights.append(f"Your emissions have increased by {abs(recent_trend):.2f} kg CO2 per day recently")
        elif recent_trend < 0:
            insights.append(f"Your emissions have decreased by {abs(recent_trend):.2f} kg CO2 per day recently")

        # Peak analysis
        peak_day = df.loc[df['total_emissions'].idxmax()]
        insights.append(f"Your highest emission day was {peak_day['date'].strftime('%Y-%m-%d')} "
                       f"with {peak_day['total_emissions']:.2f} kg CO2")

        # Category analysis
        emissions_cols = [col for col in df.columns if col.startswith('emissions_')]
        highest_category = df[emissions_cols].mean().idxmax()
        insights.append(f"Your largest source of emissions is {highest_category.replace('emissions_', '')}")

        return insights

def main():
    tracker = EnhancedCarbonTracker()
    
    while True:
        print("\nEnhanced Carbon Footprint Tracker")
        print("1. Add new entry")
        print("2. View monthly report")
        print("3. Visualize trends")
        print("4. Export data")
        print("5. Import data")
        print("6. Set reduction goal")
        print("7. Track goal progress")
        print("8. Get insights")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ")
        
        try:
            if choice == '1':
                date = input("Enter date (YYYY-MM-DD) or press Enter for today: ")
                date = date if date else None
                
                inputs = {}
                for category in tracker.emission_factors.keys():
                    value = float(input(f"Enter {category} usage: "))
                    inputs[category] = value
                
                entry = tracker.add_entry(date=date, **inputs)
                print(f"\nEntry added! Total emissions: {entry['total_emissions']:.2f} kg CO2")

            elif choice == '2':
                year = int(input("Enter year: "))
                month = int(input("Enter month (1-12): "))
                report = tracker.get_monthly_report(year, month)
                print(f"\nMonthly Report for {calendar.month_name[month]} {year}:")
                print(json.dumps(report, indent=2))

            elif choice == '3':
                tracker.visualize_trends()

            elif choice == '4':
                format_choice = input("Enter export format (csv/excel/json): ")
                filename = input("Enter filename (or press Enter for automatic): ")
                filename = filename if filename else None
                result = tracker.export_data(format=format_choice, filename=filename)
                print(result)

            elif choice == '5':
                filename = input("Enter filename to import: ")
                tracker.import_data(filename)
                print("Data imported successfully!")

            elif choice == '6':
                category = input("Enter category: ")
                target = float(input("Enter target value: "))
                date = input("Enter target date (YYYY-MM-DD): ")
                tracker.set_goal(category, target, date)
                print("Goal set successfully!")

            elif choice == '7':
                progress = tracker.track_goals()
                print("\nGoal Progress:")
                print(json.dumps(progress, indent=2))

            elif choice == '8':
                insights = tracker.get_insights()
                print("\nInsights:")
                for insight in insights:
                    print(f"- {insight}")

            elif choice == '9':
                print("Thank you for using the Enhanced Carbon Footprint Tracker!")
                break

            else:
                print("Invalid choice. Please try again.")

        except ValueError as e:
            print(f"Error: {e}")
            print("Please enter valid values.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()