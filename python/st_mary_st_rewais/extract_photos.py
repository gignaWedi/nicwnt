from getpass import getpass

import requests
import json
from bs4 import BeautifulSoup

session = requests.Session()

session.headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}

url = "https://www.madisoncopticchurch.com/wp-admin/admin.php?page=wpeg-add-images"

payload = {
    "log": "admin",
    "pwd": getpass(),
    "wp-submit": "Log In",
    "redirect_to": url,
    "testcookie": "1",
}

res = session.get('https://www.madisoncopticchurch.com/wp-login.php')
cookies = dict(res.cookies)

response = session.post("https://www.madisoncopticchurch.com/wp-login.php", data=payload, cookies=cookies)

if response.url != 'https://www.madisoncopticchurch.com/wp-admin/admin.php?page=wpeg-add-images':
    print("Failed to load the page. Try logging in again.")
    exit(1)

bigsoup = BeautifulSoup(response.text, 'html.parser')

galleries = bigsoup.find(id="galleryResults")

picture_results = {}

for form in galleries.find_all('form'): 
    # Extract form details
    form_action = form.get('action', '')
    form_method = form.get('method', 'get').lower() # Default to 'get' if not specified
    
    # Construct the full URL if form_action is a relative path
    if not form_action.startswith('http'):
        submit_url = requests.compat.urljoin(url, form_action)
    else:
        submit_url = form_action

    # Extract all input fields (including hidden ones)
    form_data = {}
    for input_tag in form.find_all(['input', 'select', 'textarea']):
        name = input_tag.get('name')
        value = input_tag.get('value', '')
        # Add logic for checkboxes/radio buttons if needed (only checked ones are submitted)
        if name:
            form_data[name] = value


    # Use 'requests.post' or 'requests.get' based on the form method
    if form_method == 'post':
        submit_response = session.post(submit_url, data=form_data)
    elif form_method == 'get':
        submit_response = session.get(submit_url, params=form_data)
    else:
        print(f"Unsupported form method: {form_method}")
        submit_response = None

    if submit_response:
        gallery = form_data["galleryName"]
        print(f"===================================== {gallery} =====================================")
        print(f"Submission status code: {submit_response.status_code}")

        sub_dict = {}
        sub_dict |= {k: v for k, v in form_data.items() if k in {"galleryId", "galleryName"}}        

        soup = BeautifulSoup(submit_response.text, 'html.parser')
        try:
            table = soup.find(id="imageResults")
            tbody = table.find("tbody")

            photos_hash = {}

            for row in tbody.find_all("tr"):
                try:
                    input_tag = row.find("input", attrs={"name": "edit_imageSort[]"})
                    key = int(input_tag['value'])
                    
                    path = row.find("input", attrs={"name": "edit_imagePath[]"})['value']
                    
                    image_name = path.removeprefix("https://madisoncopticchurch.com/wp-content/uploads/")
                    photos_hash[key] = photos_hash.get(key,[]) + [image_name]
                except:
                    print("!!! A row failed !!!")
            
            sub_dict["photos"] = []
            for k in sorted(photos_hash):
                sub_dict["photos"].extend(photos_hash[k])
            
            picture_results[form_data["galleryName"]] = sub_dict
            
            print("Complete!")
            print(json.dumps(sub_dict, indent=2))
        except Exception as exc:
            print(f"Failed: {exc}")

        

with open("gallery.json", "w") as file:
    json.dump(picture_results, file, indent=2)