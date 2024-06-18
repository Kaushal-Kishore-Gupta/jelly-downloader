from fastapi import FastAPI, BackgroundTasks, HTTPException,status
from pydantic import BaseModel
from celery.result import AsyncResult
from tasks import download_file
import os
import logging
from contextlib import asynccontextmanager
from celery_config import celery_app

app = FastAPI()

@asynccontextmanager
async def lifespan(aap: FastAPI):
    # set up required things at the startup of the application
    # initiale_logger() # TODO: improve logging
    yield
    # cleanup/ do the end of life cycle things here...


class DownloadRequest(BaseModel):
    url: str
    filename: str
    filetype: str
    directory: str

@app.post("/download/")
async def download_file_endpoint(request: DownloadRequest, background_tasks: BackgroundTasks):
    try:
        task = download_file.delay(url=request.url, filename=request.filename, filetype=request.filetype, directory=request.directory)
        return {
            "status": "success",
            "task_id": task.id
        }
    except Exception as e:
        logging.error(f"Error submitting download task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit download task")


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    try:
        task = AsyncResult(task_id)
        if task.state == "SUCCESS":
            return {"state": task.state, "result": task.result}
        elif task.state == "PROGRESS":
            progress = task.info.get('progress', 0)
            return {"state": task.state, "progress": progress}
        else:
            return {"state": task.state, "info": str(task.info)}
    except Exception as e:
        logging.error(f"Error retrieving task status: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve task status")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
