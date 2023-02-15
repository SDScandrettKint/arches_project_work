import pandas as pd
import numpy as np
import sys
import os 
import uuid

# Resource Model definitions:
modelUUID_dict = {"Lincoln Associated Organization" : "d4a88461-5463-11e9-90d9-000d3ab1e58",
                "Lincoln Associated Historic Aircraft" : "b8032b00-594d-11e9-9cf0-18cf5eb368c4",
                "Lincoln Associated Place" : "78b32d8c-b6f2-11ea-af42-f875a44e0e11",
                "Lincoln Associated Application Area" : "42ce82f6-83bf-11ea-b1e8-f875a44e0e11",
                "Lincoln Associated Digital Object" : "a535a235-8481-11ea-a6b9-f875a44e0e11",
                "Lincoln Associated Archive Source" : "b07cfa6f-894d-11ea-82aa-f875a44e0e11",
                "Lincoln Associated Heritage Story" : "0add0e11-99aa-11ea-9ab8-f875a44e0e11",
                "Lincoln Associated Maritime Vessel" : "49bac32e-5464-11e9-a6e2-000d3ab1e588",
                "Lincoln Associated Person" : "22477f01-1a44-11e9-b0a9-000d3ab1e588",
                "Lincoln Associated Activity" : "b9e0701e-5463-11e9-b5f5-000d3ab1e588",
                "Lincoln Associated Period" : "f9045867-8861-11ea-b06f-f875a44e0e11",
                "Lincoln Associated Bibliographic Source" : "24d7b54f-5464-11e9-a86b-000d3ab1e588",
                "Lincoln Associated Heritage Area" : "979aaf0b-7042-11ea-9674-287fcf6a5e72",
                "Lincoln Associated Listed Buildings" : "360a22d8-7097-11ed-b2a8-09a7eb3130f4",
                "Lincoln Associated Scheduled Monument" : "8da5808c-74bb-11ed-b2a8-09a7eb3130f4",
                "Lincoln Associated Artefact" : "343cc20c-2c5a-11e8-90fa-0242ac120005",
                "Lincoln Associated Consultation" : "8d41e49e-a250-11e9-9eab-00224800b26d",
                "Lincoln Associated Conservation Areas" : "fd9e22c2-74bb-11ed-b2a8-09a7eb3130f4",
                "Lincoln Associated Heritage Asset" : "076f9381-7b00-11e9-8d6b-80000b44d1d9",
                "Lincoln Associated Historic Landscape Characterization" : "934cd7f0-480a-11ea-9240-c4d9877d154e"}

# Declare inputs
allrelations_name = sys.argv[1]
csv_name = sys.argv[2]
graph_UUID_from = sys.argv[3]
final_name = sys.argv[4]

# First go through allrelations.csv 
# Filter by graph ID specified in CLI
allrelations_df = pd.read_csv(allrelations_name, na_filter=False)
graphfilter = allrelations_df['resourceinstancefrom_graphid']==graph_UUID_from #True or false
allrelations_filtered = allrelations_df[graphfilter]

# Go through resource csv file
resource_df = pd.read_csv(csv_name)

# Iterate through allrelations and get the values we require (resource UUIDs, relationshiptype and graph UUID)
for residfrom, residto, relationshiptype, inverserelation, graphidto in zip(
    allrelations_filtered["resourceinstanceidfrom"], 
    allrelations_filtered["resourceinstanceidto"],
    allrelations_filtered["relationshiptype"],
    allrelations_filtered["inverserelationshiptype"],
    allrelations_filtered["resourceinstanceto_graphid"]):
    
    
    # Create string for new resource relation node
    newrelationval = {"resourceId": "", "ontologyProperty": "", "resourceXresourceId": "", "inverseOntologyProperty": ""}
    newrelationval["resourceId"] = residto
    newrelationval["resourceXresourceId"] = str(uuid.uuid4())
    if relationshiptype:
        newrelationval["ontologyProperty"] = relationshiptype
    if inverserelation:
        newrelationval["inverseOntologyProperty"] = inverserelation


    # With the resource ids, relationshiptype and graph id TO that needs to be linked
    # can go through the resource CSV and filter for that resource id FROM index
    if residfrom in resource_df['ResourceID'].values:
        res_index = (resource_df[resource_df["ResourceID"]==residfrom].index.values)

        # Find correct node from graph UUID dictionary and get it's column index
        for key, value in modelUUID_dict.items():
            if value == graphidto:
                assoc_node_index = resource_df.columns.get_loc(key)
                
                # To detect if a cell is empty requires the following that must be converted into str
                isempty = pd.isnull(resource_df.iloc[res_index,assoc_node_index].item())

                # Empty or NaN should return True, so if is empty can add the list
                if isempty == True:
                   # print("Is the cell empty?", isempty)
                    emptylist = []
                    emptylist.append(newrelationval)
                    resource_df.iloc[res_index,assoc_node_index] = str(emptylist)

                # If the cell is already populated (needs a second relation adding)
                elif isempty == False:
                   # print("Is the cell empty?", isempty)
                    existing = (resource_df.iloc[res_index,assoc_node_index].item()) # Str of existing data

                    # Remove trailing "]"
                    existing_strp = existing.rstrip("]")
                    # Add a comma and the new relation data then end with a ]
                    additional = existing_strp + (", %s]" % (newrelationval)) 

                    resource_df.iloc[res_index,assoc_node_index] = str(additional)   
            

# Pandas converts names of duplicate columns into +".1"
# Use this code to prevent that from occurring ensuring correct mapping
colMap = []

for col in resource_df.columns:
    if col.rpartition('.')[0]:
        colName = col.rpartition('.')[0]
        inMap = col.rpartition('.')[0] in colMap
        lastIsNum = col.rpartition('.')[-1].isdigit()
        dupeCount = colMap.count(colName)

        if inMap and lastIsNum and (int(col.rpartition('.')[-1]) == dupeCount):
            colMap.append(colName)
            continue
    colMap.append(col)
        
resource_df.columns = colMap  


# Write output to CSV
resource_df.to_csv(('%s.csv' % (final_name)), index=False)
print("CSV Written")
