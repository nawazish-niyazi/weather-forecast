import requests
import config

def test_key():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Delhi&appid={config.API_KEY}"
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_key()
