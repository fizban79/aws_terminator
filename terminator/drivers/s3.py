import boto3
import sys

__all__ = ['help_string', 'prepare', 'process', 'print_prepare_message', 'print_report']

priority = 10 # The driver execution priority (drivers are processed from lowest to highest value)

_name = "s3"
_description = "S3 Buckets"

def help_string():
    whitespace_len = 25-len(_name)
    return "  --%s%s%s" % (_name, ' '*whitespace_len, _description)

def prepare(include, exclude):
    out = []
    s3 = boto3.client('s3');
    out = list_buckets(s3, include, exclude)
    return out

def process(buckets_list, dry_run=True):
    out = []
    s3 = boto3.client('s3')
    for bucket in buckets_list:
        out.append(remove_bucket(s3, bucket, dry_run))
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

def list_buckets(client, include, exclude):
    "This function returns list of S3 buckets matching include and exclude patterns"
    out = []
    response = client.list_buckets()

    for bucket in response['Buckets']:
        if len(include) > 0 and len(exclude) > 0:
            if bucket['Name'].find(include) != -1 and bucket['Name'].find(exclude) == -1:
                out.append(bucket['Name'])
        elif len(include) > 0 and len(exclude) == 0:
            if bucket['Name'].find(include) != -1:
                out.append(bucket['Name'])
        elif len(include) == 0 and len(exclude) > 0:
            if bucket['Name'].find(exclude) == -1:
                out.append(bucket['Name'])
    return(out)

def remove_bucket(client, bucket, dry_run=True):
    "This function removes S3 bucket or emulates removal if global dry_run_flag is set to True"
    out = {}
    out['Name'] = bucket
    out['Type'] = _name
    out['Reason'] = ''
    if dry_run: 
        out['Result'] = "dryrun_success"
    else:
        try:
            client.delete_bucket(
                Bucket=bucket
            )
        except Exception as e:
            out['Result'] = "error"
            out['Reason'] = str(e)
#            out['Reason'] = e.__class__
        else: 
            out['Result'] = "success"
    return(out)

if __name__ == "__main__":
    sys.exit()
