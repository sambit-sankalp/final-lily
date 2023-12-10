import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import sys
import json
from tabulate import tabulate
from colorama import Fore, Style
import pandas as pd

# Load the data
def train_model():
    data = pd.read_csv('generated_data.csv')  # Replace with your file path

    # Selecting features and target
    features = ['AdjustedPower', 'WinCount', 'SectorTotal', 'SectorActive', 'SectorFaults', 'SectorRecoveries']
    target = 'ReputationScore'

    # Splitting the data
    X = data[features]
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), features)  # Use the features you want to scale
        ])

    # Create a pipeline with standardization and the model
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('rf', RandomForestRegressor(random_state=42))
    ])

    # Hyperparameter tuning
    parameters = {
        'rf__n_estimators': [100, 200],
        'rf__max_depth': [None, 10, 20],
        'rf__min_samples_split': [2, 5]
    }
    grid_search = GridSearchCV(pipeline, parameters, cv=3, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)

    # Best model
    best_model = grid_search.best_estimator_

    # Evaluate the model
    y_pred = best_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    # print(f"Mean Squared Error: {mse}")
    # print(f"R² Score: {r2}")
    table_data = [
        ["Metric", "Value"],
        ["Mean Squared Error", mse],
        ["R² Score", r2]
    ]

    colored_table = [
        [Fore.CYAN + Style.BRIGHT + cell if i == 0 else str(cell) for i, cell in enumerate(row)] for row in table_data
    ]

    print(Fore.YELLOW + "Model Performance" + Style.RESET_ALL)
    print(tabulate(colored_table, headers="firstrow", tablefmt="fancy_grid"))
    print(Style.RESET_ALL)

    return best_model

def calculate_collateral(reputation_score, loan_amount):
    try:
        loan_amount = float(loan_amount)
    except ValueError:
        print("Could not convert to a number.")
    
    # Calculate the minimum collateral percentage based on loan amount
    min_collateral_percentage = 0.2  # 10% of the loan amount
    
    # Adjusting the collateral based on reputation
    # Higher reputation score leads to lower collateral requirement
     # Reputation score is between 0 to 1000
    collateral_factor = 1 - (reputation_score / 1000)
    collateral_required = max(loan_amount * min_collateral_percentage, loan_amount * collateral_factor)

    return collateral_required


def main(input):
    model = train_model()
    try:
        # Parse the JSON string
        new_miner = json.loads(input)

        # Example of accessing a value (replace 'key' with an actual key from your JSON)
        # value = json_data['key']
        # print("Value for key 'key':", value)

        features = ['AdjustedPower', 'WinCount', 'SectorTotal', 'SectorActive', 'SectorFaults', 'SectorRecoveries']

        new_miner_data = [[new_miner['AdjustedPower'], new_miner['WinCount'], new_miner['SectorTotal'],
                   new_miner['SectorActive'], new_miner['SectorFaults'], new_miner['SectorRecoveries']]]

        # Convert the input data to a Pandas DataFrame
        new_miner_df = pd.DataFrame(new_miner_data, columns=features)

        predicted_score = model.predict(new_miner_df)
        table_data = [("Parameter", "Value"),
                ("Address", new_miner['Address']),
              ("Reputation Score", predicted_score[0]),
              ("Collateral Required", calculate_collateral(predicted_score[0], 1000))]

        # Display the table with colors
        colored_table = [
            [Fore.CYAN + Style.BRIGHT + str(cell) + Style.RESET_ALL for cell in row] for row in table_data
        ]

        print(Fore.YELLOW + "Our Model Prediction" + Style.RESET_ALL)
        print(tabulate(colored_table, tablefmt="fancy_grid"))
    except json.JSONDecodeError as e:
        print("Invalid JSON string:", e)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Must pass arguments. Format: [command] input_dir")
        sys.exit()
    main(sys.argv[1])