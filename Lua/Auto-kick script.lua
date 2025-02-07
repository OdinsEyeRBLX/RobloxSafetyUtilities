-- List of group IDs to check against
local groupIDs = {34874583, 4554783, 34458835, 5443802} 
-- Replace with your group IDs or add any additional group IDs


-- ____________________________________________________________________
-- PLEASE CHECK THE "FLAGGED ERP GROUPS.TXT" IN THE MAIN REPOSITORY FOR THE GROUP IDS FLAGGED SO FAR!
-- ____________________________________________________________________



-- Replace with Discord webhook link
local webhookURL = "https://discord.com/api/webhooks/your-webhook-URL"


local httpService = game:GetService("HttpService")

-- Main functions
local function isInGroup(player)
	for _, groupId in ipairs(groupIDs) do
		local rank = player:GetRankInGroup(groupId)
		if rank > 0 then 
			return groupId, rank
		end
	end
	return nil, nil
end
local function getAvatarHeadshotUrl(player)
	local userId = player.UserId
	local url = "https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=" .. userId .. "&size=420x420&format=Png&isCircular=false"

	local success, response = pcall(function()
		return httpService:GetAsync(url)
	end)

	if success then
		local data = httpService:JSONDecode(response)
		if data and data.data and #data.data > 0 then
			return data.data[1].imageUrl
		end
	end
	return "https://www.roblox.com/headshot-thumbnail/image?userId=" .. userId .. "&width=420&height=420&format=png"
end

local function sendDiscordAlert(player, groupId, rank)
	local rankName = player:GetRoleInGroup(groupId)
	local timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ") -- Current UTC/GMT time
	local headshotUrl = getAvatarHeadshotUrl(player)

	local embed = {
		["title"] = "Auto-kick Alert | SafetyCheck",
		["description"] = string.format(
			"`%s` (@%s) has been auto-kicked due to being found in the group: `%d` with rank `%s`.\nProfile link: https://www.roblox.com/users/%d/profile \n Group link: https://www.roblox.com/communities/%d",
			player.DisplayName, player.Name, groupId, rankName, player.UserId, groupId
		),
		["color"] = 16711680, -- Red color for the embed
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
		warn("Failed to send Discord webhook: " .. response)
	end
end

game.Players.PlayerAdded:Connect(function(player)
	local groupId, rank = isInGroup(player)
	if groupId then
		local success, errorMsg = pcall(function()
			player:Kick("You were caught in restricted communities and have been kicked.")
		end)

		if not success then
			warn("Error kicking player: " .. errorMsg)
		else
			sendDiscordAlert(player, groupId, rank)
		end
	end
end)
