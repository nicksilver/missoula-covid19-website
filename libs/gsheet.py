from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd 
import gspread



def gsheet2df(spreadsheet_id, key, scope):
    """
    Returns Google Sheet data as a pandas dataframe. 

    Need to setup service account first, then share service account email with the Google Sheet. 
    See https://www.datasciencelearner.com/get-data-of-google-sheets-using-pandas/
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key, scope)
    gc = gspread.authorize(credentials)

    workbook = gc.open_by_key(spreadsheet_id)
    sheet = workbook.get_worksheet(0)
    values = sheet.get_all_values()
    data = pd.DataFrame(values[1:], columns=values[0])
    return data
