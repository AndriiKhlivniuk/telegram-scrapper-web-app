import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

def add_users_sheet(group_name, participants):

    sheet = client.open("users")

    size = len(sheet.worksheets())
    worksheet = sheet.add_worksheet(title=str(size), rows=100, cols=20)

    # Select the last sheet in the spreadsheet
    worksheet = sheet.get_worksheet(size)

    # Write the data to the sheet
    data = [["Username", "Name", "Group"]]

    for user in participants:
        if user.username:
            username = user.username
        else:
            username = ""
        if user.first_name:

            first_name = user.first_name
        else:
            first_name = ""
        if user.last_name:
            last_name = user.last_name
        else:
            last_name = ""
        name= (first_name + ' ' + last_name).strip()
        data.append([username, first_name+" "+last_name, group_name])

    worksheet.append_rows(data)
    return str(size)

def add_messages(data):
    sheet = client.open("messages")

    size = len(sheet.worksheets())
    worksheet = sheet.add_worksheet(title=str(size), rows=100, cols=20)

    # Select the last sheet in the spreadsheet
    worksheet = sheet.get_worksheet(size)
    worksheet.append_rows(data)
    return(str(size))