
import requests
import json
import re


# see https://stackoverflow.com/a/71618773
def get_topic_urls(topic_list, topic_match_string = None):

    topic_urls = {}

    for topic in topic_list:
        # code below copied from and inspired by toolfinder_reporting code
        # https://stackoverflow.com/a/70672659
        # https://stackoverflow.com/a/12595082
        # https://stackoverflow.com/a/4843178
        # https://stackoverflow.com/a/15340694
        gtn_topic_name = topic_list[topic]['name']
        if topic_match_string is not None:
            if re.search(topic_match_string, gtn_topic_name):
                # https://stackoverflow.com/a/49912808
                url = topic_list[topic]['url']
                topic_urls[gtn_topic_name] = url
        else:
            url = topic_list[topic]['url']
            topic_urls[gtn_topic_name] = url

    return(topic_urls)


### /topics/{topicId}.json
### /topics/{topicId}/tutorials/{tutorialId}/{material}.json

def get_content_for_all_topics(topic_urls):
    contents_for_all_topics = {}
    for topic_id in topic_urls:
        req = requests.request("get", topic_urls[topic_id])
        if req.status_code != 200:
            raise FileNotFoundError(req.url)
        topic_contents = json.loads(req.text)
        contents_for_all_topics[topic_id] = topic_contents
    return(contents_for_all_topics)


### example url to GTN workflow file
# https://training.galaxyproject.org/training-material/topics/metagenomics/tutorials/general-tutorial/workflows/
# ['dir'] = topics/metagenomics/tutorials/general-tutorial
# + '/workflows/'
# + ['workflows'] which contains dict with workflows, can be multiple

def get_gtn_workflow_metadata(contents_for_all_topics):

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
                    gtn_wf_id = workflow_data['wfid'] + "---" + workflow_data['workflow']
                    print(gtn_wf_id)
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
                    new_workflow_file_name = "./workflow_files/" + gtn_wf_id
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

    return (gtn_workflow_metadata)

