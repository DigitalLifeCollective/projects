from kinto_http import Client
import json
import os

# import subprocess

username = os.environ['KINTO_USER']
password = os.environ['KINTO_PASSWORD']
server_url = os.environ['KINTO_URL']
map_id = os.environ['MAP_ID']

cwd = os.getcwd()

print(cwd)

# pull the files from kinto and format the fields

def getmap(collection_id):
    processed_projects_list = []

    for file in os.listdir("projects"):
        if file.endswith(".json"):
            file = os.path.join("projects", file)
            with open(file) as json_data:
                d = json.load(json_data)
                processed_projects_list.append(d['id'])


    auth = (username, password)
    client = Client(server_url=server_url, auth=auth)
    try:
        records = client.get_records(bucket='formdata', collection=collection_id)
    except:
        return 'There was a problem getting the information from kinto'

    for record in records:
        if record['id'] in processed_projects_list:
            continue
        else:
            label = record['label']
            print(f'Processing JSON file for: {label}')
            record['element type'] = "Project"
            tagline = record['tag line']
            description1 = record['Description1']
            description2 = record['Description2']
            video = record['video src']
            markdown = f'#{tagline}\n##About {label}\n![About {label}]({video})\n ###{description1}\n{description2}'
            record['description'] = markdown

            stack_list = []
            if 'Stack' in record:
                if isinstance(record['Stack'], (list,)):
                    for value in record['Stack']:
                        stack_list.append(remove_parens(value))
                else:
                    stack_list.append(remove_parens(record['Stack']))

                record['Stack'] = stack_list

            network_list = []
            if 'Network Topology' in record:
                if isinstance(record['Network Topology'], (list,)):
                    for value in record['Network Topology']:
                        network_list.append(remove_parens(value))
                else:
                    network_list.append(remove_parens(record['Network Topology']))
                record['Network Topology'] = network_list

            # these are fileds that have comma sep strings entered by the users
            string_fields = ['Tags', 'Suggested Groups', 'Relies On', 'Suggested Areas of Work', 'Regional Traction',
                             'Suggested Values', 'Additions']

            for key in string_fields:
                record[key] = string_to_list(data_dict=record, key=key, delimiter=',')

            # remove contact and email for privacy
            del record['contact email']
            del record['map contact']

            # write out the files
            with open(f'projects/{label}.json', 'w') as outfile:
                json.dump(record, outfile)

    make_map_json()
    return "All files processed"


def make_map_json():
    path = 'projects'
    project_list = []
    output_dict = {}

    jsonfile_list = [f for f in os.listdir(path)]

    print(jsonfile_list)

    for file in jsonfile_list:
        file_path = f'{path}/{file}'
        file = json.load(open(file_path))
        project_list.append(file)
        #print(file['label'])

    output_dict['elements'] = project_list
    output_file = 'docs/digitallifecollective.json'
    with open(output_file, 'w') as f:
        json.dump(output_dict, f)
        print("writing file")


def remove_parens(text_string):
    return text_string.split("(", maxsplit=1)[0].strip()


def string_to_list(data_dict, key, delimiter):
    if ',' in data_dict[key]:
        text_string = data_dict[key]
        text_string = text_string.replace(" ", "")
        new_list = text_string.split(delimiter)

        return new_list
    else:
        return data_dict[key]


a = getmap(map_id)
print(a)
