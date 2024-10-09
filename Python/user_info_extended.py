import requests
import json

# Discord webhook URL (replace with your actual webhook URL)
WEBHOOK_URL = "http://DISCORD-WEBHOOK-URL"

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

def get_followers(user_id):
    
    url = f"https://friends.roblox.com/v1/users/{user_id}/followers"
    response = requests.get(url)
    followers_data = response.json()
    return [{"id": follower["id"], "name": follower["name"]} for follower in followers_data.get("data", [])]

def get_following(user_id):
    
    url = f"https://friends.roblox.com/v1/users/{user_id}/followings"
    response = requests.get(url)
    following_data = response.json()
    return [{"id": user["id"], "name": user["name"]} for user in following_data.get("data", [])]

def get_terminated_count(user_ids):
    
    terminated_count = 0
    terminated_names = []
    for user_id in user_ids:
        url = f"https://users.roblox.com/v1/users/{user_id}"
        response = requests.get(url)
        user_data = response.json()
        if user_data.get("isBanned"):
            terminated_count += 1
            terminated_names.append(user_data.get("name"))
    return terminated_count, terminated_names

def get_game_links(user_id):
    
    url = f"https://games.roblox.com/v2/users/{user_id}/games?accessFilter=All&sortOrder=Asc&limit=10"
    response = requests.get(url)
    games_data = response.json()
    games = games_data.get("data", [])
    return [f"https://www.roblox.com/games/{game['id']}" for game in games]

def get_avatar_thumbnail(user_id):
    
    url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=150x150&format=Png&isCircular=true"
    response = requests.get(url)
    thumbnail_data = response.json()
    return thumbnail_data["data"][0]["imageUrl"]

def send_discord_webhook(user_data):
    
    embed = {
        "title": f"Roblox Profile Information: {user_data['username']}",
        "description": "Message sent using code",
        "color": 0000000,  #Customize this number for your Discord embed color!
        "fields": [
            {"name": "Username", "value": user_data['username'], "inline": True},
            {"name": "Terminated Friends Count", "value": str(user_data['terminated_friends_count']), "inline": True},
            {"name": "Terminated Followers Count", "value": str(user_data['terminated_followers_count']), "inline": True},
            {"name": "Terminated Users Followed", "value": str(user_data['terminated_following_count']), "inline": True},
            {"name": "Friends", "value": ", ".join(user_data['friends']), "inline": False},
            {"name": "Terminated Friends", "value": ", ".join(user_data['terminated_friends']), "inline": False},
            {"name": "Terminated Followers", "value": ", ".join(user_data['terminated_followers']), "inline": False},
            {"name": "Terminated Following", "value": ", ".join(user_data['terminated_following']), "inline": False}
        ],
        "thumbnail": {"url": user_data['avatar_thumbnail']}
    }
    
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

def write_to_file(user_data):
    
    file_name = f"Roblox extended info - {user_data['username']}.txt"
    with open(file_name, "w") as file:
        file.write(f"Roblox Profile Information: {user_data['username']}\n\n")
        file.write(f"Terminated Friends Count: {user_data['terminated_friends_count']}\n")
        file.write(f"Terminated Followers Count: {user_data['terminated_followers_count']}\n")
        file.write(f"Terminated Users Followed: {user_data['terminated_following_count']}\n")
        file.write(f"Friends:\n{', '.join(user_data['friends'])}\n\n")
        file.write(f"Terminated Friends:\n{', '.join(user_data['terminated_friends'])}\n\n")
        file.write(f"Terminated Followers:\n{', '.join(user_data['terminated_followers'])}\n\n")
        file.write(f"Terminated Following:\n{', '.join(user_data['terminated_following'])}\n\n")
        file.write("Games:\n" + "\n".join(user_data['games']) + "\n")
    print(f"Information written to {file_name}")


input_value = input("Enter Roblox Username or User ID: ")


try:
    user_id = int(input_value)
except ValueError:
    user_id = get_user_id(input_value)
    if user_id is None:
        print("Invalid username. User not found.")
        exit()


friends = get_friends(user_id)
followers = get_followers(user_id)
following = get_following(user_id)
friends_ids = [friend["id"] for friend in friends]
followers_ids = [follower["id"] for follower in followers]
following_ids = [user["id"] for user in following]
terminated_friends_count, terminated_friends = get_terminated_count(friends_ids)
terminated_followers_count, terminated_followers = get_terminated_count(followers_ids)
terminated_following_count, terminated_following = get_terminated_count(following_ids)
games = get_game_links(user_id)
avatar_thumbnail = get_avatar_thumbnail(user_id)

#collect all stuff
user_data = {
    "username": input_value,
    "friends": [friend["name"] for friend in friends],
    "terminated_friends_count": terminated_friends_count,
    "terminated_followers_count": terminated_followers_count,
    "terminated_following_count": terminated_following_count,
    "terminated_friends": terminated_friends,
    "terminated_followers": terminated_followers,
    "terminated_following": terminated_following,
    "games": games,
    "avatar_thumbnail": avatar_thumbnail
}


character_count = sum(len(str(value)) for value in user_data.values())

# Send to Discord or write to file
if character_count <= 2000:
    send_discord_webhook(user_data)
else:
    print("The information exceeds Discord's character limit.")
    choice = input("Enter (1) to save to a file: ")
    if choice == "1":
        write_to_file(user_data)
