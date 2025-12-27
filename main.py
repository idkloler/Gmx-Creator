import json
import os
import random
import string
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from curl_cffi import CurlHttpVersion, Session
from edwh_uuid7 import uuid7
from faker import Faker
from lib.console.console import C, Console, Fore
from lib.solver.captchafox import Solver


class GmxRegister:
    def __init__(self, worker_count: int = 20, max_workers: int = 100):
        self.worker_count = worker_count
        self.max_workers = max_workers
        self.logger = Console()

    @staticmethod
    def extract(page: str) -> tuple[str | None, str | None]:
        soup = BeautifulSoup(page, "html.parser")
        script = soup.find("script", {"id": "application-config", "type": "application/json"})
        if script is None:
            return None, None
        try:
            cfg = json.loads(script.string or "")
        except Exception:
            return None, None
        access_token = cfg.get("accessToken")
        client_credential_guid = cfg.get("clientCredentialGuid")
        return access_token, client_credential_guid

    @staticmethod
    def va() -> str:
        return "".join(random.choice("0123456789abcdef") if c == "x" else c for c in "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")

    @staticmethod
    def _cr() -> str:
        return uuid.uuid4().hex

    @classmethod
    def ko(cls) -> str:
        return cls._cr()

    @classmethod
    def bs(cls) -> str:
        return cls._cr()[16:]

    @classmethod
    def jh(cls, trace_id: str | None = None, span_id: str | None = None) -> str:
        if trace_id is None:
            trace_id = cls.ko()
        if span_id is None:
            span_id = cls.bs()
        return f"{trace_id}-{span_id}-{random.choice([0, 1])}"

    @classmethod
    def gen_sentry_trace(cls) -> str:
        return cls.jh()

    @staticmethod
    def random_string(length: int = 10) -> str:
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    @staticmethod
    def gen_phone() -> str:
        return f"0{random.randint(7, 9)}0{random.randint(1111, 9999)}{random.randint(1111,9999)}"

    def create_account(self) -> bool:
        st = int(time.time() * 1000)
        start = time.time()
        session = Session(
            impersonate="chrome133a",
            ja3="771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,18-13-17613-43-65037-11-0-16-35-51-27-45-23-5-10-65281,4588-29-23-24,0",
            akamai="1:65536;2:0;4:6291456;6:262144|15663105|0|m,a,s,p",
            http_version=CurlHttpVersion.V2_0
        )
        proxy = f""
        if proxy == "":
            raise Exception("Set your proxy ")
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
        signup_page = session.get("https://signup.gmx.com/")
        session.cookies.update(signup_page.cookies.get_dict())
        access_token, cc_guid = self.extract(signup_page.text)
        if access_token is None and cc_guid is None:
            return False

        username = self.random_string(20)
        email = f"{username}@gmx.com"
        password = Faker().password()
        birth = Faker().date_of_birth(minimum_age=20)
        request_id = self.va()
        sentry_trace = self.gen_sentry_trace()
        #print(self.gen_phone())
        regist = session.post(
            "https://signup.gmx.com/account/email-registration",
            json={
                "user":{
                    "givenName":''.join(random.choice(string.ascii_letters) for _ in range(8)),
                    "familyName":''.join(random.choice(string.ascii_letters) for _ in range(8)),
                    "gender":"MALE",
                    "birthDate":str(birth),
                    "mobileNumber": f"+81{self.gen_phone()}",
                    "address": {
                        "countryCode": "JP",
                        "region": "",
                        "postalCode": "",
                        "locality": "",
                        "streetAddress": ""
                    },
                    "credentials":{
                        "password":f"{password}"
                    }
                },
                "mailAccount":{
                    "email": email
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
            self.logger.info(
                f"{C['pink']}Created Account{Fore.RESET} " +
                f"| {C['gray']}{email}{Fore.RESET} " +
                f"| {C['gray']}{time.time() - start:.2f}s.{Fore.RESET}"
            )
            with open("accounts.txt", "a+") as f:
                f.write(f"\n{email}:{pass}")
            return True
        else:
            if regist.status_code == 403:
                self.logger.error(f"{C['red']}Unknown Error  {Fore.RESET}")
            else:
                self.logger.error(
                    f"{C['red']}Failed         {Fore.RESET} " +
                    f"| {C['gray']}{regist.status_code}{Fore.RESET} " +
                    f"| {C['gray']}{regist.text}{Fore.RESET} " +
                    f"| {C['gray']}{time.time() - start:.2f}s.{Fore.RESET}"
                )
            return False

    def worker(self):
        while True:
            try:
                self.create_account()
            except Exception as exc:
                err_msg = str(exc)
                import traceback
                traceback.print_exc()
                self.logger.error(f"worker loop caught exception, retrying: {err_msg[:50]}")
                time.sleep(2)

    def run(self):
        os.system("clear")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for _ in range(self.worker_count):
                executor.submit(self.worker)


if __name__ == "__main__":
    GmxRegister().run()
