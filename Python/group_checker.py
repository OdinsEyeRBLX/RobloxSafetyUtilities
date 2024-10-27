import requests
import concurrent.futures

def get_user_info(user_id):
    url = f"https://users.roblox.com/v1/users/{user_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("displayName", ""), data.get("description", "")
    else:
        print(f"Failed to retrieve info for user ID: {user_id}")
        return "", ""

def fetch_page(group_id, cursor=None):
    url = f"https://groups.roblox.com/v1/groups/{group_id}/users?sortOrder=Asc&limit=100"
    if cursor:
        url += f"&cursor={cursor}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data for group.")
        return {}

def get_all_members(group_id):
    members = []
    initial_data = fetch_page(group_id)
    if 'data' not in initial_data:
        print("No data returned. Please check the group ID and try again.")
        return members
    
    members.extend(initial_data['data'])
    cursor = initial_data.get('nextPageCursor')
    while cursor:
        data = fetch_page(group_id, cursor)
        members.extend(data.get('data', []))
        cursor = data.get('nextPageCursor')

    return members

def process_members(group_id, option):
    members = get_all_members(group_id)
    
    # Define flagged phrases for usernames/display names and bios -> add any suggestive/common-among-erp-accounts words to the existing list
    flagged_phrases = ["bull", "toy", "fvta", "buni", "bunn", "soft", "bio", "stress", "black", "spade", "clock", "bxll", "femm", "dog", "mommy", "dxddy", "dom", "sub", "snow", "sn0w", "blxck", "m0mmy", "inch", "vnch", "trad", "white", "young", "stud", "enjoyer"]
    flagged_bio_phrases = ["studio", "spade", "nsfw", "playmate", "model", "top", "bottom", "clock", "wallet", "escort", "experience", "toy", "doll", "kitten", "bunn", "fvta", "cat", "add", "follow", "dom", "sub", "mommy", "fem", "cow", "bull", "tos", "💿", "💽", "khord", "blue app", "blueapp", "rp", "games", "black", "white", "🐮", "🥛", "♠️", "❄️", "🐇", "🐂", "literate", "limit", "hmu", "morph", "char"]
    
    flagged_users = []
    all_users = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_member = {executor.submit(get_user_info, member['user']['userId']): member for member in members}
        
        for future in concurrent.futures.as_completed(future_to_member):
            member = future_to_member[future]
            display_name, bio = future.result()
            username = member['user']['username']
            profile_link = f"https://www.roblox.com/users/{member['user']['userId']}/profile"
            role = member['role']['name']
            
            # Check for flagged phrases in username/display name and bio
            warning_flag = any(phrase in username.lower() or phrase in display_name.lower() for phrase in flagged_phrases)
            bio_warning_flag = any(phrase in (bio or "").lower() for phrase in flagged_bio_phrases)
            
            if option == 1:
                if warning_flag or bio_warning_flag:
                    flagged_users.append((profile_link, username, display_name, bio, role))
                    warning_text = "NAME WARNING, " if warning_flag else ""
                    bio_warning_text = "BIO WARNING" if bio_warning_flag else ""
                    print(f"{display_name} (@{username}) <{profile_link}> {warning_text} {bio_warning_text}")
                    print(f"Role: {role}")
                    if bio_warning_flag:
                        print(f"Bio: {bio}\n")


            all_users.append((display_name, username, profile_link, role))

    if option == 1:
        save_flagged = input("Save flagged users to file? (1 to save, 0 to skip): ")
        if save_flagged == "1":
            with open("flagged_erp_users.txt", "a", encoding="utf-8") as f:
                for user in flagged_users:
                    profile_link, username, display_name, bio, _ = user
                    f.write(f"{profile_link} - {username} - {bio}\n")
            print("Flagged users saved to flagged_erp_users.txt.")

    elif option == 2:
        print("All group members:")
        for user in all_users:
            display_name, username, profile_link, role = user
            print(f"{display_name} (@{username}) - {profile_link} - Role: {role}")

group_id = input("Enter group ID to retrieve users from: ")
option = int(input("Select option:\n1 -> Flagged users\n2 -> List all group members\n"))
process_members(group_id, option)
