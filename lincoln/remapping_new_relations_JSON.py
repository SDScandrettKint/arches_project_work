import pandas as pd
import json
import numpy as np
import sys
import os 
import uuid

def inserttile(nodegroupUUID, tilerelationshiptype, tileinverserelationshiptype, resourceTO_UUID, resourceFROM_UUID):
    resourceX = str(uuid.uuid4())
    tileid_UUID = str(uuid.uuid4())
    jsonnodedataraw = '''{"data": {
    "%s": [
        {
            "inverseOntologyProperty": "%s",
            "ontologyProperty": "%s",
            "resourceId": "%s",
            "resourceXresourceId": "%s"
        }
    ]
},
"nodegroup_id": "%s",
"parenttile_id": null,
"provisionaledits": null,
"resourceinstance_id": "%s",
"sortorder": 0,
"tileid": "%s"}''' % (nodegroupUUID, tileinverserelationshiptype, tilerelationshiptype, resourceTO_UUID, resourceX, nodegroupUUID, resourceFROM_UUID, tileid_UUID)

    jsonnodedata = json.loads(jsonnodedataraw)
    return jsonnodedata


def additionaltile(tilerelationshiptype, tileinverserelationshiptype, resourceTO_UUID):
    resourceX = str(uuid.uuid4())
    jsonnodedataraw = '''{"inverseOntologyProperty": "%s",
                        "ontologyProperty": "%s",
                        "resourceId": "%s",
                        "resourceXresourceId": "%s"}''' % (
        tileinverserelationshiptype, tilerelationshiptype, resourceTO_UUID, resourceX)

    jsonnodedata = json.loads(jsonnodedataraw)
    return jsonnodedata



### MAIN SCRIPT ###

allrelations_name = sys.argv[1]
JSON_file = sys.argv[2]
graph_UUID_from = sys.argv[3]
outputfilename = sys.argv[4]

# First go through all relations 
# Filter by graph ID specified in CLI
allrelations_df = pd.read_csv(allrelations_name, na_filter=False)
graphfilter = allrelations_df['resourceinstancefrom_graphid']==graph_UUID_from #True or false
allrelations_filtered = allrelations_df[graphfilter]


# Variables that are specific to each model
target_node_one = "918b5530-ad43-11ed-bf2c-679a3495f33a"
lincolnassocnode = "cd0e2a19-a62e-11ed-bf2c-679a3495f33a"



# Open JSON and store
with open(JSON_file) as f:
    res_data = json.load(f)


# Iterate through allrelations and get the values we require (resource UUIDs, relationshiptype and graph UUID)
for residfrom, residto, relationshiptype, inverserelation, graphidto in zip(
    allrelations_filtered["resourceinstanceidfrom"], 
    allrelations_filtered["resourceinstanceidto"],
    allrelations_filtered["relationshiptype"],
    allrelations_filtered["inverserelationshiptype"],
    allrelations_filtered["resourceinstanceto_graphid"]):



    # For each UUID filtered by graph id that is in the JSON data
    for resource in res_data["business_data"]["resources"]:
        for res, v in resource["resourceinstance"].items():
            if res == "resourceinstanceid":
                resource_UUID = v

                # If the resource matches go ahead with data manipulation
                # Go through each resources data in the JSON file
                if resource_UUID == residfrom:
                    
                    tile_len_res = len(resource["tiles"])
                    no_falses = 0

                    for alltile in resource["tiles"]:
                        # data is structured tiles: [ { data : { }}]
                        # so tile data is within an array in a dictionary

                        for tilesuuid, tilesvalues in alltile.items():
                            #print(tilesuuid, tilesvalues)
                            # If the current nodegroup id isnt target node then doesnodeexist is false
                            doesnodeexist = False

                            # FIRST check if the lincoln associated nodegroup exists and if so set to null and empty relations list 
                            if tilesuuid == 'nodegroup_id' and tilesvalues == lincolnassocnode:
                                for oldkey, oldval in alltile["data"].items():
                                    if type(oldval) == list:
                                        oldval.clear()

                                #resource["tiles"].remove(alltile)
                                

                            # Now onto adding the new tiles
                            # If it is target node set doesnodeexist to true and add to it
                            if tilesuuid == 'nodegroup_id' and tilesvalues == target_node_one:
                                doesnodeexist = True
                                # Does the json already contain the correct data or is there more that needs adding?
                                for existing_rel_data in alltile["data"][target_node_one]:
                                    
                                    if existing_rel_data["resourceId"] == residto:
                                        break
                                    else: # Add the new ones
                                        additionalOne = additionaltile(relationshiptype, inverserelation, residto)
                                        alltile["data"][target_node_one].append(additionalOne)
                                        break


                            # If doesnodeexist is true break out of that block
                            if doesnodeexist == True:
                                break


                        # Count the number of falses
                        # This also signals the end of one data blocks has been reached
                        if doesnodeexist == False:
                            no_falses += 1
                        
                        # If have reached the end of all tiles within a resource and none included the target nodegroup
                        # the number of falses will equal the length of the resource tiles
                        # then ADD THE TILE:
                        if tile_len_res == no_falses:
                            newtile = inserttile(target_node_one, relationshiptype, inverserelation, residto, residfrom)
                            resource["tiles"].append(newtile)
                            no_falses += 1 # Set higher so it can't loop forever
                            break
                            


### Return JSON converted data
# Save JSON output to name specified by cli                   
with open ("%s.json" % (outputfilename), "w") as out_file:
    json.dump(res_data, out_file)
