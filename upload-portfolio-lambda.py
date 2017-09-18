import os
import boto3
import mimetypes
from io import BytesIO
from zipfile import ZipFile

s3 = boto3.resource('s3')

portfolio_bucket = s3.Bucket('portfolio.jrnlabs.co.uk')
build_bucket = s3.Bucket('portfoliobuild.jrnlabs.co.uk')

portfolio_zip = BytesIO()
build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

with ZipFile(portfolio_zip) as myzip:
    for nm in myzip.namelist():
        obj = myzip.open(nm)
        if os.path.splitext(nm)[1] == '.map':
            arg = {'ContentType': 'application/json'}
        else:
            args = {'ContentType': mimetypes.guess_type(nm)[0]}
        portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs=args)
        portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
