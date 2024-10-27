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
group_ids = [34874583, 4554783, 34458835, 5443802, 13833400, 14324390, 9455955, 34717641, 34864392, 34944555, 16795620, 11514702, 16119725, 34697482, 10196423, 7424914, 4172002, 16163214, 15081762, 13407796, 32983524, 7713435, 34717641, 16304795, 33437758, 15713304, 6458502, 34918086, 15922716, 34444795, 10832235, 34477069, 32699422, 5812000, 34734752, 33855513, 33896637, 10196423, 13163042, 15912864, 34997222, 9593321, 35063781, 34988364, 16960276, 34616910, 1018746, 17241057, 34749564, 34841849, 7146011, 5717913, 34641882, 16339899, 33849843, 8080203, 12246485, 13678537, 6553297, 2626818, 16224651, 34463529, 4928849, 7315709, 15346060, 35062509, 33349824, 8791955, 19208, 35061031, 34408471, 7736495, 17310816, 16865265, 34186236, 11094955, 9486597, 5751342, 35065141, 8852238, 35008055, 34140106, 10016889, 9709065, 34927755, 6142620, 6318545, 33508385, 11166218, 9129599, 15321257, 13764554, 7405371, 34396635, 13802474, 33533199, 32970279, 34758955, 34832659, 34832953, 33203346, 35008055, 4996692, 15441981, 33630415, 35101898, 35039840, 34437676]  # Add NSFW/ERP Roblox group IDs to the list
validate_multi_group_membership(username_or_id, group_ids)
