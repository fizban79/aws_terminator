import boto3
import sys

__all__ = ['help_string', 'prepare', 'process', 'print_prepare_message', 'print_report']

priority = 1 # The driver execution priority (drivers are processed from lowest to highest value)

_name = "ec2"
_description = "EC2 instances"

def help_string():
    whitespace_len = 25-len(_name)
    return "  --%s%s%s" % (_name, ' '*whitespace_len, _description)

def prepare(include, exclude):
    out = []
    client = boto3.client(_name);
    out = list_instances(client, include, exclude)
    return out

def process(instances_list, dry_run=True):
    out = []
    client = boto3.resource(_name)
    for instance in instances_list:
        out.append(remove_instance(client, instance, dry_run))
    return out

def print_prepare_message(instances_list):
    if instances_list:
        print("%s:" % (_description))
        for obj in instances_list:
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

def get_name_tag(instance):
    out = ''
    for tag in instance['Tags']:
        if tag['Key'] == 'Name':
            out = tag['Value']
            break
    return out

def list_instances(client, include, exclude):
    "This function returns list of EC2 instances matching include and exclude patterns"
    out = []
    if len(include) == 0 and len(exclude) == 0:
        return out
    elif len(include) == 0:
        include = '*'
    else:
        include = '*' + include + '*'

    response = client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    include,
                ]
            }
        ]
    )

    for reservation in response['Reservations']:
        name_tag = ''
        for instance in reservation['Instances']:
            name_tag = get_name_tag(instance)
            if len(exclude) > 0 and name_tag.find(exclude) != -1:
                continue
            if instance['State']['Name'] != 'terminated':
                out.append(
                    {
                        'Name': name_tag,
                        'Id': instance['InstanceId']
                    }
                )
                        
    return(out)

def remove_instance(client, instance, dry_run=True):
    "This function removes EC2 instance or emulates removal if global dry_run_flag is set to True"
    out = {}
    out['Id'] = instance['Id']
    out['Name'] = instance['Name']
    out['Type'] = _name
    out['Reason'] = ''
    

    instance = client.Instance(instance['Id'])

    try:
        instance.terminate(
            DryRun = dry_run
        )
    except Exception as e:
        if e.response['Error']['Code'] == 'DryRunOperation':
            out['Result'] = "dryrun_success"
        else:
            out['Result'] = "error"
            out['Reason'] = e.__class__
    else: 
        out['Result'] = "success"

    return(out)

if __name__ == "__main__":
    sys.exit()

