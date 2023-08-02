import pandas as pd
import requests
import io
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pytz
url = "https://api.easyecom.io/getApiToken"
email = "karan.ahirwar@selectbrands.in"
password = "Annu@2023"
payload = {
    "email": email,
    "password": password
}
headers = {}
response = requests.request("POST", url, headers=headers, data=payload)
data = response.json()
api_token = data['data']["api_token"]
BaseURL = "https://api.easyecom.io"
inventory_url = f"{BaseURL}/wms/V2/getInventoryDetails"
params = {
    "api_token": api_token,
    "includeLocations": "1"
}
final = pd.DataFrame()
while inventory_url:
    try:
        response = requests.get(inventory_url, params=params)
        response.raise_for_status()
        data_raw = response.json()
        if "data" in data_raw and "inventoryData" in data_raw["data"]:
            df = pd.DataFrame(data_raw["data"]["inventoryData"])
            final = pd.concat([final, df], ignore_index=True)

        if "data" in data_raw and "nextUrl" in data_raw["data"]:
            inventory_url = f"{BaseURL}{data_raw['data']['nextUrl']}"
        else:
            inventory_url = None

    except requests.exceptions.RequestException as e:
        print("An error occurred during the request:", e)
        break

    except Exception as e:
        print("An unexpected error occurred:", e)
        break
final_raw=final[['description','sku',"brand",'companyId', 'companyName', 'location_key', 'companyProductId',
       'productId','reservedInventory','availableInventory', 'creationDate','lastUpdateDate']].copy()
final_raw["reservedInventory"]=final_raw["reservedInventory"].fillna(0)
final_raw["availableInventory"]=final_raw["availableInventory"].fillna(0)
final_raw["creationDate"]=pd.to_datetime(final_raw["creationDate"]).dt.date
final_raw["lastUpdateDate"]=pd.to_datetime(final_raw["lastUpdateDate"]).dt.date
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('./emerald-cab-384306-b8566336d0b0.json', scope)
client = gspread.authorize(creds)
gsB2c = client.open('Easycom_Live_Inventory')
sheetb2c = gsB2c.worksheet('Raw')
sheetb2c.clear()
set_with_dataframe(sheetb2c,final_raw)
print("Data Is Saved Successfully.")
