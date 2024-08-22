import logging
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv


class HelperS3(object):
    folder_name = 'test/'
    bucket_name = "myco-dubingai-bucket"

    @classmethod
    def aws_upload_file(cls,file_path, bucket, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        if object_name is None:
            object_name = os.path.basename(file_path)

        # Upload the file
        s3_client = boto3.client('s3')
        print('Uploading file to S3 @File Uploarder....')
        try:
            response = s3_client.upload_file(file_path, bucket, cls.folder_name + object_name)
            print(response)
        except ClientError as e:
            logging.error(e)
            return False
        return True



if __name__ == '__main__':
    #load_dotenv()
    HelperS3.folderName = 'testing/'
    HelperS3.aws_upload_file('output/1.mp4', 'myco-dubingai-bucket', 'test1.mp4')