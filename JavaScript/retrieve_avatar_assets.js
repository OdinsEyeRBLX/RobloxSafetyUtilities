//Can be run with "node retrieve_avatar_assets.js" if Node.js v10 and above is installed.

//Sends a detailed list of Roblox assets on an Avatar (even if terminated - will help in checking how bad the account was)

// NEWER ROBLOX BANS MAY NOT RETURN USER DATA WHEN REQUESTED REMOTELY WITH OPTION 1 (because the username is removed), THUS YOU MUST HAVE THEIR ID AND USE OPTION 2

const https = require('https');
const readline = require('readline');
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const webhookUrl = 'DISCORD_WEBHOOK_HERE'; //ADD YOUR DISCORD WEBHOOK LINK
function fetchJson(url, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const options = new URL(url);
    const requestOptions = {
      hostname: options.hostname,
      path: options.pathname + (options.search || ''),
      method: method,
      headers: {
        'Content-Type': 'application/json',
      }
    };

    const req = https.request(requestOptions, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json);
        } catch (err) {
          reject(err);
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}


function sendWebhook(payload) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(payload);

    const url = new URL(webhookUrl);

    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };

    const req = https.request(options, res => {
      if (res.statusCode >= 200 && res.statusCode < 300) {
        console.log('✅ Webhook sent successfully!');
        resolve();
      } else {
        reject(new Error(`❌ Failed to send webhook. Status: ${res.statusCode}`));
      }
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}


async function getUserIdFromUsername(username) {
  const response = await fetchJson(
    'https://users.roblox.com/v1/usernames/users',
    'POST',
    { usernames: [username], excludeBannedUsers: false }
  );

  const matched = response.data?.[0];
  if (matched) {
    return matched.id;
  } else {
    throw new Error('Username not found.');
  }
}


async function getUserId(input) {
  if (/^\d+$/.test(input)) {
    return input;
  } else {
    return await getUserIdFromUsername(input);  // Look up User ID from Username
  }
}
async function handleUserOption(input, isWebhook) {
  try {
    const userId = await getUserId(input);
    const userData = await fetchJson(`https://avatar.roblox.com/v1/users/${userId}/avatar`);
    const userProfile = await fetchJson(`https://users.roblox.com/v1/users/${userId}`);
    const username = userProfile.name
    const embed = {
      content: `Avatar details for Roblox user **${username}** (ID: ${userId})`,
      embeds: [
        {
          title: `Avatar Info for User ID: ${userId}`,
          description: `Here are the items the user is wearing:`,
          fields: [],
          color: 0x1D82B6,
        }
      ]
    };

    const assetIds = [];

    if (userData.assets && userData.assets.length > 0) {
      userData.assets.forEach(asset => {
        assetIds.push(asset.id);
        embed.embeds[0].fields.push({
          name: `${asset.name} (ID: ${asset.id})`,
          value: `[View Item](https://www.roblox.com/catalog/${asset.id})`,
          inline: true
        });
      });
    }

    embed.embeds[0].fields.push({
      name: 'All Asset IDs',
      value: assetIds.length ? assetIds.join(', ') : 'None',
      inline: false
    });

    if (isWebhook) {
      await sendWebhook(embed);
      console.log('✅ Webhook sent successfully!');
      rl.close();
      process.exit(0);
    } else {
      console.log("📝 Asset IDs for User ID:", userId);
      console.log(assetIds.length ? assetIds.join(', ') : 'No assets found for this user.');
      rl.close();
      process.exit(0);
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    rl.close();
    process.exit(1);
  }
}

rl.question('Choose an option:\n1. Get Avatar Details and Send to Webhook (Username or User ID)\n2. Get Asset IDs for User ID Only\nEnter 1 or 2: ', async (choice) => {
  rl.question('Enter Roblox User ID or Username: ', async (input) => {
    if (choice === '1') {

      await handleUserOption(input, true);
    } else if (choice === '2') {
      await handleUserOption(input, false);
    } else {
      console.log("⚠️ Invalid choice. Please enter 1 or 2.");
      rl.close();
    }
  });
});
