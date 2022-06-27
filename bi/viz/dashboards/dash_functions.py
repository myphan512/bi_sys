######## DASH FUNCTIONS FILES
""" To predefine graphing functions that can be reusable in every dashboard.
"""

### DROPDOWN FILTERS
""" Function to create options list for drop down filter:
Format: [{'label':abc, 'value':xyz}, ] (due to version dash-core-components 1.17.1)
Arguments: a list of items to be displayed in dropdown
Return: a list of dictionaries
"""
def dropdown_filters(list):
    list_dict = []
    for item in list:
        list_dict.append({'label': item, 'value': item})
    return list_dict