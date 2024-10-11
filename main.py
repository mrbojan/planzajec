from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import shutil, zipfile, os
from plan_zajec.serwer import getResponseFor

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    return {"message": "Przejdź do /static/index.html, aby zobaczyć stronę"}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"files/{file.filename}"
    
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    print(file_location)
    getResponseFor("/plan_zajec.zip", file_location)

    with zipfile.ZipFile("static/plan_zajec.zip", 'r') as zip_ref:
        zip_ref.extractall("static")
