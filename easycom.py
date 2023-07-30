import pandas as pd
import requests
import io
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
BaseURL = "https://api.easyecom.io"
url = f"{BaseURL}/access/token"
email = "karan.ahirwar@selectbrands.in"
password = "Annu@2023"
location_key = "en11797218225"
payload = {
    "email": email,
    "password": password,
    "location_key": location_key
}

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        access_token = data["data"]["token"]["jwt_token"]
        print("Credentials created successfully.")
    else:
        print(f"Error: API request failed with status code {response.status_code}")
        print("Response:", response.text)
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
x_api_key = "0f68a914017e171f9335ddea23a55f842f71d0b5"
inventory_endpoint =  "https://api.easyecom.io/inventory/getInventorySnapshotApi?start_date=2023-07-29 00:00:00&end_date=2023-07-29-23:59:59"
headers = {
    "Authorization": f"Bearer {access_token}",
    "x-api-key": x_api_key
}
try:
    response = requests.get(inventory_endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Inventory data is generated")
    else:
        print(f"Error: API request failed with status code {response.status_code}")
        print("Response:", response.text)
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
file_url=data["data"][0]["file_url"]
response = requests.get(file_url)
df = pd.read_csv(io.BytesIO(response.content))
sorted_df=df[['Description', 'SKU', 'Brand', 'Available Quantity']].copy()
sorted_df["SKU"]=sorted_df["SKU"].str.replace("`", "").str.strip()
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('./emerald-cab-384306-b8566336d0b0.json', scope)
client = gspread.authorize(creds)
gsB2c = client.open('Easycom_Live_Inventory')
sheetb2c=gsB2c.worksheet('Raw')
sheetb2c.clear()
set_with_dataframe(sheetb2c,sorted_df)
print("Data Is Saved Successfully.")
