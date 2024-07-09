import urllib.parse

def upload_csv_to_s3(s3_client, bucket_name, group_number, csv_content):
    file_key = f"group_{group_number}.csv"
    s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=csv_content)
    encoded_file_key = urllib.parse.quote(file_key, safe='')
    url = f"https://{bucket_name}.s3.{config.REGION_NAME}.amazonaws.com/{encoded_file_key}"
    return url
