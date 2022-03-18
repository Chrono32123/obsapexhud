import requests
import json
import obspython as obs
import os

run_boolean = False

#rank_value and prev_rank_value need to be different at the start of the script.
rank_image_url = ""
rank_value = "0"
prev_rank_value = "-1"

debug = False
check_interval = 15
rank_img_source = ""
rank_val_source = ""
default_location = "ranks"



def script_description():
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function:script description")
    return "Display Apex Legends Rank Informaiton"

def script_properties():
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function: script properties")
    
    props = obs.obs_properties_create()

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

    #tracker.gg api key
    obs.obs_properties_add_text(props, "api_key", "Tracker.gg Api Key:", obs.OBS_TEXT_DEFAULT)

    #Rank Image Location
    rank_img_source = obs.obs_properties_add_list(
        props,
        "rank_img_source",
        "Ranked Image Source",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    obs.obs_property_list_add_string(rank_img_source, "", "")

    #Rank Value Location
    rank_val_source = obs.obs_properties_add_list(
        props,
        "rank_val_source",
        "Ranked Value Source",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    obs.obs_property_list_add_string(rank_val_source, "", "")

    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "image_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(rank_img_source, name, name)
            if source_id == "text_gdiplus":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(rank_val_source, name, name)
    
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
    global run_boolean

    rank_height = obs.obs_data_get_int(settings, "rank_height")
    rank_width = obs.obs_data_get_int(settings, "rank_width")
    rank_img_source = obs.obs_data_get_string(settings,"rank_img_source")
    rank_val_source = obs.obs_data_get_string(settings,"rank_val_source")

    json_file = obs.obs_data_get_string(settings, "json_file")

    setup_source(rank_img_source, rank_height, rank_width)
    
    obs.timer_remove(update_rank)

    if not run_boolean:
        return
    
    username = obs.obs_data_get_string(settings,"userName")
    platform = obs.obs_data_get_string(settings,"platform_select")
    apikey = obs.obs_data_get_string(settings,"api_key")
    
    obs.timer_add(update_rank(username, platform, apikey), check_interval * 1000)

def update_rank(username, platform, apikey):
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function: update rank")

    global rank_image_url
    global rank_value
    global prev_rank_value
    global rank_img_source
    global rank_val_source

    print(prev_rank_value, rank_value)
    #if the rank value hasn't changed, don't make a call.
    if prev_rank_value == rank_value:
        print("no updates needed.")
        return
    
    print("making the request")
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
    rankScore = segments[0].get("stats").get("rankScore")
    rankMeta = rankScore.get("metadata")
    rank_image_url = rankMeta.get("iconUrl")
    rank_value = rankScore.get("value")
    rank_value = str(rank_value)[:-2]
    
    #cache the image returned from the call
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
        obs.obs_data_set_string(settings, "text", str(rank_value))
        obs.obs_source_update(value_source, settings)
        obs.obs_data_release(settings)
    obs.obs_source_release(value_source)

    prev_rank_value = rank_value

def cache_image(link, location):
    # If debug is enabled, print out this bit of text
    if debug:
        print("Function: Cache image")

    # Set the cache folder
    cache_folder = f"{script_path()}cache/{location}/"

    # Get the file name from the image link
    filename = link.split("/")[-1]

    # Check if doesn't exist. If so, then download it and store it in the cache
    if not os.path.isfile(cache_folder + filename):
        r = requests.get(link)
        with open(cache_folder + filename, "wb") as f:
            f.write(r.content)

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