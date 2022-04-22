# get_user_saved_addresses

------------------- WHAT THIS PROGRAM DOES -------------------

When a user signs in we want to be able to show them all of their saved homes. With that in mind, Laravel is going to be saving the Address_Ids that the user saves, and will then call this function, pass it the user_id and the list of addresses, and will expect to get back cached reports for each of them. Note, if the user has created their own version of an address (as in signed-in and inputting data into the form), this function will return the latest version of their personalized address report. For the ones in which they have not provided data, the function returns the baseline reports. 

------------------- WHAT FILE ACTS AS THE CONTROLLER -------------------

lambda_handler.py

------------------- STEPS IN THE PROCESS -------------------

All steps are run in the lambda_handler.py file

Step #1: Capture the inputs to the function

Step #2: Add the user saved addresses record

Step #3: Create an output object for the function 

Step #4: Create an object that will store the initial keys/vales that will be sent to Dynamo.

Step #5: First we search all addresses, with the user_id, to return the personalized reports where they exist. So we need to create the keys for Dynamo to search. 

Step #6: Add these personalized reports to the output object

Step #7: We then need to do the same exercise of preping the remaining addresses for batch search to get baselines

Step #8: We now add the baseline reports we collected to the output object, so they are all in a singular place

Step #9: Return the now complete object

------------------- OTHER FILES -------------------

create_cached_home_samples.py --> This file lets you create a sample set of cached reports that can be searched through. This was for local testing. 