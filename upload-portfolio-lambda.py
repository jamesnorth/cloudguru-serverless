import os
import boto3
import mimetypes
from io import BytesIO
from zipfile import ZipFile

def build_portfolio(bucket_name, object_key):
    s3 = boto3.resource('s3')

    print('Building from {} with {}'.format(bucket_name, object_key))

    portfolio_bucket = s3.Bucket('portfolio.jrnlabs.co.uk')
    build_bucket = s3.Bucket(bucket_name)

    portfolio_zip = BytesIO()
    build_bucket.download_fileobj(object_key, portfolio_zip)

    with ZipFile(portfolio_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            if os.path.splitext(nm)[1] == '.map':
                arg = {'ContentType': 'application/json'}
            else:
                args = {'ContentType': mimetypes.guess_type(nm)[0]}
            portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs=args)
            portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

def lambda_handler(event, context):
    job = event.get('CodePipeline.job')

    location = {
        'bucketName': 'portfoliobuild.jrnlabs.co.uk',
        'objectKey': 'portfoliobuild.zip'
    }

    if job is not None:
        for artifact in job['data']['inputArtifacts']:
            if artifact['name'] == 'MyAppBuild':
                location = artifact['location']['s3Location']
        code_pipeline = boto3.client('codepipeline')
    else:
        code_pipeline = None

    try:
        build_portfolio(location['bucketName'], location['objectKey'])

        if code_pipeline is not None:
            code_pipeline.put_job_success_result(jobId=job['id'])
    except:
        pass

    print("Job Done!")

    return 'Hello from Lambda'
