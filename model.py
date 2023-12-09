import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
import sys
import json

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

    # Create a pipeline with standardization and the model
    pipeline = Pipeline([
        ('scaler', StandardScaler()),  # Standardization
        ('rf', RandomForestRegressor(random_state=42))  # Random Forest Regressor
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
    print(f"Mean Squared Error: {mse}")
    print(f"R² Score: {r2}")

    return best_model

def calculate_collateral(reputation_score, loan_amount):
    try:
        loan_amount = float(loan_amount)
    except ValueError:
        print("Could not convert to a number.")
    # Assuming a base collateral rate
    base_collateral_rate = 0.5  # 50% of the loan amount

    # Adjusting the collateral based on reputation
    # Higher reputation score leads to lower collateral requirement
    collateral_factor = 10 - (reputation_score / 100)
    collateral_required = loan_amount * base_collateral_rate * collateral_factor

    return collateral_required


def main(input):
    model = train_model()
    try:
        # Parse the JSON string
        new_miner = json.loads(input)

        # Now json_data is a Python dictionary
        print("Parsed JSON:", new_miner)

        # Example of accessing a value (replace 'key' with an actual key from your JSON)
        # value = json_data['key']
        # print("Value for key 'key':", value)

        predicted_score = model.predict([ [new_miner['AdjustedPower'], new_miner['WinCount'], new_miner['SectorTotal'], new_miner['SectorActive'], new_miner['SectorFaults'], new_miner['SectorRecoveries']] ])
        print(f"Predicted Reputation Score: {predicted_score[0]}")

        print(f"Collateral Required: {calculate_collateral(predicted_score[0], new_miner['LoanAmount'])}")
    except json.JSONDecodeError as e:
        print("Invalid JSON string:", e)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Must pass arguments. Format: [command] input_dir")
        sys.exit()
    main(sys.argv[1])