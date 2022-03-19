from fastapi import APIRouter
from pydantic import BaseModel
from core.facebook import facebook

apiRouter = APIRouter()
prefix = '/facebook'
tags = ['Facebook']


class ReqValueChecker(BaseModel):
    cookie: str


@apiRouter.post('/checker')
def facebook_checker(req: ReqValueChecker):
    return facebook.apiCheck(req.cookie)
