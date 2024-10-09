import requests

def get_group_members(group_id):
    url = f"https://groups.roblox.com/v1/groups/{group_id}/users?sortOrder=Asc&limit=100"
    members = []
    
    while url:
        response = requests.get(url)
        data = response.json()

        for member in data['data']:
            user_id = member['user']['userId']
            username = member['user']['username']
            profile_link = f"https://www.roblox.com/users/{user_id}/profile"
            members.append({"username": username, "profile_link": profile_link})
        
        # check for pagination
        url = data.get('nextPageCursor')
        if url:
            url = f"https://groups.roblox.com/v1/groups/{group_id}/users?cursor={url}&sortOrder=Asc&limit=100"
    
    return members


group_id = input("Enter group ID to retrieve users from: ")  # takes input from user, input MUST BE ROBLOX GROUP ID
members = get_group_members(group_id)

for member in members:
    print(f"Username: {member['username']}, Profile Link: {member['profile_link']}")