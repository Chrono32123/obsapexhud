import requests
import json
import obspython as obs
import os

run_boolean = False

#rank_value and prev_rank_value need to be different at the start of the script.
rank_image_url = ""
arena_image_url = ""
rank_value = "0"
arenas_rank_value = "0"
prev_rank_value = "-1"
arenas_prev_rank_value = prev_rank_value

debug = False
check_interval = 15
rank_img_source = ""
rank_val_source = ""
arenas_rank_img_source = ""
arenas_rank_val_source = ""
default_location = "ranks"

#credentials needed to make the request to tracker.gg
username = ""
apikey = ""
platform = ""

def script_description():
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function:script description")
    return "Display Apex Legends Player Informaiton"

def script_properties():
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function: script properties")
    
    props = obs.obs_properties_create()


    #Enable/Disable Script
    obs.obs_properties_add_bool(props,"run_boolean","Run?")

    #refresh interval
    obs.obs_properties_add_int(props, "check_interval_int", "Update Interval (seconds)", 1, 120, 1)

    #rank image dimensions
    obs.obs_properties_add_int(props, "rank_height", "Height (pixels)", 1, 1000, 1)
    obs.obs_properties_add_int(props, "rank_width", "Width (pixels)", 1, 1000, 1)

    #platform selector
    platform_select = obs.obs_properties_add_list(
        props,
        "platform_select",
        "Platform Select:",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    obs.obs_property_list_add_string(platform_select,"","")
    obs.obs_property_list_add_string(platform_select,"xbl","xbl")
    obs.obs_property_list_add_string(platform_select,"psn","psn")
    obs.obs_property_list_add_string(platform_select,"origin","origin")

    #username input
    obs.obs_properties_add_text(props, "userName", "Gamertag:", obs.OBS_TEXT_DEFAULT)

    #tracker.gg api key input
    obs.obs_properties_add_text(props, "api_key", "Tracker.gg Api Key:", obs.OBS_TEXT_DEFAULT)

    #Rank Image Source
    rank_img_source = obs.obs_properties_add_list(
        props,
        "rank_img_source",
        "Ranked Image Source",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    obs.obs_property_list_add_string(rank_img_source, "", "")

    #Rank Value Source
    rank_val_source = obs.obs_properties_add_list(
        props,
        "rank_val_source",
        "Ranked Value Source",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    obs.obs_property_list_add_string(rank_val_source, "", "")

    #Arenas Rank Image Source
    arenas_rank_img_source = obs.obs_properties_add_list(
        props,
        "arenas_rank_img_source",
        "Arenas Ranked Image Source",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    obs.obs_property_list_add_string(arenas_rank_img_source, "", "")
    
    #Arenas Rank Value Source
    arenas_rank_val_source = obs.obs_properties_add_list(
        props,
        "arenas_rank_val_source",
        "Arenas Ranked Value Source",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    obs.obs_property_list_add_string(arenas_rank_val_source, "", "")

    #get the image and text sources and populate the drop down lists
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "image_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(rank_img_source, name, name)
                obs.obs_property_list_add_string(arenas_rank_img_source, name, name)
            if source_id == "text_gdiplus":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(rank_val_source, name, name)
                obs.obs_property_list_add_string(arenas_rank_val_source, name, name)
    
    obs.source_list_release(sources)

    return props

def script_defaults(settings):
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function: script defaults")
    
     
    obs.obs_data_set_default_bool(settings, "run_boolean", False)
    obs.obs_data_set_default_int(settings, "check_interval_int", 60)
    obs.obs_data_set_default_int(settings, "rank_height", 200)
    obs.obs_data_set_default_int(settings, "rank_width", 200)

def script_update(settings):
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function: script update")
    
    global check_interval
    global rank_img_source
    global rank_val_source
    global arenas_rank_img_source
    global arenas_rank_val_source
    global run_boolean
    global username
    global apikey
    global platform

    rank_height = obs.obs_data_get_int(settings, "rank_height")
    rank_width = obs.obs_data_get_int(settings, "rank_width")
    rank_img_source = obs.obs_data_get_string(settings,"rank_img_source")
    rank_val_source = obs.obs_data_get_string(settings,"rank_val_source")
    arenas_rank_img_source = obs.obs_data_get_string(settings,"arenas_rank_img_source")
    arenas_rank_val_source = obs.obs_data_get_string(settings,"arenas_rank_val_source")
    run_boolean = obs.obs_data_get_bool(settings, "run_boolean")
    
    obs.timer_remove(update_stats)

    if not run_boolean:
        return
    
    setup_source(rank_img_source, rank_height, rank_width)
    setup_source(arenas_rank_img_source, rank_height, rank_width)

    username = obs.obs_data_get_string(settings,"userName")
    platform = obs.obs_data_get_string(settings,"platform_select")
    apikey = obs.obs_data_get_string(settings,"api_key")
    
    obs.timer_add(update_stats, check_interval * 1000)

def update_stats():
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function: update rank")

    global rank_image_url
    global arena_image_url
    global rank_value
    global prev_rank_value
    global arenas_rank_value
    global arenas_prev_rank_value
    global rank_img_source
    global rank_val_source
    global arenas_rank_img_source
    global arenas_rank_val_source

    #if the rank values haven't changed, don't make a call.
    if (prev_rank_value == rank_value) and (arenas_prev_rank_value == arenas_rank_value):
        return
    
    #build the request
    url = f'https://public-api.tracker.gg/v2/apex/standard/profile/{platform}/{username}'
    headers = {
        'TRN-api-key':apikey
    }

    #make the api call
    resp = requests.get(url, headers=headers)

    #grab the response and parse out the data we need
    info = resp.json()
    data = info["data"]
    segments = data["segments"]

    #parse ranked data out of response
    rankScore = segments[0].get("stats").get("rankScore")
    rankMeta = rankScore.get("metadata")
    rank_image_url = rankMeta.get("iconUrl")
    rank_value = rankScore.get("value")
    
    #parse arenas ranked data out of response
    arenaScore = segments[0].get("stats").get("arenaRankScore")
    arenaMeta = arenaScore.get("metadata")
    arena_image_url = arenaMeta.get("iconUrl")
    arenas_rank_value = arenaScore.get("value")
    #arenas_rank_value = str(arenas_rank_value)[:-2] #dropping the decimal place
    
    #close response
    resp.close()
    
    #cache the image returned from the call and set its location to the image source
    location = cache_image(rank_image_url, default_location)

    image_source = obs.obs_get_source_by_name(rank_img_source)
    if image_source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "file", location)
        obs.obs_source_update(image_source, settings)
        obs.obs_data_release(settings)
    obs.obs_source_release(image_source)
    
    value_source = obs.obs_get_source_by_name(rank_val_source)
    if value_source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", str(rank_value)[:-2])
        obs.obs_source_update(value_source, settings)
        obs.obs_data_release(settings)
    obs.obs_source_release(value_source)

    #do the same as above but for arena ranks
    location = cache_image(arena_image_url, f"{default_location}/arenas")

    image_source = obs.obs_get_source_by_name(arenas_rank_img_source)
    if image_source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "file", location)
        obs.obs_source_update(image_source, settings)
        obs.obs_data_release(settings)
    obs.obs_source_release(image_source)
    
    value_source = obs.obs_get_source_by_name(arenas_rank_val_source)
    if value_source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", str(arenas_rank_value)[:-2])
        obs.obs_source_update(value_source, settings)
        obs.obs_data_release(settings)
    obs.obs_source_release(value_source)

    #set the previous rank value to the rank value returned from the api
    #this prevents the script from making api calls that don't update anything
    prev_rank_value = rank_value
    arenas_prev_rank_value = arenas_rank_value

def cache_image(link, location):
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function: Cache image")

    # Set the cache folder
    cache_folder = f"{script_path()}cache/{location}/"

    # Get the file name from the image link
    filename = link.split("/")[-1]

    # Check if image doesn't exist. If so, then download and store it in the cache
    if not os.path.isfile(cache_folder + filename):
        r = requests.get(link)
        with open(cache_folder + filename, "wb") as f:
            f.write(r.content)
            f.close()
        r.close()

    return cache_folder + filename

def setup_source(source_name, height, width):
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function: setup source")
    current_scene = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(current_scene)
    obs.obs_source_release(current_scene)

    source = obs.obs_scene_find_source(scene, source_name)

    obs.obs_sceneitem_set_bounds_type(source, obs.OBS_BOUNDS_SCALE_INNER)

    new_scale = obs.vec2()
    new_scale.x = height
    new_scale.y = width
    obs.obs_sceneitem_set_bounds(source, new_scale)