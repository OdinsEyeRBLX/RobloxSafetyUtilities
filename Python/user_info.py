import requests
import json

# Discord webhook URL (replace with your actual webhook URL)
WEBHOOK_URL = "https://discord.com/api/webhooks/"

def get_user_id(username):
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {
        "usernames": [username],
        "excludeBannedUsers": False  #false allows to view banned users
    }
    response = requests.post(url, json=payload)
    data = response.json()
    
    if data["data"]:
        return data["data"][0]["id"]
    else:
        return None

def get_user_info(user_id):
    
    user_info_url = f"https://users.roblox.com/v1/users/{user_id}"
    user_info_response = requests.get(user_info_url)
    user_info = user_info_response.json()

    # check if the account is banned
    if user_info.get("isBanned"):
        terminated = True
    else:
        terminated = False

    
    creation_date = user_info.get("created", "Unknown")

    
    avatar_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=720x720&format=Png&isCircular=false"
    avatar_response = requests.get(avatar_url)
    avatar_data = avatar_response.json()
    
    thumbnail_url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=150x150&format=Png&isCircular=true"
    thumbnail_response = requests.get(thumbnail_url)
    thumbnail_data = thumbnail_response.json()

    return {
        "username": user_info.get("name"),
        "nickname": user_info.get("displayName"),
        "description": user_info.get("description", "No description available."),
        "creation_date": creation_date,
        "avatar_image": avatar_data["data"][0]["imageUrl"],
        "thumbnail_image": thumbnail_data["data"][0]["imageUrl"],
        "profile_link": f"https://www.roblox.com/users/{user_id}/profile",
        "is_terminated": terminated
    }

def send_discord_webhook(user_data):

    #Warning if the user is terminated
    alert_message = "⚠️ **Alert! User is terminated!** ⚠️" if user_data["is_terminated"] else ""

    embed = {
        "title": f"Roblox Profile Information: {user_data['username']}",
        "color": 0000000,  #embed color, you can customize this!
        "fields": [
            {"name": "Username", "value": user_data['username'], "inline": True},
            {"name": "Nickname", "value": user_data['nickname'], "inline": True},
            {"name": "About Me", "value": user_data['description'], "inline": False},
            {"name": "Creation Date", "value": user_data['creation_date'], "inline": False},
            {"name": "Profile Link", "value": f"[Click Here]({user_data['profile_link']})", "inline": False}
        ],
        "thumbnail": {"url": user_data['thumbnail_image']},
        "image": {"url": user_data['avatar_image']}
    }

    if alert_message:
        embed["description"] = alert_message

    payload = {
        "embeds": [embed]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)

    if response.status_code == 204:
        print("Information sent successfully!")
    else:
        print("Failed to send information:", response.status_code, response.text)

#ask for input
input_value = input("Enter Roblox Username or User ID: ")

#don't mess with this
try:
    user_id = int(input_value)
except ValueError:
    user_id = get_user_id(input_value)
    if user_id is None:
        print("Invalid username. User not found.")
        exit()


user_data = get_user_info(user_id)

# Send the information through the Discord webhook
send_discord_webhook(user_data)
