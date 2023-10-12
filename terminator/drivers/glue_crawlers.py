import boto3
import sys

__all__ = ['help_string', 'prepare', 'process', 'print_prepare_message', 'print_report']

priority = 3 # The driver execution priority (drivers are processed from lowest to highest value)

_name = "glue_crawlers"
_description = "Glue crawlers"

def help_string():
    whitespace_len = 25-len(_name)
    return "  --%s%s%s" % (_name, ' '*whitespace_len, _description)

def info():
    return {
        "Name": _name,
        "Description": "Glue crawlers"
    }

def prepare(include, exclude):
    client = boto3.client('glue');
    out = list_crawlers(client, include, exclude)
    return out

def process(crawlers_list, dry_run=True):
    out = []
    client = boto3.client('glue')
    for crawler in crawlers_list:
        out.append(remove_crawler(client, crawler, dry_run))
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

# TODO: implement continuation token usage (to process more than 1000 objects)
def list_crawlers(client, include, exclude):
    "This function returns list of Glue crawlers matching include and exclude patterns"
    out = []

    if len(include) == 0 and len(exclude) == 0:
        return out

    response = client.get_crawlers(
        MaxResults=1000
    )

    for crawler in response['Crawlers']:
        if len(include) > 0 and len(exclude) > 0:
            if crawler['Name'].find(include) != -1 and crawler['Name'].find(exclude) == -1:
                out.append(crawler['Name'])
        elif len(include) > 0 and crawler['Name'].find(include) != -1:
            out.append(crawler['Name'])
        elif len(exclude) > 0 and crawler['Name'].find(exclude) == -1:
            out.append(crawler['Name'])
    return out

def remove_crawler(client, crawler, dry_run=True):
    "This function removes Glue crawler or emulates removal if global dry_run_flag is set to True"
    out = {}
    out['Name'] = crawler
    out['Type'] = _name
    out['Reason'] = ''
    
    if dry_run:
        out['Result'] = "dryrun_success"
    else:
        try:
            client.delete_crawler(
                Name=crawler
            )
        except Exception as e:
            out['Result'] = "error"
            out['Reason'] = e.__class__
        else: 
            out['Result'] = "success"

    return(out)

if __name__ == "__main__":
    sys.exit()

