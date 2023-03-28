import requests
import json
from request_data import DATA_DEFAULT, HEADERS

old_i = 30
for i in range(31, 60):
    DATA_DEFAULT['fabrik___filter[list_99_com_fabrik_99][value][1]'] = "M"
    DATA_DEFAULT['limit99'] = i * 500
    DATA_DEFAULT['limitstart99'] = old_i * 500
    male_players_request = requests.post(
        'https://results.ittf.link/index.php?option=com_fabrik&view=list&listid=99&Itemid=266&resetfilters=0&clearordering=0&clearfilters=0',
        headers=HEADERS,
        data=DATA_DEFAULT)
    jsonString = json.dumps(male_players_request.text)
    file_name = 'male_players_part' + str(i) + '.json' 
    jsonFile = open(file_name, "w")
    jsonFile.write(jsonString)
    jsonFile.close()

old_i = 0
for i in range(1, 50):
    DATA_DEFAULT['fabrik___filter[list_99_com_fabrik_99][value][1]'] = "W"
    DATA_DEFAULT['limit99'] = i * 500
    DATA_DEFAULT['limitstart99'] = old_i * 500
    female_players_request = requests.post(
        'https://results.ittf.link/index.php?option=com_fabrik&view=list&listid=99&Itemid=266&resetfilters=0&clearordering=0&clearfilters=0',
        headers=HEADERS,
        data=DATA_DEFAULT)
    jsonString = json.dumps(female_players_request.text)
    file_name = 'female_players_part' + str(i) + '.json' 
    jsonFile = open(file_name, "w")
    jsonFile.write(jsonString)
    jsonFile.close()
