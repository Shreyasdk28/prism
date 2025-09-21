from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from shop_agent.namma_models import AddUserToSessionRequest, AddProductToSessionRequest, AddPrefsToSessionRequest
from shop_agent.utils import save_user_to_session, generate_session, save_product_to_session, save_prefs_to_session, get_session_by_session_id
from shop_agent.utils import run_using_object
import json
import os
import uuid

app = FastAPI()

# Path to your JSON file
JSON_FILE_PATH = "output/results.json"
HTML_FILE_PATH = "template/index.html"


@app.get("/", response_class=HTMLResponse)
async def get_index():
    if not os.path.exists(HTML_FILE_PATH):
        raise HTTPException(status_code=404, detail="HTML file not found")
    return FileResponse(HTML_FILE_PATH)


@app.get('/get-session')
async def get_user_id(request : AddUserToSessionRequest):
    return {
        "session" : generate_session()
    }

@app.post("/{user_session}/set-username")
async def set_username(user_session: str, request: AddUserToSessionRequest):
    try:
        save_user_to_session(session_id=user_session, username=request.username)
        return {"status": "200"}
    except Exception as e:
        return {"status": "500"}
    
@app.post("/{user_session}/set-product")
async def set_product(user_session : str, request : AddProductToSessionRequest):
    try:
        save_product_to_session(session_id=user_session, product=request.product)
        return {
            "status" : "200"
        }
    except Exception as e:
        return {
            "status" : "500"
        }

@app.post('/{user_session}/set-preferences')
async def set_prefs(user_session : str, request : AddPrefsToSessionRequest):
    try:
        save_prefs_to_session(session_id=user_session, prefs=request.prefs)
        return {
            "status" : "200"
        }
    except Exception as e:
        return {
            "status" : "500"
        }
    
@app.post('/{user_session}/search')
async def start_search(user_session: str):
    session = get_session_by_session_id(user_session)
    await run_using_object(session)
    return {
        "status" : "ok"
    }

@app.get("/data")
async def get_data():
    if not os.path.exists(JSON_FILE_PATH):
        raise HTTPException(status_code=404, detail="Data file not found")
    try:
        with open(JSON_FILE_PATH, "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading data file: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="0.0.0.0", port=8000)