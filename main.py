from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import urllib.request
from spleeter.separator import Separator

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FILEPATH = {}

@app.post('/split-audio')
async def split_audio(request: Request, file: UploadFile = File(...)):
    
    if not file:
        return {'success': False, 'message': 'No file uploaded'}, 400
    
    output_dir = './output'
    separator = Separator('spleeter:4stems')
    filepath = os.path.join(output_dir, file.filename)
    with open(filepath, 'wb') as f:
        f.write(await file.read())
    separator.separate_to_file(filepath, output_dir)
    
    
    

    # Get the base URL of the server
    server_url = str(request.base_url)
    global FILEPATH
    FILEPATH = {
                   "vocals":f"{server_url}audio/?filepath={os.path.splitext(file.filename)[0]}/vocals.wav",
                   "bass":f"{server_url}audio/?filepath={os.path.splitext(file.filename)[0]}/bass.wav",
                   "drums":f"{server_url}audio/?filepath={os.path.splitext(file.filename)[0]}/drums.wav",
                   'other':f"{server_url}audio/?filepath={os.path.splitext(file.filename)[0]}/other.wav"
                }
    # Return URLs for each stem file, replacing backslashes with forward slashes
    return {
        'success': True,
        "vocals":f"{server_url}audio?filepath={os.path.splitext(file.filename)[0]}/vocals.wav",
                   "bass":f"{server_url}audio/?filepath={os.path.splitext(file.filename)[0]}/bass.wav",
                   "drums":f"{server_url}audio/?filepath={os.path.splitext(file.filename)[0]}/drums.wav",
                   'other':f"{server_url}audio/?filepath={os.path.splitext(file.filename)[0]}/other.wav"
    }

@app.get('/audio')
async def download_file(filepath: str):
    filename = os.path.basename(filepath)
    file_path = f"./output/{filepath}"
    return FileResponse(path=file_path, media_type="application/octet-stream", filename=filename)

@app.get('/playback-urls')
async def get_playback_urls():
    try:
        global FILEPATH
        data = FILEPATH
        if data is None:
            return {'success': False, 'message': 'No JSON body found in the request'}

        vocalsurl = data['vocals']
        bassurl = data['bass']
        drumsurl = data['drums']
        otherurl = data['other']

        # Return the URLs as a JSON response
        return {
            'success': True,
            'vocalsurl': vocalsurl,
            'bassurl': bassurl,
            'drumsurl': drumsurl,
            'otherurl': otherurl
        }
    except Exception as e:
        print(f"Error getting playback URLs: {e}")
        return {'success': False}

