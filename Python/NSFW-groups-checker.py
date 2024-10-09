import requests

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

def is_user_in_group(user_id, group_id):
    url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
    response = requests.get(url)
    data = response.json()
    
    if "data" in data:
        for group in data["data"]:
            if group["group"]["id"] == group_id:
                return True
    return False

def validate_multi_group_membership(username_or_id, group_ids):
    
    try:
        user_id = int(username_or_id)
    except ValueError:
        user_id = get_user_id(username_or_id)
        if user_id is None:
            print("Invalid username. User not found.")
            return
    
    # check group membership
    member_groups = []
    for group_id in group_ids:
        if is_user_in_group(user_id, group_id):
            # Create a link to the group
            group_link = f"https://www.roblox.com/groups/{group_id}"
            member_groups.append((group_id, group_link))

    if member_groups:
        print("The user is a member of the following groups:")
        for group_id, link in member_groups:
            print(f" - Group ID: {group_id} | Link: {link}")
    else:
        print("The user is not a member of any of the specified groups.")


username_or_id = input("Enter Roblox Username or User ID: ")
#add group IDs below, existing IDs are a few of the MANY nsfw/erp groups on Roblox. | This list can update as time passes, be sure to keep checking the Github page.
group_ids = [34874583, 4554783, 34458835, 5443802, 13833400, 14324390, 9455955, 34717641, 34864392, 34944555, 16795620, 11514702, 16119725, 34697482, 10196423, 7424914, 4172002, 16163214, 15081762, 13407796, 32983524, 7713435, 34717641, 16304795]  # Add NSFW/ERP Roblox group IDs to the list
validate_multi_group_membership(username_or_id, group_ids)
