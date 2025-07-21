import requests
import time
import random
import urllib3
import threading
import string
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://10.0.0.1/" 
headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
}
def generate_user_input():
    length = random.randint(5, 30)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

print("Sending benign POST request...")
def benign_post():
    while True:
        try:
            username = generate_user_input()
            data = {"user": username}
            response = requests.post(url, headers=headers, data=data, verify=False)
            print(f"Response Code: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        delay = random.uniform(0.1, 1)
        print(f"Tunggu selama {delay:.2f} detik...")
        time.sleep(delay)

for _ in range(2):
    threading.Thread(target=benign_post, daemon=True).start()

while True:
    time.sleep(10)
