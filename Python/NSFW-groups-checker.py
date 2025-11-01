const axios = require('axios');
const readline = require('readline');

// GitHub raw URL for the flagged group IDs file - this allows automation
const GROUP_IDS_URL = 'https://raw.githubusercontent.com/OdinsEyeRBLX/RobloxSafetyUtilities/main/FLAGGED%20ERP%20GROUPS.txt';

async function loadGroupIdsFromGithub() {
    try {
        const response = await axios.get(GROUP_IDS_URL);
        const content = response.data;
        const groupIds = new Set(
            content
                .split(',')
                .map(id => id.trim())
                .filter(id => /^\d+$/.test(id))
                .map(Number)
        );
        return groupIds;
    } catch (error) {
        console.error("Error fetching group IDs:", error.message);
        return new Set();
    }
}

async function getUserId(username) {
    try {
        const response = await axios.post("https://users.roblox.com/v1/usernames/users", {
            usernames: [username],
            excludeBannedUsers: false
        });
        const data = response.data;
        return data.data?.[0]?.id || null;
    } catch (error) {
        console.error("Error fetching user ID:", error.message);
        return null;
    }
}

async function getUserGroups(userId) {
    try {
        const url = `https://groups.roblox.com/v1/users/${userId}/groups/roles`;
        const response = await axios.get(url);
        return response.data.data.map(group => ({
            id: group.group.id,
            name: group.group.name
        }));
    } catch (error) {
        console.error("Error fetching user groups:", error.message);
        return [];
    }
}

async function validateMultiGroupMembership(usernameOrId, knownGroupIds) {
    let userId;

    if (/^\d+$/.test(usernameOrId)) {
        userId = parseInt(usernameOrId, 10);
    } else {
        userId = await getUserId(usernameOrId);
        if (!userId) {
            console.log("Invalid username. User not found.");
            return;
        }
    }

    console.log("Retrieving user groups...");
    const userGroups = await getUserGroups(userId);

    if (userGroups.length > 0) {
        console.log("Checking group memberships against known ERP groups...");
        const memberGroups = userGroups.filter(group => knownGroupIds.has(group.id));

        if (memberGroups.length > 0) {
            console.log("The user is a member of the following known ERP groups:");
            memberGroups.forEach((group, index) => {
                const link = `https://www.roblox.com/groups/${group.id}`;
                console.log(` - ${group.name} | Link: ${link} | ${index + 1}`);
            });
        } else {
            console.log("The user is not a member of any of the specified groups.");
        }
    } else {
        console.log("The user is not a member of any groups.");
    }
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.question("Enter Roblox Username or User ID: ", async (input) => {
    const knownGroupIds = await loadGroupIdsFromGithub();
    await validateMultiGroupMembership(input, knownGroupIds);
    rl.close();
});
