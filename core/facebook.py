from fastapi import HTTPException
from urllib.parse import unquote
import json
import random
import re
import requests


class Facebook:
    def __init__(self, cookie: str) -> None:
        self.DEFAULT_USERAGENT_DESKTOP = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15'
        self.DEFAULT_USERAGENT_MOBILE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Snapchat/10.77.5.59 (like Safari/604.1)'
        self.FACEBOOK_BASE_CORE = 'https://graph.facebook.com'
        self.FACEBOOK_BASE_API = 'https://graph.facebook.com/v13.0'
        self.FACEBOOK_BASE_MBASIC = 'https://mbasic.facebook.com'
        self.FACEBOOK_BASE_M = 'https://m.facebook.com'
        self.FACEBOOK_BASE_WWW = 'https://www.facebook.com'
        self.FACEBOOK_BASE_BM = 'https://business.facebook.com'

        self.api = requests.session()

        self.cookie = cookie

    def onCheck(self):
        try:
            self.apiSetCookie()
            self.apiSetProxy()
            EAAI = self.apiGetTokenEAAI()
            if EAAI is None:
                raise HTTPException(status_code=404)

            EAAG = self.apiGetTokenEAAG()
            if EAAG is None:
                raise HTTPException(status_code=404)

            return {
                'EAAI': EAAI,
                'EAAG': EAAG,
                'sessions': self.apiGetSessions(),
                'me': self.apiGetMe(EAAG),
                'adaccounts': self.apiGetAdaccountsMapping(EAAI, self.apiGetUID()),
                'businesses': self.apiGetBusinesses(EAAG),
                'pages': self.apiGetFacebookPages(EAAI)
            }
        except requests.exceptions.ConnectionError:
            return self.onCheck()
        except:
            raise HTTPException(status_code=404)

    def apiChunks(self, lst, n):
        return [lst[i:i + n] for i in range(0, len(lst), n)]

    def apiConvertStringToDic(self):
        return {e.get('name'): e.get('value') for e in json.loads(self.cookie.strip())}

    def apiGetUID(self):
        return self.apiConvertStringToDic().get('c_user')

    def apiGetHeadersDesktop(self):
        return {'User-Agent': self.DEFAULT_USERAGENT_DESKTOP}

    def apiGetHeadersMobile(self):
        return {'User-Agent': self.DEFAULT_USERAGENT_MOBILE}

    def apiSetCookie(self):
        self.api.cookies.update(self.apiConvertStringToDic())

    def apiSetProxy(self):
        session_id = random.random()
        self.api.proxies.update({
            'http': f'http://lum-customer-hl_ab3d1e44-zone-checker-session-{session_id}:4sinqp2g8704@zproxy.lum-superproxy.io:22225',
            'https': f'http://lum-customer-hl_ab3d1e44-zone-checker-session-{session_id}:4sinqp2g8704@zproxy.lum-superproxy.io:22225'
        })

    def apiGetTokenEAAI(self):
        try:
            res = self.api.get(
                f'{self.FACEBOOK_BASE_WWW}/ads/manager/account_settings/account_billing',
                headers=self.apiGetHeadersDesktop()
            ).text
            regx = re.findall(r'access_token:"(.*?)"', res)
            return regx[0] if len(regx) > 0 else None
        except:
            return None

    def apiGetTokenEAAB(self, act: str):
        try:
            res = self.api.get(
                f'{self.FACEBOOK_BASE_WWW}/adsmanager/manage/campaigns?act={act}',
                headers=self.apiGetHeadersDesktop()
            ).text
            regx = re.findall(r'__accessToken="(.*?)', res)
            return regx[0] if len(regx) > 0 else None
        except:
            return None

    def apiGetTokenEAAG(self):
        try:
            res = self.api.get(
                f'{self.FACEBOOK_BASE_BM}/content_management',
                headers=self.apiGetHeadersDesktop()
            ).text
            regx = re.findall(r'accessToken":"(EAAG.*?)"', res)
            return regx[0] if len(regx) > 0 else None
        except:
            return None

    def apiGetSessions(self):
        try:
            res = self.api.get(
                f'{self.FACEBOOK_BASE_M}/settings/security_login/sessions',
                headers=self.apiGetHeadersMobile()
            ).text
            IP = re.findall(r'__html:"IP: (.*?)"', res)
            return list(dict.fromkeys(IP))
        except:
            return []

    def apiGetMe(self, access_token: str):
        try:
            res = self.api.get(
                f'{self.FACEBOOK_BASE_API}/me?fields=id,name,birthday,gender,friends.limit(0),picture.type(large)&access_token={access_token}',
                headers=self.apiGetHeadersDesktop()
            ).json()
            return res
        except:
            return {}

    def apiGetAdaccounts(self, access_token: str, adaccounts=[], next=None):
        try:
            if next is None:
                default_url = f'{self.FACEBOOK_BASE_API}/me?fields=adaccounts.limit(2500){{account_id,id,name,account_status,currency,balance,amount_spent,adtrust_dsl,adspaymentcycle,owner,users,business,timezone_name,timezone_offset_hours_utc,is_notifications_enabled,disable_reason,ads_volume}}&access_token={access_token}'
                res = self.api.get(
                    default_url,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'adaccounts' in res:
                    if len(res.get('adaccounts').get('data')) >= 2500:
                        if 'next' in res.get('adaccounts').get('paging'):
                            return self.apiGetAdaccounts(
                                access_token,
                                adaccounts + res.get('adaccounts').get('data'),
                                res.get('adaccounts').get('paging').get('next')
                            )
                    return res.get('adaccounts').get('data')
                return adaccounts
            else:
                next = unquote(next)
                res = self.api.get(
                    next,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'next' in res.get('paging'):
                    return self.apiGetAdaccounts(
                        access_token,
                        adaccounts + res.get('data')
                    )
                return adaccounts + res.get('data')
        except:
            return adaccounts

    def apiGetAdaccountsMapping(self, access_token: str, uid: str):
        adaccounts_fixed = []

        adaccounts = self.apiGetAdaccounts(access_token)
        try:
            adaccounts_has_permission = []
            for adaccount in adaccounts:
                me = None
                for e in adaccount.get('users').get('data'):
                    if e.get('id') == uid:
                        me = e
                        break
                if me.get('role') in [1001, 1002]:
                    adaccounts_has_permission.append(adaccount)

            adaccounts_has_permission_chunks = self.apiChunks(
                adaccounts_has_permission,
                100
            )
            adaccounts_values = {}
            for adaccounts_chunks in adaccounts_has_permission_chunks:
                ids = ','.join(
                    list(map(lambda e: e.get('id'), adaccounts_chunks)))
                res = self.api.get(
                    f'{self.FACEBOOK_BASE_API}?ids={ids}&fields=all_payment_methods{{pm_credit_card{{credit_card_address,credit_card_type,display_string,exp_month,exp_year,is_verified,time_created}},payment_method_paypal{{email_address,time_created}},payment_method_stored_balances{{balance,total_fundings,time_created}}}}&access_token={access_token}',
                    headers=self.apiGetHeadersDesktop()
                ).json()
                adaccounts_values = {**adaccounts_values, **res}

            for adaccount in adaccounts:
                adaccounts_fixed.append(
                    {**adaccount, **adaccounts_values.get(adaccount.get('id'))}
                )
            return adaccounts_fixed
        except:
            return adaccounts

    def apiGetBusinesses(self, access_token: str, businesses=[], next=None):
        try:
            if next is None:
                default_url = f'{self.FACEBOOK_BASE_API}/me?fields=businesses.limit(2500){{id,name,owned_ad_accounts.limit(2500){{id,account_id,name}},business_users.limit(2500){{id,name,role,email,pending_email}},created_time,owned_pixels{{id,name}}}}&access_token={access_token}'
                res = self.api.get(
                    default_url,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'businesses' in res:
                    if len(res.get('businesses').get('data')) >= 2500:
                        if 'next' in res.get('businesses').get('paging'):
                            return self.apiGetBusinesses(
                                access_token,
                                businesses + res.get('businesses').get('data'),
                                res.get('businesses').get('paging').get('next')
                            )
                    return res.get('businesses').get('data')
                return businesses
            else:
                next = unquote(next)
                res = self.api.get(
                    next,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'next' in res.get('paging'):
                    return self.apiGetBusinesses(
                        access_token,
                        businesses + res.get('data')
                    )
                return businesses + res.get('data')
        except:
            return businesses

    def apiGetFacebookPages(self, access_token: str, facebook_pages=[], next=None):
        try:
            if next is None:
                default_url = f'{self.FACEBOOK_BASE_API}/me?fields=facebook_pages.limit(2500){{id,name,page_created_time,followers_count,fan_count,owner_business,roles}}&access_token={access_token}'
                res = self.api.get(
                    default_url,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'facebook_pages' in res:
                    if len(res.get('facebook_pages').get('data')) >= 2500:
                        if 'next' in res.get('facebook_pages').get('paging'):
                            return self.apiGetFacebookPages(
                                access_token,
                                facebook_pages +
                                res.get('facebook_pages').get('data'),
                                res.get('facebook_pages').get(
                                    'paging').get('next')
                            )
                    return res.get('facebook_pages').get('data')
                return facebook_pages
            else:
                next = unquote(next)
                res = self.api.get(
                    next,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'next' in res.get('paging'):
                    return self.apiGetFacebookPages(
                        access_token,
                        facebook_pages + res.get('data')
                    )
                return facebook_pages + res.get('data')
        except:
            return facebook_pages
