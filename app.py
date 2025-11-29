import asyncio
import datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

pending_requests = {}     # request_id → Future
received_requests = []    # журнал
request_counter = 0
lock = asyncio.Lock()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/requests")
async def api_requests():
    return JSONResponse(received_requests)

@app.post("/reply")
async def reply(request_id: int = Form(...), code: int = Form(...), body: str = Form(...)):
    if request_id in pending_requests:
        pending_requests[request_id].set_result((code, body))
        return {"status": "ok"}
    return {"status": "notfound"}

@app.post("/clear")
async def clear():
    received_requests.clear()
    return {"status": "ok"}

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request):
    global request_counter
    body = await request.body()
    body_text = body.decode("utf-8", errors="ignore")

    async with lock:
        request_counter += 1
        req_id = request_counter-1

    loop = asyncio.get_event_loop()
    future = loop.create_future()
    pending_requests[req_id] = future

    if request.url.path != "/favicon.ico":
        received_requests.append({
            "id": req_id,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method": request.method,
            "path": request.url.path,
            "body": body_text
        })

    code, response_body = await future
    del pending_requests[req_id]
    return PlainTextResponse(response_body, status_code=code)
