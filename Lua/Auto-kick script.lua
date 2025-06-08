-- THIS ROBLOX LUA SCRIPT AUTO-KICKS USERS IN ERP GROUPS AND SENDS A DISCORD WEBHOOK ALERT/LOG
-- SETTINGS
local webhookURL = "YOUR_DISCORD_WEBHOOK" -- Copy paste your Discord webhook link
local groupIDFileURL = "https://raw.githubusercontent.com/OdinsEyeRBLX/RobloxSafetyUtilities/main/FLAGGED%20ERP%20GROUPS.txt"
local refreshInterval = 300 -- Time in seconds to refresh group list (default: 5 minutes)

-- SERVICES
local httpService = game:GetService("HttpService")
local players = game:GetService("Players")
local runService = game:GetService("RunService")


local groupIDs = {}

-- FUNCTION: Fetch and parse group IDs
local function fetchGroupIDs()
	local success, response = pcall(function()
		return httpService:GetAsync(groupIDFileURL)
	end)

	if success and response then
		groupIDs = {}
		for id in string.gmatch(response, "%d+") do
			table.insert(groupIDs, tonumber(id))
		end
		print("[Automod] Successfully updated group ID list. Total IDs: " .. #groupIDs)
	else
		warn("[Automod] Failed to fetch group IDs: " .. tostring(response))
	end
end

-- FUNCTION: Check if player is in any flagged group
local function isInGroup(player)
	for _, groupId in ipairs(groupIDs) do
		local rank = player:GetRankInGroup(groupId)
		if rank > 0 then
			local success, groupInfo = pcall(function()
				return game:GetService("GroupService"):GetGroupInfoAsync(groupId)
			end)
			if success and groupInfo then
				return groupInfo.Name, groupId, rank
			else
				return tostring(groupId), groupId, rank
			end
		end
	end
	return nil, nil, nil
end


-- FUNCTION: Get player's avatar headshot URL

-- Replace this with your actual Google Apps Script URL [LOOK BELOW IN THE MULTILINE COMMENT TO FIND APPS SCRIPT CODE]
local proxyURL = "https://script.google.com/macros/s/AKfy..../exec"

local function getAvatarHeadshotUrl(player)
	local userId = player.UserId
	local url = proxyURL .. "?userId=" .. userId

	local success, response = pcall(function()
		return httpService:GetAsync(url)
	end)

	if success and response then
		local isValidUrl = response:match("^https?://tr%.rbxcdn%.com/.+")
		if isValidUrl then
			return response
		else
			warn("[Automod] Invalid image URL or not ready yet: " .. response)
		end
	else
		warn("[Automod] Failed to fetch avatar headshot for userId " .. userId .. ": " .. tostring(response))
	end
	-- Fallback (may not embed in Discord correctly, but better than nothing)
	return "https://www.roblox.com/headshot-thumbnail/image?userId=" .. userId .. "&width=420&height=420&format=png"
end



-- FUNCTION: Send Discord alert
local function sendDiscordAlert(player, groupName, groupId, rank)
	local rankName = player:GetRoleInGroup(groupId)
	local timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ")
	local headshotUrl = getAvatarHeadshotUrl(player)

	local embed = {
		["title"] = "Automod: User is a safety concern",
		["description"] = string.format(
			"`%s` (`@%s`) has been auto-kicked due to being found in the group: **`%s (%d)`** with rank `%s`.\n\n**Profile link:** https://www.roblox.com/users/%d/profile \n\n**Group link:** https://www.roblox.com/communities/%d",
			player.DisplayName, player.Name, groupName, groupId, rankName, player.UserId, groupId
		),
		["color"] = 16711680,
		["thumbnail"] = {
			["url"] = headshotUrl  
		},
		["timestamp"] = timestamp
	}

	local data = {
		["embeds"] = {embed}
	}

	local jsonData = httpService:JSONEncode(data)
	local success, response = pcall(function()
		return httpService:PostAsync(webhookURL, jsonData, Enum.HttpContentType.ApplicationJson)
	end)

	if not success then
		warn("[Automod] Failed to send Discord webhook: " .. response)
	end
end

-- FUNCTION: Check and handle new players
local function handlePlayer(player)
	local groupName, groupId, rank = isInGroup(player)
	if groupId then
		sendDiscordAlert(player, groupName, groupId, rank)
		task.wait(2)
		player:Kick("[Automod] User is a safety concern.")
	end
end



-- INITIALIZE
fetchGroupIDs()

-- Player join handling
players.PlayerAdded:Connect(handlePlayer)

-- AUTO-UPDATE GROUP LIST
task.spawn(function()
	while true do
		task.wait(refreshInterval)
		fetchGroupIDs()
	end
end)



--[[
----------------------------------------------------------------------------------------
GOOGLE APPS SCRIPT CODE | GO TO https://script.google.com/home AND MAKE A NEW PROJECT, COPY PASTE THIS THERE AND MAKE A NEW DEPLOYMENT AS WEB APP, GIVE ACCESS TO "ANYONE" AND COPY THE URL AND PASTE ABOVE IN THE CODE

function doGet(e) {
  var userId = e.parameter.userId;
  if (!userId) {
    return ContentService.createTextOutput("Missing userId").setMimeType(ContentService.MimeType.TEXT);
  }

  var url = "https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=" + userId + "&size=420x420&format=Png&isCircular=false";
  var response = UrlFetchApp.fetch(url);
  var json = JSON.parse(response.getContentText());

  if (json && json.data && json.data.length > 0 && json.data[0].state === "Completed") {
    var imageUrl = json.data[0].imageUrl;
    return ContentService.createTextOutput(imageUrl).setMimeType(ContentService.MimeType.TEXT);
  } else {
    return ContentService.createTextOutput("Image not ready").setMimeType(ContentService.MimeType.TEXT);
  }
}

 ]]
