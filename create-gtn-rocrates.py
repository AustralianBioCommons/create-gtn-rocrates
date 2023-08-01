
import os
import requests
from functions import *
from rocrate.rocrate import ROCrate
#from rocrate.model.contextentity import ContextEntity
from rocrate.model.person import Person
from rocrateValidator import validate as validate


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


gtn_topic_urls = get_topic_urls(topic_list = gtn_topic_list)
gtn_contents_for_all_topics = get_content_for_all_topics(topic_urls = gtn_topic_urls)


################################################
### step 3 ensure access to workflow.ga file ###
################################################

gtn_workflow_metadata = get_gtn_workflow_metadata(contents_for_all_topics = gtn_contents_for_all_topics)


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


#####################################################
### step 5 create RO-crates for all GTN materials ###
#####################################################

# see https://github.com/ResearchObject/ro-crate-py



for workflow_id in gtn_workflow_metadata:

    workflow_data = gtn_workflow_metadata[workflow_id]

    crate = ROCrate()


    #workflow = crate.add_file("./workflow_files/" + workflow_id + ".ga")
    #workflow = crate.add(ContextEntity(crate, workflow_id, properties={
    #    "@type": ["File", "SoftwareSourceCode", "ComputationalWorkflow"],
    #    "name": workflow_data['workflow_name'],
    #    "version": workflow_data['workflow_version'],
    #    "license": workflow_data['workflow_license']
    #}))

    #workflow = crate.add_workflow(os.path.join('./workflow_files/',f"{workflow_id}.ga"),main=True,lang="galaxy",gen_cwl=False)
    workflow = crate.add_workflow(os.path.join('./workflow_files/', f"{workflow_id}"), main=True, lang="galaxy",gen_cwl=False)

    if isinstance(workflow_data['workflow_creator'], list):
        creator_list = []
        for creator in range(len(workflow_data['workflow_creator'])):
            data = workflow_data['workflow_creator'][creator]
            if 'identifier' in data:
                creator_entry = crate.add(Person(crate, data['identifier'], properties={
                    "name": data['name']
                }))
            else:
                creator_entry = crate.add(Person(crate, properties={
                    "name": data['name']
                }))
            creator_list.append(creator_entry)
        workflow["author"] = creator_list

    crate_file = os.path.join("./ro_crates/", workflow_id.replace(".","_") + "---" + workflow_data['workflow_uuid'])

    crate.write(crate_file)

    #######################################################
    ### step 6 validate RO-crates for all GTN materials ###
    #######################################################

    # see https://github.com/ResearchObject/ro-crate-validator-py/blob/main/demo.ipynb

    # see https://stackoverflow.com/a/3207973
    #for file in os.listdir("./ro_crates"):

    v = validate.validate(crate_file)
    v.validator()

#########################################################
### step 7 test submission to dev API for WorkflowHub ###
#########################################################

### dev instance of WorkflowHub : https://dev.workflowhub.eu/
### see also https://about.workflowhub.eu/developer/ro-crate-api/



payload = { 'ro_crate': ('my_ro_crate.crate.zip ', open('my_ro_crate.crate.zip', 'rb')),
            'workflow[project_ids][]': (None, '1234') }
headers = { 'authorization': 'Token YOUR_TOKEN_HERE' }

response = requests.post('https://workflowhub.eu/workflows', files=payload, headers=headers)






