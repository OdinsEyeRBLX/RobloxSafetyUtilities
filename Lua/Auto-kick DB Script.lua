-- PLACE THIS SCRIPT IN SERVERSCRIPTSERVICE
-- THIS SCRIPT AUTO-KICKS THE PLAYER IF THEY ARE IN THE SCOUT DATABASE: https://scout-system.onrender.com/

-- SETTINGS
local discordWebhookURL = "YOUR_DISCORD_WEBHOOK_URL_HERE" -- !!!!!!!!!!!!!!!!!!!!!! REPLACE WITH YOUR DISCORD WEBHOOK !!!!!!!!!!!!!!!!!!!!!!!
local scoutApiUrl = "https://fallback-node.onrender.com/fallback-check/" -- API to check if the joined user is a known threat
local kickMessage = "[ S.C.O.U.T. ]\n\nYou have been automatically removed from this experience due to being flagged as a severe security threat."

-- Automatically convert standard Discord webhook to the lewisakura proxy to bypass Roblox restrictions
local webhookURL = string.gsub(discordWebhookURL, "discord%%.com", "webhook.lewisakura.moe")

-- SERVICES
local httpService = game:GetService("HttpService")
local players = game:GetService("Players")

-- FUNCTION: Check SCOUT database
local function checkScoutDatabase(player)
	local url = scoutApiUrl .. player.UserId
	local success, response = pcall(function() return httpService:GetAsync(url) end)
	
	if not success then 
		warn("[SCOUT] API request failed:", response) 
		return nil 
	end
	
	local parseSuccess, data = pcall(function() return httpService:JSONDecode(response) end)
	if not parseSuccess then 
		warn("[SCOUT] JSON decode failed") 
		return nil 
	end

	-- Render Fallback returns { isThreat: true, details: {...} }
	if data and data.isThreat and data.details then
		if data.details.tier == "CRITICAL" or data.details.tier == "HIGH" then
			return data.details
		end
	end
	return nil
end

local function sendDiscordAlert(playerName, playerId, playerDisplayName, threatDetails)
	if webhookURL == "" or webhookURL == "YOUR_DISCORD_WEBHOOK_URL_HERE" then 
		warn("[SCOUT] No webhook URL set") 
		return 
	end
	
	local timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ")

	local embed = {
		title = "<:SCOUT:1434492864041324595> S.C.O.U.T. Game Subsystem: Player Kicked",
		description = string.format("`%s` (`@%s`) has been auto-kicked.\n\nProfile:\nhttps://www.roblox.com/users/%d/profile", playerDisplayName, playerName, playerId),
		color = 16711680,
		fields = {
			{ name = "Threat Tier", value = tostring(threatDetails.tier or "Unknown"), inline = true },
			{ name = "Risk Score", value = tostring(threatDetails.riskscore or 0), inline = true },
			{ name = "Flagged Groups", value = tostring(threatDetails.flaggedgroups or 0), inline = true }
		},
		thumbnail = { url = "https://www.roblox.com/headshot-thumbnail/image?userId=" .. playerId .. "&width=150&height=150&format=png" },
		timestamp = timestamp
	}

	local payload = { embeds = { embed } }
	local jsonData = httpService:JSONEncode(payload)

	task.spawn(function()
		local success, response = pcall(function() 
			return httpService:PostAsync(webhookURL, jsonData, Enum.HttpContentType.ApplicationJson) 
		end)
		
		if success then 
			print("[SCOUT] ✅ Webhook sent for:", playerName) 
		else 
			warn("[SCOUT] ❌ Webhook failed:", response) 
		end
	end)
end

local function handlePlayer(player)
	print("[SCOUT] Checking player:", player.Name)
	local threatDetails = checkScoutDatabase(player)

	if threatDetails then
		print("[SCOUT] <:SCOUT:1434492864041324595> Threat detected:", player.Name)
		sendDiscordAlert(player.Name, player.UserId, player.DisplayName, threatDetails)
		task.wait(1)
		player:Kick(kickMessage)
	else
		print("[SCOUT] Player safe:", player.Name)
	end
end

players.PlayerAdded:Connect(handlePlayer)
