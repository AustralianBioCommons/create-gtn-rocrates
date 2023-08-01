
### script copied from https://github.com/bio-tools/biohackathon2022/blob/353570d03a3cccc73294b907c7c79ac9f814d815/scripts/workflowhub_galaxy_biotools.py on 2023-07-28
### license: MIT

###########################################################
### CITATION here https://doi.org/10.37044/osf.io/79kje ###
###########################################################

import requests, json, re, itertools

###############
## Examples ###
###############

### workflow: https://workflowhub.eu/workflows/220.json
### galaxy API id: toolshed.g2.bx.psu.edu/repos/devteam/picard/picard_SamToFastq/2.18.2.2
### workflowhub step description: \n toolshed.g2.bx.psu.edu/repos/devteam/picard/picard_SamToFastq/2.18.2.2

#####################################
### Copied and modified code from ###
#####################################

### https://github.com/AustralianBioCommons/australianbiocommons.github.io/blob/4c771d9fece80dacce259304688c2aadb23962ca/finders/toolfinder.py
### https://github.com/AustralianBioCommons/australianbiocommons.github.io/blob/4c771d9fece80dacce259304688c2aadb23962ca/finders/workflowfinder.py

#####################################################
### Access Galaxy API & extract ID + bio.tools ID ###
#####################################################

def galaxy_api_request(url):
    galaxy_api_req = requests.request("get", url)
    if galaxy_api_req.status_code != 200:
        raise FileNotFoundError(galaxy_api_req.url)
    tool_sections = json.loads(galaxy_api_req.text)
    ### Herve Menager via Slack
    tools_nested = [tool_section.get('elems') for tool_section in tool_sections if 'elems' in tool_section]
    tools = list(itertools.chain.from_iterable(tools_nested))
    return(tools)

