
from functions import *
from workflowhub_galaxy_biotools import *


############################################
### step 1 access API to get topic areas ###
############################################

# GTN API https://training.galaxyproject.org/training-material/api/
# from https://github.com/AustralianBioCommons/australianbiocommons.github.io/blob/master/finders/toolfinder.py

req = requests.request("get", "https://training.galaxyproject.org/training-material/api/topics.json")
if req.status_code != 200:
    raise FileNotFoundError(req.url)
gtn_topic_list = json.loads(req.text)


#################################################################################################
### step 2 access API again to get metadata materials from each tutorial from each topic area ###
#################################################################################################

gtn_topic_urls = get_topic_urls(topic_list = gtn_topic_list, topic_match_string = "[Mm]etabolomics")
gtn_contents_for_all_topics = get_content_for_all_topics(topic_urls = gtn_topic_urls)


################################################
### step 3 ensure access to workflow.ga file ###
################################################

gtn_workflow_metadata = get_gtn_workflow_metadata(contents_for_all_topics = gtn_contents_for_all_topics)


######################################################
### step 4 list all tools in the workflow.ga files ###
######################################################

for workflow in gtn_workflow_metadata:
    gtn_tool_ids = []
    if 'workflow_steps' in gtn_workflow_metadata[workflow]:
        workflow_steps = gtn_workflow_metadata[workflow]['workflow_steps']
        for step in workflow_steps:
            if workflow_steps[step]['tool_id'] is not None:
                tool_id = workflow_steps[step]['tool_id']
                if tool_id not in gtn_tool_ids:
                    gtn_tool_ids.append(tool_id)


####################################################
### step 5 compare tools across Galaxy instances ###
####################################################

### GALAXY AUSTRALIA ###
galaxy_AU_tools = galaxy_api_request(url = "https://usegalaxy.org.au/api/tools")
### GALAXY EUROPE ###
galaxy_Eu_tools = galaxy_api_request(url = "https://usegalaxy.eu/api/tools")

instances = {
    "Galaxy_EU": galaxy_Eu_tools,
    "Galaxy_AU": galaxy_AU_tools
             }

def merge_tools_from_multiple_galaxy_instances_and_GTN(instance_dictionary, gtn_tool_id_list, panel_section_id):

    main_list = {}

    for instance in instance_dictionary:
        instance_temp = instance_dictionary[instance]
        for tool in range(len(instance_temp)):
            tool_data = instance_temp[tool]
            if 'panel_section_id' in tool_data:
                if tool_data['panel_section_id'] == panel_section_id:
                    name = tool_data["name"]
                    id = tool_data["id"]
                    if id not in main_list:
                        main_list[id] = {}
                        main_list[id]['name'] = name
                        main_list[id]['instance'] = [instance]
                    else:
                        main_list[id]['instance'].append(instance)

    for tool_id in gtn_tool_id_list:
        if tool_id not in main_list:
            main_list[tool_id] = {}
            main_list[tool_id]['GTN'] = "True"
        else:
            main_list[tool_id]['GTN'] = "True"

    return(main_list)

main_list = merge_tools_from_multiple_galaxy_instances_and_GTN(instance_dictionary = instances,
                                           gtn_tool_id_list = gtn_tool_ids,
                                           panel_section_id = "metabolomics")

