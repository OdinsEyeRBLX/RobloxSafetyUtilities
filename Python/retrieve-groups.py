import requests
import time
import json

def get_user_id(username):
    """Retrieves the user ID based on the username."""
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {
        "usernames": [username],
        "excludeBannedUsers": False
    }
    response = requests.post(url, json=payload)
    data = response.json()
    
    if data["data"]:
        return data["data"][0]["id"]
    else:
        return None

def get_groups(user_id):
    """Retrieves the groups the user is a member of."""
    url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
    response = requests.get(url)
    groups_data = response.json()
    return [{"id": group["group"]["id"], "name": group["group"]["name"]} for group in groups_data.get("data", [])]

input_value = input("Enter Roblox Username or User ID: ")


try:
    user_id = int(input_value)
except ValueError:
    user_id = get_user_id(input_value)
    if user_id is None:
        print("Invalid username. User not found.")
        exit()


groups = get_groups(user_id)

if groups:
    for group in groups:
        link = f"https://www.roblox.com/groups/{group['id']}"
        message = f"`{input_value}` is a member of the group: {group['name']}\nLink: {link}\nID: `{group['id']}`"
        print(message)
        time.sleep(1)
else:
    print("The user is not a member of any groups.")
