import json
import boto3
# import random
import datetime 

def get_user_saved_addresses(input_object_raw,context):
	
	# Capture the inputs to the function
	input_object = input_object_raw
	user_id = input_object['user_id']
	saved_addresses_master = list(input_object['saved_addresses']) # We want this so we can have a copy to refer back to
	saved_addresses_original = list(input_object['saved_addresses']) # This is what we will start working against

	saved_addresses = list(set(saved_addresses_original))

	timestamp = str(datetime.datetime.now())

	# Connect to Dynamodb and create table for batch get

	# dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8001')
	dynamodb = boto3.resource('dynamodb')
	cached_homes = dynamodb.Table('Cached_Home_Analysis_Reports')
	user_saved_addresses_table = dynamodb.Table('User_Saved_Addresses')

	# Add the user saved addresses record
	
	user_saved_addresses_object = {
		"User_Id": user_id,
		"Timestamp": timestamp,
		"Saved_Addresses": saved_addresses_master,
		"Number_of_Saved_Addresses": len(saved_addresses_master)
	}
	
	user_saved_addresses_table.put_item(Item=user_saved_addresses_object)

	#Create an output object for the function 

	output_object = {
		"user_id": user_id,
		"user_saved_addresses": saved_addresses_master,
		"number_of_saved_addresses": str(len(saved_addresses_master)),
		"returned_reports": [],
		"missing_reports": [],
		'timestamp': timestamp
	}
	

	# Create an object that will store the initial keys/vales that will be sent to Dynamo. 
	parpared_initial_homes = []

	# First we search all addresses, with the user_id, to return the personalized reports where they exist. So we need to create the keys for Dynamo to search. 

	for item in saved_addresses:
		parpared_initial_homes.append({"Address_Id": item, "User_Id":user_id})

	# Do a batch search of Dynamo to return those reports
	user_personalized_search = dynamodb.batch_get_item(RequestItems={
		'Cached_Home_Analysis_Reports':{
		'Keys': parpared_initial_homes
			}
		}
		)

	# Add these personalized reports to the output object
	
	output_object['returned_reports'] = user_personalized_search['Responses']['Cached_Home_Analysis_Reports']
	
	# Next we need to figure out which homes we need to go back to get the Quoll baseline for, so we look through that list we just added to the output object, look at the address id for each, and remove that from our initial list. 
	
	for i in output_object['returned_reports']:
		saved_addresses.remove(i['Address_Id'])


	# We then need to do the same exercise of preping the remaining addresses for batch search to get baselines
	prepared_second_search_homes = []

	for i in saved_addresses:
		prepared_second_search_homes.append({"Address_Id": i, "User_Id":"Quoll"})

	user_baseline_search = dynamodb.batch_get_item(RequestItems={
		'Cached_Home_Analysis_Reports':{
		'Keys': prepared_second_search_homes
			}
		}
		)
	
	# We now add the baseline reports we collected to the output object, so they are all in a singular place

	output_object['returned_reports'] = output_object['returned_reports'] + user_baseline_search['Responses']['Cached_Home_Analysis_Reports']
	output_object['number_of_returned_reports'] = str(len(output_object['returned_reports']))

	# Finally, as a last check, we remove the baseline address ids from the saved_addresses object and then add whatever may be left (hopefully nothing), from that original saved homes list
	for i in user_baseline_search['Responses']['Cached_Home_Analysis_Reports']:
		saved_addresses.remove(i['Address_Id'])

	# Return the now complete object 
	
	output_object['missing_reports'] = saved_addresses

	return output_object

# ---------------- TESTING ----------------

# test_get_homes = {
# 	"user_id": "5",
# 	"saved_addresses": ["90","40","27","81","22","65","76","77","77"]	
# }
# context = "test"

# x = get_user_saved_addresses(test_get_homes,context)
# print(x)
