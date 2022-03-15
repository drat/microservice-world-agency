from fastapi import APIRouter
from pydantic import BaseModel
import base64
from core.facebook import Facebook

api_router = APIRouter()
prefix = '/facebook'
tags = ['Facebook']


class ReqValueChecker(BaseModel):
    cookie: str


@api_router.post('/checker')
def checker_facebook_account(req: ReqValueChecker):
    cookie = base64.b64decode(req.cookie.encode('utf-8')).decode('utf-8')
    fb = Facebook(cookie)
    return fb.check()
