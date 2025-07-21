import requests
import threading
import string
import time
import random
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://10.0.0.1/"
headers = {
    "User-Agent": "Mozilla/5.0"
}
print("Sending benign GET request...")
def benign_get():
    while True:
        try:
            response = requests.get(url, headers=headers, verify=False)
            print(f"Response Code: {response.status_code}")
            
        except Exception as e:
            print(f"Error: {e}")
        delay = random.uniform(0.1, 1)
        print(f"Tunggu selama {delay:.2f} detik...")
        time.sleep(delay)

for _ in range(2):
    threading.Thread(target=benign_get, daemon=True).start()

while True:
    time.sleep(10)
