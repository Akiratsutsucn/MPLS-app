import paramiko

def upload_file(local_path, remote_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('192.168.100.150', port=22, username='root', password='P@ssw0rd@2026', timeout=10)
    sftp = client.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    client.close()
    print(f"Uploaded {local_path} -> {remote_path}")

if __name__ == '__main__':
    upload_file(r'D:\WorkSpace\Claude\mlps-pm\backend\Dockerfile', '/opt/mlps-pm/backend/Dockerfile')
    upload_file(r'D:\WorkSpace\Claude\mlps-pm\frontend\Dockerfile', '/opt/mlps-pm/frontend/Dockerfile')
