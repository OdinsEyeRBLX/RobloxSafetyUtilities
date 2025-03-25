//WARNING: MAKE SURE YOU HAVE THE CORRECT PACKAGES INSTALLED! INSTALL NODE.JS AND RUN "npm install axios prompt-sync" IN THE VS TERMINAL TO INSTALL THE REQUIRED PACKAGES FOR THIS PROGRAM!
//ERROR CODE 423 MEANS THAT YOU ARE RATE LIMITED, TRY AGAIN AFTER SOME TIME!
//Due to Roblox's current friends.roblox.com/v1/users base API returning only 200 users, you can only check for the membership of the first 200 of the friend's users.

const axios = require('axios');
const prompt = require('prompt-sync')();
const USER_URL = 'https://users.roblox.com/v1/users/';
const GROUP_URL = 'https://groups.roblox.com/v1/groups/';
const FRIENDS_URL = 'https://friends.roblox.com/v1/users/';
async function getUserGroups(userId) {
  try {
    const response = await axios.get(`https://groups.roblox.com/v1/users/${userId}/groups/roles`);
    return response.data.data;
  } catch (error) {
    console.error(`Error getting user groups for user ${userId}: ${error}`);
    return [];
  }
}
async function getUserProfile(userId) {
  try {
    const response = await axios.get(`${USER_URL}${userId}`);
    const data = response.data;
    return {
      username: data.name,
      profileLink: `https://roblox.com/users/${userId}/profile`
    };
  } catch (error) {
    console.error(`Error getting user profile for ${userId}: ${error}`);
    return null;
  }
}
async function getUserFriends(userId) {
  try {
    const response = await axios.get(`${FRIENDS_URL}${userId}/friends`);
    return response.data.data.map(friend => friend.id);
  } catch (error) {
    console.error(`Error getting user friends for user ${userId}: ${error}`);
    return [];
  }
}
async function checkUserAndFriendsInGroup(userId, groupId) {
  let members = [];
  console.log(`Checking user ${userId}...`);
  const userGroups = await getUserGroups(userId);
  const inGroup = userGroups.some(group => group.group.id === groupId);

  if (inGroup) {
    const userProfile = await getUserProfile(userId);
    if (userProfile) {
      members.push(userProfile);
    }
  }
  const friends = await getUserFriends(userId);
  const friendsGroupCheckPromises = friends.map(async (friendId) => {
    console.log(`Checking friend ${friendId}...`);
    const friendGroups = await getUserGroups(friendId);
    if (friendGroups.some(group => group.group.id === groupId)) {
      const friendProfile = await getUserProfile(friendId);
      if (friendProfile) {
        members.push(friendProfile);
      }
    }
  });
  await Promise.all(friendsGroupCheckPromises);

  return members;
}
async function main() {
  const usernameOrId = prompt('Enter the Roblox username or User ID: ');
  const groupId = prompt('Enter the Group ID to search: ');

  let userId;
  const groupIdInt = parseInt(groupId);
  if (isNaN(groupIdInt)) {
    console.log("Invalid Group ID.");
    return;
  }
  if (!isNaN(usernameOrId)) {
    userId = parseInt(usernameOrId);
  } else {
    try {
      const response = await axios.get(`https://users.roblox.com/v1/users/search?keyword=${usernameOrId}`);
      const data = response.data;
      if (data.data.length > 0) {
        userId = data.data[0].id;
      } else {
        console.log("No user found with that username.");
        return;
      }
    } catch (error) {
      console.error(`Error searching for user: ${error}`);
      return;
    }
  }
  const members = await checkUserAndFriendsInGroup(userId, groupIdInt);

  if (members.length > 0) {
    console.log(`\nMembers of Group ${groupIdInt}:`);
    members.forEach(member => {
      console.log(`Username: ${member.username}, Profile Link: ${member.profileLink}`);
    });
  } else {
    console.log(`No members found in group ${groupIdInt} among the user and their friends.`);
  }
}

main();
