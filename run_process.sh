#!/bin/bash

# Define variables
SCRAPING_SCRIPT="./datascrape.py"
MODEL_SCRIPT="model.py"
GENERATED_JSON="newminer.json"

echo "Please enter your miner address:"
read address

echo "Please enter your loan amount:"
read loan

# Step 1: Run the scraping script
echo "Running scraping script..."
python $SCRAPING_SCRIPT $address

# Check if newminer.json is generated
if [ ! -f "$GENERATED_JSON" ]; then
    echo "Scraping failed: $GENERATED_JSON not found."
    exit 1
fi

modified_json=$(jq --arg varName "LoanAmount" --arg varValue $loan '.[$varName] = $varValue' "$GENERATED_JSON" | jq -c .)

export SERVICE_SOLVER="0xd4646ef9f7336b06841db3019b617ceadf435316"
export SERVICE_MEDIATORS="0x2d83ced7562e406151bd49c749654429907543b4"
export WEB3_PRIVATE_KEY=b6d9c1def985b0644e2bcb6fe5fa31f898fb080c222c347b25c67eaf8464fb2e

echo "Model is running on Lilypad..."
lilypad_output=$(lilypad run github.com/sambit-sankalp/testlily:v0.0.15 -i Prompt="$modified_json")

# Use grep and awk to extract the file path for stdout
file_path=$(echo "$lilypad_output" | grep -o "/tmp/lilypad/data/downloaded-files/[^ ]*/stdout")

# Check if the file path is extracted
if [ -z "$file_path" ]; then
    echo "Error: File path not found in the command output."
    exit 1
fi

echo "Predicting Reputation Score and Calculating Collateral..."
# Display the contents of the extracted file path
cat "$file_path"

# End of script
echo "Script completed."