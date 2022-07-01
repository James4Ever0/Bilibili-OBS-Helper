obs         = obslua
start_script_name = ""
end_script_name = ""

function run_node()
   local liveKey = ''
   local tmpfile = '/tmp/bilibili-live-key.txt'
   os.execute(start_script_name..' > '..tmpfile)
   local f = io.open(tmpfile)
   if not f then return files end  
   local k = 1
   for line in f:lines() do
		liveKey = line
   end
   f:close()
   return liveKey
end

function on_event(event)
	if event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTING then
		if start_script_name ~= "start_script" then
			obs.script_log(obs.LOG_INFO, "executing " .. start_script_name)
			local liveKey = run_node()
			obs.script_log(obs.LOG_INFO, "Get Bilibili live key: " .. liveKey)

    		local service = obs.obs_frontend_get_streaming_service()
    		local settings = obs.obs_service_get_settings(service)
    		obs.obs_data_set_string(settings, "key", liveKey)
    		obs.obs_service_update(service, settings)
    		obs.obs_data_release(settings)
    		obs.obs_frontend_save_streaming_service()
		end
	end
end
-----------------------------------------------------------------------------------------------------

function script_update(settings)
	start_script_name = obs.obs_data_get_string(settings, "start_script_name")
	end_script_name = obs.obs_data_get_string(settings, "end_script_name")
end

function script_description()
	return "run a script / executable when the stream starts or ends"
end

function script_properties()
	props = obs.obs_properties_create()

	obs.obs_properties_add_path(props, "start_script_name", "Start Stream", obs.OBS_PATH_FILE, "(*.exe *.bat *.sh);;(*.*)", NULL)
	obs.obs_properties_add_path(props, "end_script_name", "End Stream", obs.OBS_PATH_FILE, "(*.exe *.bat *.sh);;(*.*)", NULL)
		
	return props
end

function script_defaults(settings)
	obs.obs_data_set_default_string(settings, "start_script_name", "start_script")
	obs.obs_data_set_default_string(settings, "end_script_name", "end_script")
end

function script_load(settings)
	obs.obs_frontend_add_event_callback(on_event)
end