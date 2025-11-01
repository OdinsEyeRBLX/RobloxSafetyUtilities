import requests
import re

# GitHub raw URL for the flagged group IDs file
GROUP_IDS_URL = 'https://raw.githubusercontent.com/OdinsEyeRBLX/RobloxSafetyUtilities/main/FLAGGED%20ERP%20GROUPS.txt'

def load_group_ids_from_github():
    try:
        response = requests.get(GROUP_IDS_URL)
        response.raise_for_status()
        content = response.text
        group_ids = set(
            map(int, filter(lambda x: re.match(r'^\d+$', x), content.split(',')))
        )
        return group_ids
    except requests.RequestException as e:
        print(f"Error fetching group IDs: {e}")
        return set()

def get_user_id(username):
    try:
        response = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [username], "excludeBannedUsers": False}
        )
        response.raise_for_status()
        data = response.json()
        return data['data'][0]['id'] if data['data'] else None
    except requests.RequestException as e:
        print(f"Error fetching user ID: {e}")
        return None

def get_user_groups(user_id):
    try:
        url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
        response = requests.get(url)
        response.raise_for_status()
        groups_data = response.json()
        return [{"id": group['group']['id'], "name": group['group']['name']} for group in groups_data['data']]
    except requests.RequestException as e:
        print(f"Error fetching user groups: {e}")
        return []

def validate_multi_group_membership(username_or_id, known_group_ids):
    user_id = None

    # Check if the input is a number (ID) or a username
    if username_or_id.isdigit():
        user_id = int(username_or_id)
    else:
        user_id = get_user_id(username_or_id)
        if not user_id:
            print("Invalid username. User not found.")
            return

    print("Retrieving user groups...")
    user_groups = get_user_groups(user_id)

    if user_groups:
        print("Checking group memberships against known ERP groups...")
        member_groups = [
            group for group in user_groups if group['id'] in known_group_ids
        ]

        if member_groups:
            print("The user is a member of the following known ERP groups:")
            for index, group in enumerate(member_groups, start=1):
                link = f"https://www.roblox.com/groups/{group['id']}"
                print(f" - {group['name']} | Link: {link} | {index}")
        else:
            print("The user is not a member of any of the specified groups.")
    else:
        print("The user is not a member of any groups.")

def main():
    username_or_id = input("Enter Roblox Username or User ID: ")
    known_group_ids = load_group_ids_from_github()
    validate_multi_group_membership(username_or_id, known_group_ids)

if __name__ == "__main__":
    main()
