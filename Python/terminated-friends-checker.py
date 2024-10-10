import requests
import time

def get_user_id(username):
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

def get_friends(user_id):
    url = f"https://friends.roblox.com/v1/users/{user_id}/friends"
    response = requests.get(url)
    friends_data = response.json()
    return [{"id": friend["id"], "name": friend["name"]} for friend in friends_data.get("data", [])]

def is_user_terminated(user_id):
    url = f"https://users.roblox.com/v1/users/{user_id}"
    response = requests.get(url)
    user_data = response.json()
    return user_data.get("isBanned", False), user_data.get("name", "Unknown")

def print_terminated_friends(username_or_id):
    try:
        user_id = int(username_or_id)
    except ValueError:
        user_id = get_user_id(username_or_id)
        if user_id is None:
            print("Invalid username. User not found.")
            return
    
    # Retrieve friends list
    friends = get_friends(user_id)
    if not friends:
        print("The user has no friends or the friends list is private.")
        return

    print("Checking friends for termination status...")
    for friend in friends:
        time.sleep(0.5)
        is_terminated, username = is_user_terminated(friend["id"])
        if is_terminated:
            print("✔️ Terminated friend found: {username} - Link: https://www.roblox.com/users/{friend['id']}/profile")

username_or_id = input("Enter Roblox Username or User ID: ")
print("⏳ Checking...")
print_terminated_friends(username_or_id)
