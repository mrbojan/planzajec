from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import shutil, zipfile, os
from plan_zajec.serwer import getResponseFor
from fastapi.responses import FileResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"files/{file.filename}"
    
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    getResponseFor("/plan_zajec.zip", file_location)

    with zipfile.ZipFile("static/plan_zajec.zip", 'r') as zip_ref:
        zip_ref.extractall("static")
    
    with open('last_file.txt', 'w') as f:
        f.write(file_location)

@app.get("/plantxt/")
async def main():
    with open('last_file.txt', 'r') as f:
        last_file = f.read()
    return FileResponse(last_file, media_type='application/octet-stream', filename=last_file.split('/')[-1])