import boto3
import sys

__all__ = ['help_string', 'prepare', 'process', 'print_prepare_message', 'print_report']

priority = 1 # The driver execution priority (drivers are processed from lowest to highest value)

_name = "sfn"
_description = "Step functions"

def help_string():
    whitespace_len = 25-len(_name)
    return "  --%s%s%s" % (_name, ' '*whitespace_len, _description)

def prepare(include, exclude):
    client = boto3.client('stepfunctions');
    out = list_state_machines(client, include, exclude)
    return out

def process(state_machines_list, dry_run=True):
    out = []
    client = boto3.client('stepfunctions')
    for state_machine in state_machines_list:
        out.append(remove_state_machine(client, state_machine, dry_run))
    return out

def print_prepare_message(resources_list):
    if resources_list:
        print("%s:" % (_description))
        for obj in resources_list:
            print("  %s (%s)" % (obj['Name'], obj['Arn']))
    return True

def print_report(report):
    if report:
        print("%s:" % (_description))
        for obj in report:
            if (obj['Reason']):
                result_string = "%s (%s)" % (obj['Result'], obj['Reason'])
            else:
                result_string = obj['Result']
            print("  %s (%s) - %s" % (obj['Name'], obj['Arn'], result_string))
    return True

# TODO: implement continuation token usage (to process more than 1000 objects)
def list_state_machines(client, include, exclude):
    "This function returns list of Step function state machines matching include and exclude patterns"
    out = []

    if len(include) == 0 and len(exclude) == 0:
        return out

    response = client.list_state_machines(
        maxResults=1000
    )

    for state_machine in response['stateMachines']:
        if len(include) > 0 and len(exclude) > 0:
            if state_machine['name'].find(include) != -1 and state_machine['name'].find(exclude) == -1:
                out.append({
                    'Name': state_machine['name'],
                    'Arn': state_machine['stateMachineArn']
                })
        elif len(include) > 0 and state_machine['name'].find(include) != -1:
            out.append({
                'Name': state_machine['name'],
                'Arn': state_machine['stateMachineArn']
            })
        elif len(exclude) > 0 and state_machine['name'].find(exclude) == -1:
            out.append({
                'Name': state_machine['name'],
                'Arn': state_machine['stateMachineArn']
            })
    return out

def remove_state_machine(client, state_machine, dry_run=True):
    "This function removes Step function state machine or emulates removal if global dry_run_flag is set to True"
    out = {}
    out['Name'] = state_machine['Name']
    out['Arn'] = state_machine['Arn']
    out['Type'] = _name
    out['Reason'] = ''

    print(state_machine)
    
    if dry_run:
        out['Result'] = "dryrun_success"
    else:
        try:
            client.delete_state_machine(
                stateMachineArn=state_machine['Arn']
            )
        except Exception as e:
            out['Result'] = "error"
            out['Reason'] = e.__class__
        else: 
            out['Result'] = "success"

    return(out)

if __name__ == "__main__":
    sys.exit()

