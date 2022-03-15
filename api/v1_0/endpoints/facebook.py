from fastapi import APIRouter
from pydantic import BaseModel
from core.facebook import Facebook

api_router = APIRouter()
prefix = '/facebook'
tags = ['Facebook']


class ReqValueChecker(BaseModel):
    cookie: str


@api_router.post('/checker')
def checker_facebook_account(req: ReqValueChecker):
    fb = Facebook(req.cookie)
    return fb.check()
