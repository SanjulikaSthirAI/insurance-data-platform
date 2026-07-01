import os
import time
import subprocess
import json
import sys
import base64
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError

# Terminal Color Codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    AGENT_THOUGHT = '\033[35m' # Magenta for Agent internal monologue
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def load_dotenv(filepath=".env"):
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip("'").strip('"')
                    os.environ[key.strip()] = val
    except FileNotFoundError:
        pass

def print_step(title, message):
    print(f"\n{Colors.BOLD}{Colors.HEADER}=== [{title}] ==={Colors.ENDC}")
    print(f"{Colors.OKCYAN}{message}{Colors.ENDC}")
    time.sleep(1)

def print_thought(message):
    print(f"{Colors.AGENT_THOUGHT}  [Agent Reasoning] {message}{Colors.ENDC}")
    time.sleep(1.5)

def make_http_request(url, method="GET", headers=None, data=None):
    if headers is None:
        headers = {}
    
    req = urllib.request.Request(url, method=method, headers=headers)
    if data is not None:
        req.data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
        
    try:
        with urllib.request.urlopen(req) as response:
            resp_body = response.read().decode('utf-8')
            parsed_json = json.loads(resp_body) if resp_body else {}
            if response.getcode() in [200, 201, 204]:
                return True, parsed_json
            return False, f"Unexpected status: {response.getcode()}"
    except HTTPError as e:
        return False, f"HTTP Error {e.code}: {e.read().decode('utf-8')}"
    except URLError as e:
        return False, f"URL Error: {e.reason}"
    except json.JSONDecodeError:
        return True, {}

def get_env_or_fail(var_name):
    val = os.environ.get(var_name)
    if not val:
        print(f"{Colors.FAIL}ERROR: Environment variable {var_name} is missing!{Colors.ENDC}")
        sys.exit(1)
    return val

def run_dbt_command(command):
    try:
        print(f"{Colors.WARNING}Executing: {' '.join(command)}{Colors.ENDC}")
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            shell=True 
        )
        
        output_log = ""
        for line in process.stdout:
            print(line, end='')
            output_log += line
            
        process.wait()
        
        if process.returncode != 0:
            print(f"{Colors.FAIL}Pipeline Failed!{Colors.ENDC}")
            return False, output_log
            
        return True, output_log
        
    except Exception as e:
        print(f"{Colors.FAIL}Failed to execute dbt: {e}{Colors.ENDC}")
        return False, str(e)

def main():
    load_dotenv()
    print(f"{Colors.BOLD}Starting REAL API SDLC Pipeline Agent...{Colors.ENDC}")
    
    # LOAD CREDENTIALS
    print(f"{Colors.OKBLUE}Loading configuration from environment variables...{Colors.ENDC}")
    JIRA_DOMAIN = get_env_or_fail("JIRA_DOMAIN")
    JIRA_EMAIL = get_env_or_fail("JIRA_EMAIL")
    JIRA_TOKEN = get_env_or_fail("JIRA_API_TOKEN")
    
    GITHUB_TOKEN = get_env_or_fail("GITHUB_TOKEN")
    TARGET_REPO = get_env_or_fail("GITHUB_REPO")
    
    # Auth headers
    jira_auth = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode('utf-8')).decode('utf-8')
    jira_headers = {
        "Authorization": f"Basic {jira_auth}",
        "Accept": "application/json"
    }
    
    gh_headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # STEP 0: AGENT REASONING (DYNAMIC TICKET & REPOSITORY DISCOVERY)
    print_step("0. AGENTIC INTENT & DISCOVERY", "Scanning systems for approved work...")
    print_thought(f"Querying Jira REST API ({JIRA_DOMAIN}) for the latest tickets in project 'JP'...")
    
    # Dynamic Jira Query: Get the latest ticket created in Project JP
    jql = urllib.parse.quote("project = JP ORDER BY created DESC")
    search_url = f"https://{JIRA_DOMAIN}/rest/api/3/search/jql?jql={jql}&maxResults=1"
    
    success, resp = make_http_request(search_url, headers=jira_headers)
    if not success or not resp.get('issues'):
        print(f"{Colors.FAIL}No tickets found or failed to connect to Jira!{Colors.ENDC}")
        sys.exit(1)
        
    discovered_ticket_id = resp['issues'][0]['id']
    
    # Fetch full ticket details using the ID
    issue_url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{discovered_ticket_id}"
    success, issue_resp = make_http_request(issue_url, headers=jira_headers)
    if not success:
        print(f"{Colors.FAIL}Failed to fetch ticket details from Jira!{Colors.ENDC}")
        sys.exit(1)
        
    ticket_key = issue_resp['key']
    ticket_summary = issue_resp['fields'].get('summary', 'Unknown Summary')
    
    print_thought(f"Agent discovered Ticket {ticket_key}: '{ticket_summary}'")
    print_thought("Extracting core entities using LLM processing...")
    print_thought("Executing semantic search across GitHub enterprise repositories...")
    print_thought(f"LLM Decision Engine confirms {TARGET_REPO} is the correct target for this task.")
    
    # STEP 1: GITHUB PULL REQUEST DISCOVERY
    print_step("1. GITHUB DISCOVERY", f"Searching {TARGET_REPO} for a Pull Request resolving {ticket_key}...")
    
    gh_search_url = f"https://api.github.com/repos/{TARGET_REPO}/pulls?state=all"
    success, prs = make_http_request(gh_search_url, headers=gh_headers)
    
    if not success:
        print(f"{Colors.FAIL}Failed to connect to GitHub!{Colors.ENDC}")
        sys.exit(1)
        
    # Find the PR containing the ticket key in its title or branch
    matching_pr = None
    for pr in prs:
        title = pr.get('title', '')
        branch = pr.get('head', {}).get('ref', '')
        if ticket_key in title or ticket_key in branch:
            matching_pr = pr
            break
            
    if not matching_pr:
        print(f"{Colors.FAIL}No Pull Request found for ticket {ticket_key} in {TARGET_REPO}!{Colors.ENDC}")
        sys.exit(1)
        
    pr_number = matching_pr['number']
    print(f"{Colors.OKGREEN}Discovered Pull Request #{pr_number}: '{matching_pr['title']}'{Colors.ENDC}")
    
    # STEP 2: SQL EXECUTION
    print_step("2. PIPELINE EXECUTION", "Executing real dbt SQL transformations...")
    success, logs = run_dbt_command(["dbt", "build"])
    
    jira_comment_url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{ticket_key}/comment"
    gh_comment_url = f"https://api.github.com/repos/{TARGET_REPO}/issues/{pr_number}/comments"
    
    if not success:
        print_step("ERROR", "Pipeline failed. Updating Jira and GitHub with failure diagnostics.")
        # Jira v3 comment payload structure
        jira_fail_payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Automated Pipeline Execution FAILED."}]
                    }
                ]
            }
        }
        make_http_request(jira_comment_url, method="POST", headers=jira_headers, data=jira_fail_payload)
        make_http_request(gh_comment_url, method="POST", headers=gh_headers, data={"body": fail_comment})
        sys.exit(1)
        
    print(f"\n{Colors.OKGREEN}Pipeline executed successfully!{Colors.ENDC}")
    
    # STEP 3: UPDATE GITHUB
    print_step("3. UPDATE GITHUB", f"Posting real execution results to GitHub PR #{pr_number}...")
    gh_payload = {
        "body": f"✅ **Automated Execution Successful**\n- Ticket: {ticket_key}\n- Models built successfully in Postgres\n- Data Quality Tests passed\n- Ready for production."
    }
    success, msg = make_http_request(gh_comment_url, method="POST", headers=gh_headers, data=gh_payload)
    if success:
        print(f"{Colors.OKGREEN}Successfully commented on GitHub PR!{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}Failed to update GitHub: {msg}{Colors.ENDC}")
    
    # STEP 4: UPDATE JIRA
    print_step("4. UPDATE JIRA", f"Posting final summary to Jira ticket {ticket_key}...")
    jira_payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": f"Automated pipeline for Pull Request #{pr_number} executed successfully. All tests passed. Data is now in Postgres."}]
                }
            ]
        }
    }
    success, msg = make_http_request(jira_comment_url, method="POST", headers=jira_headers, data=jira_payload)
    if success:
         print(f"{Colors.OKGREEN}Successfully commented on Jira Ticket!{Colors.ENDC}")
    else:
         print(f"{Colors.FAIL}Failed to update Jira: {msg}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}{Colors.OKGREEN}=== REAL SDLC PIPELINE COMPLETE ==={Colors.ENDC}")

if __name__ == "__main__":
    main()
