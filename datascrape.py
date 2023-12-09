
from bs4 import BeautifulSoup
import requests
import sys
import json
import re

def extract_sectors_numbers_from_html(span_elements):
    """
    Extracts numbers from a list of BeautifulSoup span elements.

    :param span_elements: List of BeautifulSoup span elements.
    :return: List of extracted numbers.
    """
    numbers = []

    for tag in span_elements:
        # Extract numbers using regular expression
        number = re.findall(r'\d[\d,]*', tag.text)
        if number:
            numbers.append(number[0].replace(',', ''))  # Remove commas for pure numerical value

    return numbers

def parseHTML(selected_tag):
    return selected_tag.text.strip().split()[0]

def convert_to_number(miner):
    for key in miner:
        try:
            # Attempt to convert the string to a float first
            value = float(miner[key])
            # If the float value is actually an integer, convert it to an integer
            if value.is_integer():
                value = int(value)
            miner[key] = value
        except ValueError:
            # If conversion fails, it's not a number, so we leave it as is
            pass
    return miner

def scrape_miner_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')

        # Example of extracting specific data - this will need to be customized
        adjusted_power = parseHTML(soup.select('div.flex.items-center.justify-between.w-full>p.font-medium.text-2xl')[0])
        win_count = soup.find('div', class_='text-sm items-center justify-end flex').text.strip().split()[-1]
        sectors = extract_sectors_numbers_from_html(soup.select('div.text-sm.mt-2.items-center.justify-between.flex > div span'))
        # powergrowth = soup.select('div.bg-white.rounded-md.pb-6.my-4 > div.mx-8.border.border-background.rounded-sm.p-4 > div.flex.items-center.w-full.mb-2 > p.text-sm.w-5\/12.text-left')

        # print(powergrowth)
        # ... more data extraction based on the page structure

        return {
            'Address': url.split('/')[-1],
            'AdjustedPower': adjusted_power,
            'WinCount': win_count,
            'SectorTotal': sectors[0],
            'SectorActive': sectors[1],
            'SectorFaults': sectors[2],
            'SectorRecoveries': sectors[3]
        }
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def main(address):
    miner_url = f'https://filfox.info/en/address/{address}'
    new_miner = scrape_miner_data(miner_url)
    new_miner = convert_to_number(new_miner)
    # predicted_score = best_model.predict([ [new_miner['AdjustedPower'], new_miner['WinCount'], new_miner['SectorTotal'], new_miner['SectorActive'], new_miner['SectorFaults'], new_miner['SectorRecoveries']] ])
    # print(f"Predicted Reputation Score: {predicted_score[0]}")

    with open('newminer.json', 'w') as json_file:
        json.dump(new_miner, json_file, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Must pass arguments. Format: [command] input_dir")
        sys.exit()
    main(sys.argv[1])