from fastapi import APIRouter, Form, Request, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from . import controller
from pydantic import BaseModel
from typing import List
import json
from utils.auth import get_current_user
from . import streamingController
from db.database import get_db
from sqlalchemy.orm import Session

from utils.workflow_config import get_workflow_id, get_workflow_name


router = APIRouter(tags=["coze"])

streaming_headers = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
}
