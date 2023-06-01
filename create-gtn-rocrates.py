import requests
import json
from rocrate.rocrate import ROCrate


############################################
### step 1 access API to get topic areas ###
############################################

# GTN API https://training.galaxyproject.org/training-material/api/
# from https://github.com/AustralianBioCommons/australianbiocommons.github.io/blob/master/finders/toolfinder.py

all_data = {}

req = requests.request("get", "https://training.galaxyproject.org/training-material/api/topics.json")
if req.status_code != 200:
    raise FileNotFoundError(req.url)
topic_list = json.loads(req.text)

#################################################################################################
### step 2 access API again to get metadata materials from each tutorial from each topic area ###
#################################################################################################

topic_urls = {}
for topic in topic_list:
    topic_id = topic_list[topic]['name']
    url = topic_list[topic]['url']
    topic_urls[topic_id] = url

### /topics/{topicId}.json
### /topics/{topicId}/tutorials/{tutorialId}/{material}.json

contents_for_all_topics = {}
for topic_id in topic_urls:
    req = requests.request("get", topic_urls[topic_id])
    if req.status_code != 200:
        raise FileNotFoundError(req.url)
    topic_contents = json.loads(req.text)
    contents_for_all_topics[topic_id] = topic_contents


################################################
### step 3 ensure access to workflow.ga file ###
################################################

### example url to GTN workflow file
# https://training.galaxyproject.org/training-material/topics/metagenomics/tutorials/general-tutorial/workflows/
# ['dir'] = topics/metagenomics/tutorials/general-tutorial
# + '/workflows/'
# + ['workflows'] which contains dict with workflows, can be multiple

gtn_workflow_metadata = {}

for topic in contents_for_all_topics:
    materials_data = contents_for_all_topics[topic]['materials']
    for i in range(len(materials_data)):
        # extract single GTN materials from the topic
        single_materials = materials_data[i]
        if 'workflows' in single_materials:
            ### for each workflow that exists in the single GTN materials
            for workflow in range(len(single_materials['workflows'])):
                ### collect workflow GTN metadata
                workflow_data = single_materials['workflows'][workflow]
                ### extract GTN metadata of interest
                gtn_wf_id = workflow_data['wfid']
                gtn_title = single_materials['title']
                gtn_topic = single_materials['topic_name']
                gtn_contributors = single_materials['contributors']
                gtn_url = single_materials['url']
                if 'zenodo_link' in single_materials:
                    gtn_zenodo = single_materials['zenodo_link']
                else:
                    gtn_zenodo = "Not available"
                ### extract the workflow URL
                workflow_url = workflow_data['url']
                ### request the workflow using its URL
                workflow_file_request = requests.request("get", workflow_url)
                if workflow_file_request.status_code != 200:
                    raise FileNotFoundError(workflow_file_request.url)
                ### load workflow file contents
                workflow_file_metadata = json.loads(workflow_file_request.text)
                ### also save workflow file to a local directory for creation of RO-crates downstream
                # see https://stackoverflow.com/a/63440075
                new_workflow_file_name = "./workflow_files/" + gtn_wf_id + ".ga"
                file = open(new_workflow_file_name, "w")
                file.write(workflow_file_request.text)
                file.close()
                ### add workflow ID to dictionary created above for all GTN workflow metadata
                if gtn_wf_id not in gtn_workflow_metadata:
                    gtn_workflow_metadata[gtn_wf_id] = {}
                ### annotate the workflow entry with all required metadata
                gtn_workflow_metadata[gtn_wf_id]['gtn_title'] = gtn_title
                gtn_workflow_metadata[gtn_wf_id]['gtn_topic'] = gtn_topic
                gtn_workflow_metadata[gtn_wf_id]['gtn_contributors'] = gtn_contributors
                gtn_workflow_metadata[gtn_wf_id]['gtn_url'] = gtn_url
                gtn_workflow_metadata[gtn_wf_id]['gtn_zenodo'] = gtn_zenodo
                gtn_workflow_metadata[gtn_wf_id]['workflow_name'] = workflow_file_metadata['name']
                if 'annotation' in workflow_file_metadata:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_annotation'] = workflow_file_metadata['annotation']
                else:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_annotation'] = "Not available"
                if 'tags' in workflow_file_metadata:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_tags'] = workflow_file_metadata['tags']
                else:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_tags'] = "Not available"
                if 'license' in workflow_file_metadata:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_license'] = workflow_file_metadata['license']
                else:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_license'] = "Not available"
                if 'creator' in workflow_file_metadata:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_creator'] = workflow_file_metadata['creator']
                else:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_creator'] = "Not available"
                if 'uuid' in workflow_file_metadata:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_uuid'] = workflow_file_metadata['uuid']
                else:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_uuid'] = "Not available"
                if 'version' in workflow_file_metadata:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_version'] = workflow_file_metadata['version']
                else:
                    gtn_workflow_metadata[gtn_wf_id]['workflow_version'] = "Not available"
                gtn_workflow_metadata[gtn_wf_id]['workflow_steps'] = workflow_file_metadata['steps']


#######################################################################
### step 4 ensure the correct metadata is available for an RO-crate ###
#######################################################################

# What metadata is required?
# 1. workflow file (*.ga)
# 2. type: "workflows"
# 3. attributes:
#       "title",
#       "description",
#       "workflow_class": "galaxy",
#       "tags"
#       "operation_annotations"
#       "topic_annotations"
#       "license"
# 4. relationships
#       "creators": "data"


####################################################
### step 5 create RO-crate for all GTN materials ###
####################################################

### create single RO-crate
# see https://github.com/ResearchObject/ro-crate-py

### example
one_workflow = gtn_workflow_metadata['visualisation-circos']

crate = ROCrate()
workflow = crate.add_file("./workflow_files/assembly-assembly-quality-control.ga")
from rocrate.model.person import Person

if 'workflow_creator' in one_workflow:
    for creator in range(len(one_workflow['workflow_creator'])):
        data = one_workflow['workflow_creator'][creator]
        creator_entry = crate.add(Person(crate, data['identifier'], properties={
            "name": data['name']
        }))
        workflow["author"] = creator_entry

crate.write("exp_crate")

