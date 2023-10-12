import boto3
import sys

__all__ = ['help_string', 'prepare', 'process', 'print_prepare_message', 'print_report']

priority = 8 # The driver execution priority (drivers are processed from lowest to highest value)

_name = "dynamodb"
_description = "DynamoDB tables"

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
            print("  %s" % (obj))
    return True

def print_report(report):
    if report:
        print("%s:" % (_description))
        for obj in report:
            if (obj['Reason']):
                result_string = "%s (%s)" % (obj['Result'], obj['Reason'])
            else:
                result_string = obj['Result']
            print("  %s - %s" % (obj['Name'], result_string))
    return True

def list_resources(client, include, exclude):
    "This function returns list of resources matching include and exclude patterns"
    out = []

    if len(include) == 0 and len(exclude) == 0:
        return out
    
    finished = False
    last_table = '' 
    while not finished:
        if not last_table:
            response = client.list_tables(
                Limit = 100
            )
        else:
            response = client.list_tables(
                Limit = 100,
                ExclusiveStartTableName = last_table
            )
        if 'LastEvaluatedTableName' not in response.keys():
            finished = True
        else:
            last_table = response['LastEvaluatedTableName']

        for res in response['TableNames']:
            if len(include) > 0 and len(exclude) > 0:
                if res.find(include) != -1 and res.find(exclude) == -1:
                    out.append(res)
            elif len(include) > 0 and res.find(include) != -1:
                out.append(res)
            elif len(exclude) > 0 and res.find(exclude) == -1:
                out.append(res)
        return out

def remove_resource(client, res, dry_run=True):
    "This function removes resource or emulates removal if global dry_run_flag is set to True"
    out = {}
    out['Name'] = res
    out['Type'] = _name
    out['Reason'] = ''
    
    if dry_run:
        out['Result'] = "dryrun_success"
    else:
        try:
            client.delete_table(
                TableName=res
            )
        except Exception as e:
            out['Result'] = "error"
            out['Reason'] = e.__class__
        else: 
            out['Result'] = "success"

    return(out)

if __name__ == "__main__":
    sys.exit()

