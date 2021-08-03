import boto3
import json
from dateutil import parser

def main(aws_access_key, aws_secret_key):
    aws_regions = ['us-east-1','us-east-2','us-west-1','us-west-2','ap-northeast-2','ap-southeast-1','ap-southeast-2','ap-northeast-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-north-1','sa-east-1']
    ami_owners = {'kali*':'679593333241', 'debian*':'136693071363', 'ubuntu*':'099720109477'}
    new_amis = {}
    
    print('Updating image IDs may take some time, please be patient!')
    for name in ami_owners:
        print('Updating image IDs for ' + name[:-1])
        for region in aws_regions:
            ami = get_amis(region, ami_owners[name], name, aws_access_key, aws_secret_key)
            new_amis.update({f'{region}-{name[:-1]}': ami})

    update(new_amis)

def get_amis(region, owner, name, aws_access_key, aws_secret_key):
    ec2_client=boto3.client('ec2', region_name=region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    
    filters = [ {
        'Name': 'name',
        'Values': [name]
    },
    {
        'Name': 'owner-id',
        'Values': [owner]
    },{
        'Name': 'state',
        'Values': ['available']
    } ]

    amis = ec2_client.describe_images(Owners=[owner], Filters=filters)
    return latest_amis(amis['Images'])['ImageId']

def latest_amis(list_of_images):
    latest = None
    
    for image in list_of_images:
        if not latest:
            latest = image
            continue
        
        try:
            if parser.parse(image['CreationDate']) > parser.parse(latest['CreationDate']):
                latest = image
        except(ParserError):
            continue
    
    return latest

def update(new_amis):
    with open('config/config.json') as filehandle:
        json_data = json.load(filehandle)
    
    json_data['aws']['amis'] = new_amis

    with open('config/config.json', 'w') as filehandle:
        filehandle.write(json.dumps(json_data, indent=4)) 
    
    print("AMIs updated in config.json")

if __name__ == '__main__':
    main()
