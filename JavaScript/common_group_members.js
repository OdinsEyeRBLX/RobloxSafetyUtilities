/* LIBRARIES REQUIRED! Run the below commands:
npm install axios
npm install prompt-sync

REPLACE THE "KEYWORD" GROUP AND ITS ID FOR ANY GROUP OF YOUR CHOICE, IT HELPS IN A QUICK CHECK IF YOU ARE CHECKING YOUR GROUP (LINE 84 - 99).

This code checks the common members between 2 groups. Enter 2 group IDs and select a number option given in the role list to scan for common members in that role of Group 1 and entire group 2.
!!! Role limitation for group 1 is done to reduce rate limits (helps to check over large flagged groups) !!!

For group 1 having a huge amount of users in the specific role, expect delays or errors due to rate limitations. Please be mindful of the size you are taking from group 1.

Simple explanation of the code for non-coders: All this code does is ask for 2 Roblox Group IDs, it returns you the list of roles from Group 1, and depending on what role you select as an option, it scans
all members of the selected role to check if they are a member of Group 2. If any common members are found, they are displayed.
*/

const axios = require('axios');
const prompt = require('prompt-sync')({ sigint: true });

async function asyncPool(poolLimit, array, iteratorFn) {
  const ret = [];
  const executing = [];
  for (const item of array) {
    const p = Promise.resolve().then(() => iteratorFn(item));
    ret.push(p);

    if (poolLimit <= array.length) {
      const e = p.then(() => executing.splice(executing.indexOf(e), 1));
      executing.push(e);
      if (executing.length >= poolLimit) {
        await Promise.race(executing);
      }
    }
  }
  return Promise.all(ret);
}

// Step 1: Get roles in group
async function getGroupRoles(groupId) {
  try {
    const response = await axios.get(`https://groups.roblox.com/v1/groups/${groupId}/roles`);
    return response.data.roles;
  } catch (error) {
    console.error('Error fetching group roles:', error.response?.data || error.message);
    return [];
  }
}

// Step 2: Get users for selected role
async function getRoleUsers(groupId, roleId) {
  const users = [];
  let cursor = null;

  do {
    try {
      const response = await axios.get(`https://groups.roblox.com/v1/groups/${groupId}/roles/${roleId}/users`, {
        params: {
          limit: 100,
          cursor: cursor
        }
      });
      users.push(...response.data.data);
      cursor = response.data.nextPageCursor;
    } catch (error) {
      console.error(`Error fetching users for role ${roleId}:`, error.response?.data || error.message);
      break;
    }
  } while (cursor);

  return users;
}

// Step 3: Check if a user is in target group
async function isUserInGroup(user, targetGroupId) {
  try {
    const response = await axios.get(`https://groups.roblox.com/v1/users/${user.userId}/groups/roles`);
    const inGroup = response.data.data.some(g => g.group.id === targetGroupId);
    return inGroup ? user.username : null;
  } catch (error) {
    console.error(`Error fetching groups for user ${user.userId}:`, error.response?.data || error.message);
    return null;
  }
}

async function main() {
  const group1Input = prompt('Enter the first group ID (source group): ').trim();
  let group2Input = prompt('Enter the second group ID (target group or "keyword"): ').trim();

  // Validate group1 ID
  const group1Id = parseInt(group1Input);
  if (isNaN(group1Id)) {
    console.log('Invalid first group ID.');
    return;
  }

  if (group2Input.toLowerCase() === 'keyword') {
    group2Input = '12345'; // REPLACE WITH YOUR GROUP ID
    console.log('Keyword detected: "keyword" → Using group ID <groupid>');
    console.log('Group name');
  }

  const group2Id = parseInt(group2Input);
  if (isNaN(group2Id)) {
    console.log('Invalid second group ID.');
    return;
  }

  const roles = await getGroupRoles(group1Id);
  if (!roles.length) {
    console.log('No roles found in the first group.');
    return;
  }

  console.log('\nPick the role to scan users of that role:');
  roles.forEach((role, idx) => {
    console.log(`${idx + 1}: ${role.name}`);
  });

  const selectedIndex = Number(prompt('\nEnter the number for the role: ')) - 1;
  const selectedRole = roles[selectedIndex];
  if (!selectedRole) {
    console.log('Invalid selection.');
    return;
  }

  console.log(`\nFetching users with role "${selectedRole.name}"...`);
  const users = await getRoleUsers(group1Id, selectedRole.id);
  if (!users.length) {
    console.log('No users found for this role.');
    return;
  }

  console.log(`Checking group memberships of ${users.length} users in parallel...`);

  // Use concurrency limit of 10 for requests
  const concurrencyLimit = 10;
  const results = await asyncPool(concurrencyLimit, users, user => isUserInGroup(user, group2Id));

  const matchedUsers = results.filter(Boolean);

  if (matchedUsers.length) {
    console.log('\nUsers in both groups:');
    matchedUsers.forEach(name => console.log(name));
  } else {
    console.log('\nNo users found in common between selected Group 1 role and Group 2.');
  }
}

main();
