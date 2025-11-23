import random
import uuid
import json
import time
import os
from edwh_uuid7 import uuid7
from faker import Faker
from curl_cffi import Session, CurlHttpVersion
from lib.solver.captchafox import Solver
from lib.console.console import Console, C, Fore
from bs4 import BeautifulSoup



def extract(page: str) -> tuple[str, str]:
    soup = BeautifulSoup(page, "html.parser")
    script = soup.find("script", {"id": "application-config", "type": "application/json"})
    cfg = {}
    try:
        cfg = json.loads(script.string)
    except:
        return None, None
    access_token = cfg.get("accessToken")
    client_credential_guid = cfg.get("clientCredentialGuid")
    return access_token, client_credential_guid
def va() -> str:
    return "".join(random.choice("0123456789abcdef") if c == "x" else c for c in "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
def _cr() -> str:
    return uuid.uuid4().hex
def ko() -> str:
    return _cr()
def bs() -> str:
    return _cr()[16:]
def jh(trace_id: str | None = None, span_id: str | None = None) -> str:
    if trace_id is None:
        trace_id = ko()
    if span_id is None:
        span_id = bs()
    return f"{trace_id}-{span_id}-{random.choice([0, 1])}"
def gen_sentry_trace() -> str:
    return jh()
def random_string(length=10):
    import string
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def login(session: Session, statistics: str, email: str, password: str):
    return session.post(
        "https://login.gmx.com/login",
        data={
            'ibaInfo': 'abd=false',
            'service': 'mailint',
            'statistics': statistics,
            'uasServiceID': 'mc_starter_gmxcom',
            'successURL': 'https://$(clientName)-$(dataCenter).gmx.com/login',
            'loginFailedURL': 'https://www.gmx.com/logout/?ls=wd',
            'loginErrorURL': 'https://www.gmx.com/logout/?ls=te',
            'edition': 'us',
            'lang': 'en',
            'usertype': 'standard',
            'username': email,
            'password': password,
        },
        headers={
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ja',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.gmx.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://www.gmx.com/',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        }
    )

def createAccount():
    st = int(time.time()*1000)
    start = time.time()
    session = Session(
        impersonate="chrome133a",
        ja3="771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,18-13-17613-43-65037-11-0-16-35-51-27-45-23-5-10-65281,4588-29-23-24,0",
        akamai="1:65536;2:0;4:6291456;6:262144|15663105|0|m,a,s,p",
        http_version=CurlHttpVersion.V2_0
    )
    proxy = "set your proxy"
    if proxy == "set your proxy":
        raise Exception("Set your proxy")
    session.proxies.update(
        {
            "https": proxy,
            "http": proxy,
        }
    )

    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
    )
    logger = Console()
    #logger.info("Starting...")
    signup_page = session.get("https://signup.gmx.com/")
    session.cookies.update(signup_page.cookies.get_dict())
    access_token, cc_guid = extract(signup_page.text)
    if access_token == None and cc_guid == None:
        return False
    #statistics = signup_page.text.split('"statistics": "')[1].split('"')[0]
    #logger.info(access_token)
    #logger.info(cc_guid)
    username = random_string(20)
    password = f"A{os.urandom(4).hex()}!"
    birth = Faker().date_of_birth(minimum_age=20)
    request_id = va()
    sentry_trace = gen_sentry_trace()
    session.post(
        "https://register-suggest.gmx.com/rest/email-alias/availability",
        json={
            "emailAddress":"aaaaaaaa.aaaaaaaa@gmx.com",
            "firstName":"AAAAAAAA",
            "lastName":"AAAAAAAA",
            "birthDate":str(birth),
            "city":"",
            "countryCode":"US",
            "initialRequestedEmailAddress":"",
            "suggestionProducts":[
                "gmxcomFree"
            ],
            "maxResultCountToProduct":{
                "gmxcomFree":"4"
            },
            "mdhMaxResultCount":"0",
            "requestedEmailAddressProduct":"gmxcomFree"
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US;q=0.9',
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/vnd.ui.mam.suggestion.creation-v1+json',
            'X-UI-APP': '@mamdev/umreg.registration-app2/8.31.0',
            'X-CCGUID': str(cc_guid),
            'X-REQUEST-ID': str(va()),
            'Origin': 'https://signup.gmx.com',
            'Connection': 'keep-alive',
            'Referer': 'https://signup.gmx.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Priority': 'u=0',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'trailers',
        }
    )
    session.post(
        "https://register-suggest.gmx.com/rest/email-alias/availability",
        json={
            "emailAddress":f"{username}@gmx.com",
            "firstName":"",
            "lastName":"",
            "birthDate":str(birth),
            "city":"",
            "countryCode":"US",
            "initialRequestedEmailAddress":"",
            "suggestionProducts":[
                "gmxcomFree"
            ],
            "maxResultCountToProduct":{
                "gmxcomFree":"4"
            },
            "mdhMaxResultCount":"0",
            "requestedEmailAddressProduct":"gmxcomFree"
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US;q=0.9',
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/vnd.ui.mam.suggestion.creation-v1+json',
            'X-UI-APP': '@mamdev/umreg.registration-app2/8.31.0',
            'X-CCGUID': str(cc_guid),
            'X-REQUEST-ID': str(va()),
            'Origin': 'https://signup.gmx.com',
            'Connection': 'keep-alive',
            'Referer': 'https://signup.gmx.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Priority': 'u=0',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'trailers',
        }
    )
    regist = session.post(
        "https://signup.gmx.com/account/email-registration",
        json={
            "user":{
                "givenName":"AAAAAAAA",
                "familyName":"AAAAAAAA",
                "gender":"MALE",
                "birthDate":str(birth),
                "mobileNumber": f"+810{random.randint(7, 8)}0{random.randint(1111, 9999)}{random.randint(1111, 9999)}",
                "address":{
                    "countryCode":"JP",
                    "region":"",
                    "postalCode":"",
                    "locality":"",
                    "streetAddress":""
                },
                "credentials":{
                    "password":f"{password}"
                }
            },
            "mailAccount":{
                "email":f"{username}@gmx.com"
            },
            "product":"gmxcomFree"
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US;q=0.9',
            'Content-Type': 'application/vnd.ui.mam.account.creation+json',
            'X-UI-APP': '@mamdev/umreg.registration-app2/8.31.0',
            'X-CCGUID': str(cc_guid),
            'X-REQUEST-ID': str(request_id),
            'Template-Name': 'B',
            'Authorization': f'Bearer {access_token}',
            'cf-captcha-response': str(Solver(proxy=proxy).solve()["token"]),
            'sentry-trace': sentry_trace,
            'baggage': f'sentry-environment=live,sentry-release=registration-app2%408.31.0,sentry-public_key=3a5b6ce168339211e7bd2d0dd3d696d3,sentry-trace_id={sentry_trace.split("-")[0]},sentry-transaction=%2F,sentry-sampled=false,sentry-sample_rand={random.random()},sentry-sample_rate=0.1',
            'Origin': 'https://signup.gmx.com',
            'Connection': 'keep-alive',
            'Referer': 'https://signup.gmx.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=0',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'trailers',
        },
        cookies={
            'AB_COOKIE': 'B',
            'utag_main': f'_sn:1$_se:20%3Bexp-session$_ss:0%3Bexp-session$_st:{int(time.time()*1000)}%3Bexp-session$ses_id:{st}%3Bexp-session$_pn:1%3Bexp-session',
            '_originalReferrer': 'no_referrer',
            'ua_id': str(uuid7())
        }
    )
    if regist.status_code == 204:
        logger.info(
            f"{C["pink"]}Created Account{Fore.RESET} "+
            f"| {C["gray"]}{username}@gmx.com{Fore.RESET} "+
            f"| {C["gray"]}{password}{Fore.RESET} "+
            f"| {C["gray"]}{time.time() - start:.2f}s.{Fore.RESET}"
        )
        open('accounts.txt', 'a+').write(f'{username}@gmx.com:{password}\n')
        return True
    else:
        if regist.status_code == 403:
            logger.error(f"{C["red"]}Unknown Error  {Fore.RESET}")
        else:
            logger.error(
                f"{C["red"]}Failed         {Fore.RESET} "+
                f"| {C["gray"]}{regist.status_code}{Fore.RESET} "+
                f"| {C["gray"]}{regist.text}{Fore.RESET} "+
                f"| {C["gray"]}{time.time() - start:.2f}s.{Fore.RESET}"
            )
        return False


if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    os.system("clear")
    def worker():
        while True:
            try:
                createAccount()
            except Exception as exc:
                Console().warning("worker loop caught exception, retrying", error=str(exc[:30]))
                time.sleep(2)
    with ThreadPoolExecutor(max_workers=40) as executor:
        for i in range(30):
            executor.submit(worker)
    
