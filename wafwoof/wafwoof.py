import requests
from flask import Flask, request, render_template

app = Flask(__name__)


CLOUDFLARE_API_TOKEN = "your_cloudflare_api_token"
CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4/"

def get_firewall_details(zone_id):
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    firewall_rules_url = f"{CLOUDFLARE_API_URL}zones/{zone_id}/firewall/rules"
    response = requests.get(firewall_rules_url, headers=headers)

    if response.status_code == 200:
        rules = response.json().get('result', [])
        firewall_details = [{"rule": rule.get("description", "No description"), 
                             "expiry_date": rule.get("paused")} 
                            for rule in rules]
        return firewall_details
    else:
        return None

def get_zone_id(domain):
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    zones_url = f"{CLOUDFLARE_API_URL}zones?name={domain}"
    response = requests.get(zones_url, headers=headers)

    if response.status_code == 200:
        zones = response.json().get('result', [])
        if zones:
            return zones[0]['id']
        else:
            return None
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    firewall_details = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            domain = url.split('/')[2]  # Extract domain from URL
            zone_id = get_zone_id(domain)
            if zone_id:
                firewall_details = get_firewall_details(zone_id)
            else:
                firewall_details = "Zone ID not found for the provided domain."
        else:
            firewall_details = "No URL provided. Please enter a valid URL."

    return render_template('index.html', firewall_details=firewall_details)

if __name__ == '__main__':
    app.run(debug=True)
