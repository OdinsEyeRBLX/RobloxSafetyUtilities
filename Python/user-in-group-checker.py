import requests

def get_user_id(username):
    url = f"https://users.roblox.com/v1/usernames/users"
    payload = {
        "usernames": [username],
        "excludeBannedUsers": True
    }
    response = requests.post(url, json=payload)
    data = response.json()
    
    if data["data"]:
        return data["data"][0]["id"]
    else:
        return None

def get_user_group_role(user_id, group_id):
    url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
    response = requests.get(url)
    data = response.json()

    if "data" in data:
        for group in data["data"]:
            if group["group"]["id"] == group_id:
                role_name = group["role"]["name"]
                return True, role_name
    return False, None

input_value = input("Enter Roblox Username or User ID: ")
group_id = int(input("Enter Group ID: "))

#check if input is username or ID | DO NOT MESS WITH THIS
try:
    user_id = int(input_value)
except ValueError:
    user_id = get_user_id(input_value)
    if user_id is None:
        print("Invalid username. User not found.")
        exit()

# Check if the user is in the group
user_in_group, role_name = get_user_group_role(user_id, group_id)

if user_in_group:
    print(f"User exists in the group with the role: {role_name}")
else:
    print("User does not exist in the group.")
