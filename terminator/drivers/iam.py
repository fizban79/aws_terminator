import boto3
import sys

__all__ = ['help_string', 'prepare', 'process', 'print_prepare_message', 'print_report']

priority = 100 # The driver execution priority (drivers are processed from lowest to highest value)

_name = "iam"
_description = "IAM Roles and Policies"

def help_string():
    whitespace_len = 25-len(_name)
    return "  --%s%s%s" % (_name, ' '*whitespace_len, _description)

def prepare(include, exclude):
    client = boto3.client(_name);
    out = list_resources(client, include, exclude)
    if not out['Roles'] and not out['Policies']:
        out = []
    return out

def process(resources_list, dry_run=True):
    out = {}
    out['Roles'] = []
    out['Policies'] = []

    client = boto3.client(_name)
    for resource in resources_list['Roles']:
        out['Roles'].append(remove_resource(client, 'iam_role', resource, dry_run))
    for resource in resources_list['Policies']:
        out['Policies'].append(remove_resource(client, 'iam_policy', resource, dry_run))

    return out

def print_prepare_message(resources_list):
    if not resources_list:
        return True
    if resources_list['Roles']:
        print("IAM Roles:")
        for obj in resources_list['Roles']:
            print("  %s (%s)" % (obj['Name'], obj['Arn']))
    if resources_list['Policies']:
        print("IAM Policies:")
        for obj in resources_list['Policies']:
            print("  %s (%s)" % (obj['Name'], obj['Arn']))
    return True

def print_report(report):
    if not report:
        return True
    if report['Roles']:
        print("IAM Roles:")
        for obj in report['Roles']:
            if (obj['Reason']):
                result_string = "%s (%s)" % (obj['Result'], obj['Reason'])
            else:
                result_string = obj['Result']
            print("  %s (%s) - %s" % (obj['Name'], obj['Arn'], result_string))
    if report['Policies']:
        print("IAM Policies:")
        for obj in report['Policies']:
            if (obj['Reason']):
                result_string = "%s (%s)" % (obj['Result'], obj['Reason'])
            else:
                result_string = obj['Result']
            print("  %s (%s) - %s" % (obj['Name'], obj['Arn'], result_string))
    return True

# TODO: implement continuation token usage (to process more than 1000 objects)
def list_resources(client, include, exclude):
    "This function returns list of resources matching include and exclude patterns"
    out = {}
    out['Roles'] = []
    out['Policies'] = []

    if len(include) == 0 and len(exclude) == 0:
        return out
    
    finished = False
    next_token = ''
    while not finished:
        if not next_token:
            response = client.list_roles(
                MaxItems=1000
            )
        else:
            response = client.list_roles(
                MaxItems=1000,
                Marker=next_token
            )

        if not response['IsTruncated']:
            finished = True
        else:
            next_token = response['Marker']

        for res in response['Roles']:
            if len(include) > 0 and len(exclude) > 0:
                if res['RoleName'].find(include) != -1 and res['RoleName'].find(exclude) == -1:
                    out['Roles'].append({'Name': res['RoleName'], 'Arn': res['Arn']})
            elif len(include) > 0 and res['RoleName'].find(include) != -1:
                out['Roles'].append({'Name': res['RoleName'], 'Arn': res['Arn']})
            elif len(exclude) > 0 and res['RoleName'].find(exclude) == -1:
                out['Roles'].append({'Name': res['RoleName'], 'Arn': res['Arn']})

    finished = False
    next_token = ''
    while not finished:
        if not next_token:
            response = client.list_policies(
                Scope='Local',
                MaxItems=1000
            )
        else:
            response = client.list_policies(
                Scope='Local',
                MaxItems=1000,
                Marker=next_token
            )

        if not response['IsTruncated']:
            finished = True
        else:
            next_token = response['Marker']

        for res in response['Policies']:
            if len(include) > 0 and len(exclude) > 0:
                if res['PolicyName'].find(include) != -1 and res['PolicyName'].find(exclude) == -1:
                    out['Policies'].append({'Name': res['PolicyName'], 'Arn': res['Arn']})
            elif len(include) > 0 and res['PolicyName'].find(include) != -1:
                out['Policies'].append({'Name': res['PolicyName'], 'Arn': res['Arn']})
            elif len(exclude) > 0 and res['PolicyName'].find(exclude) == -1:
                out['Policies'].append({'Name': res['PolicyName'], 'Arn': res['Arn']})
    return out

def remove_resource(client, res_type, res, dry_run=True):
    "This function removes Glue db or emulates removal if global dry_run_flag is set to True"
    out = {}
    out['Name'] = res['Name']
    out['Arn'] = res['Arn']
    out['Type'] = res_type
    out['Reason'] = ''
    
    if dry_run:
        out['Result'] = "dryrun_success"
    else:
        try:
            if res_type == 'iam_role':
                response = client.list_attached_role_policies(
                    RoleName=res['Name']
                )
                for att in response['AttachedPolicies']:
                    client.detach_role_policy(
                        RoleName=res['Name'],
                        PolicyArn=att['PolicyArn']
                    )
                client.delete_role(
                    RoleName=res['Name']
                )
            elif res_type == 'iam_policy':
                client.delete_policy(
                    PolicyArn=res['Arn']
                )
            else:
                out['Result'] = "error"
                out['Reason'] = "Unknown resource type"
        except Exception as e:
            out['Result'] = "error"
            out['Reason'] = str(e)
        else: 
            out['Result'] = "success"
    return(out)

if __name__ == "__main__":
    sys.exit()

