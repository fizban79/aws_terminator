import boto3
import sys

__all__ = ['priority', 'help_string', 'prepare', 'process', 'print_prepare_message', 'print_report']

priority = 1 # The driver execution priority (drivers are processed from lowest to highest value).

_name = "apigateway"
_description = "API gateways"

def help_string():
    whitespace_len = 25-len(_name)
    return "  --%s%s%s" % (_name, ' '*whitespace_len, _description)

def prepare(include, exclude):
    client = boto3.client(_name);
    out = list_resources(client, include, exclude)
    return out

def process(resources_list, dry_run=True):
    out = []
    client = boto3.client(_name)
    for resource in resources_list:
        out.append(remove_resource(client, resource, dry_run))
    return out

def print_prepare_message(resources_list):
    if resources_list:
        print("%s:" % (_description))
        for obj in resources_list:
            print("  %s (%s)" % (obj['Name'], obj['Id']))
    return True

def print_report(report):
    if report:
        print("%s:" % (_description))
        for obj in report:
            if (obj['Reason']):
                result_string = "%s (%s)" % (obj['Result'], obj['Reason'])
            else:
                result_string = obj['Result']
            print("  %s (%s) - %s" % (obj['Name'], obj['Id'], result_string))
    return True

# TODO: implement continuation token usage (to process more than 500 objects)
def list_resources(client, include, exclude):
    "This function returns list of resources matching include and exclude patterns"
    out = []

    if len(include) == 0 and len(exclude) == 0:
        return out

    response = client.get_rest_apis(
        limit=500
    )

    for res in response['items']:
        if len(include) > 0 and len(exclude) > 0:
            if res['name'].find(include) != -1 and res['name'].find(exclude) == -1:
                out.append({'Name': res['name'], 'Id': res['id']})
        elif len(include) > 0 and res['name'].find(include) != -1:
            out.append({'Name': res['name'], 'Id': res['id']})
        elif len(exclude) > 0 and res['name'].find(exclude) == -1:
            out.append({'Name': res['name'], 'Id': res['id']})
    return out

def remove_resource(client, res, dry_run=True):
    "This function removes Glue db or emulates removal if global dry_run_flag is set to True"
    out = {}
    out['Name'] = res['Name']
    out['Id'] = res['Id']
    out['Type'] = _name
    out['Reason'] = ''
    
    if dry_run:
        out['Result'] = "dryrun_success"
    else:
        try:
            client.delete_rest_api(
                restApiId = res['Id']
            )
        except Exception as e:
            out['Result'] = "error"
            out['Reason'] = e.__class__
        else: 
            out['Result'] = "success"

    return(out)

if __name__ == "__main__":
    sys.exit()

