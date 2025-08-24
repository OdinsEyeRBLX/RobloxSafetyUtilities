const axios = require('axios');
const prompt = require('prompt-sync')();

// DISCORD WEBHOOK
const WEBHOOK_URL = 'YOUR_DISCORD_WEBHOOK'; // Replace with your actual webhook

// Map AssetTypeId to readable names
const assetTypeMap = {
  1: "Image", 2: "T-Shirt", 3: "Audio", 4: "Mesh", 8: "Hat", 9: "Place", 10: "Model",
  11: "Shirt", 12: "Pants", 13: "Decal", 21: "Avatar", 24: "Animation", 34: "Emote",
  38: "Plugin", 40: "MeshPart", 41: "Hair Accessory", 42: "Face Accessory", 43: "Neck Accessory",
  44: "Shoulder Accessory", 45: "Front Accessory", 46: "Back Accessory", 47: "Waist Accessory"
};

const input = prompt('Enter one or more Roblox Asset IDs (comma-separated): ');
const assetIds = input.split(',').map(id => id.trim()).filter(Boolean);
async function getAssetField(assetId) {
  try {
    const assetUrl = `https://economy.roblox.com/v2/assets/${assetId}/details`;
    const assetResponse = await axios.get(assetUrl);
    const assetData = assetResponse.data;

    const creatorId = assetData.Creator.Id;
    const userUrl = `https://users.roblox.com/v1/users/${creatorId}`;
    const userResponse = await axios.get(userUrl);
    const creatorName = userResponse.data.name;

    const typeName = assetTypeMap[assetData.AssetTypeId] || `Unknown (ID ${assetData.AssetTypeId})`;

    return {
      name: `${assetData.Name || "Unnamed"} [Asset ID: ${assetId}]`,
      value:
        `**Type:** ${typeName}\n` +
        `**Price:** ${assetData.PriceInRobux ? `${assetData.PriceInRobux} Robux` : "Free"}\n` +
        `**Creator:** [${creatorName}](https://www.roblox.com/users/${creatorId}/profile)\n` +
        `**Created:** ${new Date(assetData.Created).toDateString()}\n` +
        `[View on Roblox](https://www.roblox.com/library/${assetId})`,
      inline: false
    };
  } catch (error) {
    return {
      name: `Error with Asset ID: ${assetId}`,
      value: `\`\`\`${error.response?.data?.errors?.[0]?.message || error.message}\`\`\``,
      inline: false
    };
  }
}

(async () => {
  const allFields = await Promise.all(assetIds.map(getAssetField));
  const embedChunks = [];
  for (let i = 0; i < allFields.length; i += 25) {
    embedChunks.push(allFields.slice(i, i + 25));
  }

  // Prepare and send embeds
  for (let i = 0; i < embedChunks.length; i++) {
    const embed = {
      embeds: [
        {
          title: embedChunks.length > 1
            ? `Asset Info (Page ${i + 1} of ${embedChunks.length})`
            : "Roblox Asset Info",
          color: 0x3498db,
          fields: embedChunks[i],
          footer: {
            text: `Showing ${embedChunks[i].length} of ${allFields.length} assets`
          }
        }
      ]
    };

    try {
      const res = await axios.post(WEBHOOK_URL, embed);
      if (res.status !== 204) {
        console.error(`❌ Failed to send embed page ${i + 1}:`, res.statusText);
      }
    } catch (err) {
      console.error(`❌ Discord webhook error on page ${i + 1}:`, err.message);
    }
  }

  console.log("✅ All embeds sent to Discord.");
})();
