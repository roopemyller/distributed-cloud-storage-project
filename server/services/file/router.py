# services/file/router.py
from fastapi import APIRouter

router = APIRouter()

@router.post('/upload')
async def upload(file):
    return {'message': f'Uploading a file: {file}'}

@router.post('/download')
async def download(file_path):
    return {'message': f'Downloading a file from {file_path}'}

@router.post('/delete')
async def download(file_path):
    return {'message': f'Deleted a file from {file_path}'}