from fastapi import APIRouter, Form, Request, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from . import controller
from pydantic import BaseModel
from typing import List
import json
from utils.auth import get_current_user
from utils.exceptions import (
    ValidationException, AuthenticationException, NotFoundException,
    ConflictException, DatabaseException, ExternalServiceException
)
from . import streamingController
from db.database import get_db
from sqlalchemy.orm import Session
import logging

from utils.workflow_config import get_workflow_id_by_function, get_workflow_name, get_workflow_info

logger = logging.getLogger(__name__)


router = APIRouter(tags=["coze"])

streaming_headers = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
}
