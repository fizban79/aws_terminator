Description
-----------
This utility deletes AWS resources


Requirements
------------
* Python 3
* boto3 python module
* AWS CLI configured for appropriate AWS environment

Usage
-----
```
aws_terminator [OPTIONS...] [RESOURCE_TYPES...]

Available options:
  -h, --help                 Print the help message
  -i, --include <text>       Include resources with <text> substring in name
  -x, --exclude <text>       Exclude resources with <text> substring in name
  --dry-run                  Emulate resources deletion without actual removal
  --delete                   Actually delete the resources. Requires confirmation if any resources deleted

Available resource types:
  --all                      Process all available resource types
  --apigateway               API gateways
  --codebuild                CodeBuild Projects
  --dynamodb                 DynamoDB tables
  --ec2                      EC2 instances
  --glue_conn                Glue database connections
  --glue_crawlers            Glue crawlers
  --glue_db                  Glue databases
  --glue_jobs                Glue Jobs
  --iam                      IAM Roles and Policies
  --lambda                   Lambda Functions
  --s3                       S3 Buckets
  --sfn                      Step functions
```

### Notice
* At least one of -i (--include) or -x (--exclude) should be specified. In none specified, no resources will be processed
* Use -x (--exclude) option with care, it may lead to destroying all resources when used without -i (--include) option
* --dry-run and --delete options are mutually exclusive. If both specified, the dry run will be performed. If none, only preparation phase is being performed.

Examples
--------

### Show EC2 resources containing 'test' in name, excluding resources fith 'foo' in name
```
aws_terminator --include test --exclude foo --ec2
```

### Delete resources of all types containing 'test' in name
```
aws_terminator --include test --delete --all
```


### Emulate deletion of s3, ec2 and iam resources not containing 'test' in name
```
aws_terminator --exclude test --dry-run --s3 --ec2 --iam
```

