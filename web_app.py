from fastapi import FastAPI, Request, Depends, HTTPException, Response, Cookie
from telethon import TelegramClient
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse 
from fastapi.templating import Jinja2Templates
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from sheets import*
import secrets
from typing import Union


api_id = 27485413
api_hash = 'd727d551fa10b6709eb13dea02cf9bb7'


groups_id = set()
channels_id = set()
groups = []
channels = []
all_chats = []

phone_glob = ["111111"]

app = FastAPI()


templates = Jinja2Templates(directory="templates/")

# client connection
client = TelegramClient('session_name', api_id, api_hash)



######AUTH##########

users = set()
@app.get("/adminlogin")
def adminlogin(request: Request):
    return templates.TemplateResponse('adminlogin.html', context={'request': request})

@app.get("/register")
def generate_user(ident: str):
    if ident == 'admin':
        hash = secrets.token_hex(16)
        users.add(hash)
        return "Your token for login(save it): "+hash
    else:
        return {"message": "Not authorized user"}

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse('login.html', context={'request': request})

def validate_token(token: Union[str, None] = Cookie(default=None)):

    if token != "secret-token":
        raise HTTPException(status_code=400, detail="Invalid token")
    return token

@app.post("/token/{hash}")
def login(hash: str, response: Response):

    if hash in users:
        response.set_cookie(key="token", value="secret-token")
        return {"message": "Token has been stored in the cookie."}
    else:
        return {"message": "Not authorized user"}


# @app.get("/secure")
# def secure(token: str = Depends(validate_token)):
#     return {"message": "Welcome to the secure endpoint!"}

######################

@app.get("/")
def send_code(request: Request, token: str = Depends(validate_token)):

    return templates.TemplateResponse('sendcode.html', context={'request': request})


@app.get("/sendcode")
async def send_code(phone:str, request: Request, token: str = Depends(validate_token)):
    
    
    phone_glob[0] = phone
    await client.connect()
    global sent_code
    sent_code = await client.send_code_request(phone)
    
    return templates.TemplateResponse('verifynumber.html', context={'request': request})


@app.get("/verif")
async def verify(code:str, request: Request):

    await client.sign_in(phone_glob[0], int(code))
    groups.clear()
    channels.clear()
    groups_id.clear()
    channels_id.clear()

    return await main_menu()

@app.get("/parse")
async def groups_channels(token: str = Depends(validate_token)):

    chats = []

    last_date = None
    size_chats = 200

    await client.start()
    result =  await client(GetDialogsRequest(
                offset_date=last_date,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=size_chats,
                hash = 0
            ))
    chats = result.chats
    
    for chat in chats:
        try:
            if chat.megagroup and chat.id not in groups_id:
                groups_id.add(chat.id)
                groups.append(chat)
            if chat.broadcast and chat.id not in channels_id:
                channels_id.add(chat.id)
                channels.append(chat)
        except:
            continue
    return JSONResponse(content="chats parsed")
        

@app.get("/main")
async def main_menu(token: str = Depends(validate_token)):
    

    await groups_channels()
    
    return FileResponse('index.html')


@app.get("/getusers")
def get_users(request: Request, token: str = Depends(validate_token)):

    result = {}
    for i, group in enumerate(groups):
       result[i] = group.title

    return templates.TemplateResponse('groups.html', context={'request': request, 'result': result})

@app.post("/parsegroup/{group_id}")
async def parseusers(group_id:int, request: Request):
    group = groups[group_id]
    limit = 1000
    participants = await client.get_participants(group, limit=limit)

    sheet = add_users_sheet(group.title, participants)
    result = {"sheet":sheet, "link": "https://docs.google.com/spreadsheets/d/1ep3ewL78nSJiooT9LcHpnihuo9Wddls4LNHYJ5q1fvY/edit#gid=679545068"}

    return templates.TemplateResponse('results.html', context={'request': request, 'result': result})


@app.get("/keyword")
def searh_messages(request: Request):
    all_chats.clear()
    all_chats.extend(groups)
    all_chats.extend(channels)

    result = {}
    for i, chat in enumerate(all_chats):
        result[i] = chat.title
    
    return templates.TemplateResponse('keyword.html', context={'request': request, 'result': result})

@app.get("/parsechat")
async def parsechat(chat_id:int, keyword:str, request: Request):

    chat = all_chats[chat_id]
    data = [["Username", "Name", "Group", "Keyword", "Message"]]

    i = 0
    async for message in (client.iter_messages(chat)):
        if message.message:

            if keyword in message.message:
                if message.from_id:
                    user = await client.get_entity(message.from_id)

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
                else:
                    username = ""
                    first_name = "admin"
                    last_name = ""

                data.append(
                            [username+"     ", first_name+"     "+last_name+"     ",
                            chat.title+"     ", keyword+"     ", message.message]
                            )
        i += 1
        if i>10000:
            break

    sheet = add_messages(data)
    result = {"sheet":sheet, "link": "https://docs.google.com/spreadsheets/d/1peWbcQ4vHjK_CvS0mS2PQtdus3oyQyHs3EjCXL0X6sI/edit#gid=302727912"}
    
    return templates.TemplateResponse('results.html', context={'request': request, 'result': result})

