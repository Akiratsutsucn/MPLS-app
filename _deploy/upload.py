import paramiko
import os
import stat

def upload_dir(local_path, remote_path, host='192.168.100.150', port=22, user='root', password='P@ssw0rd@2026'):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=user, password=password, timeout=10)
    sftp = client.open_sftp()

    # Ensure remote base dir exists
    _mkdir_p(sftp, remote_path)

    skip_dirs = {'node_modules', '.git', '__pycache__', 'dist', 'venv', '.venv', 'uploads', '_deploy'}

    count = 0
    for root, dirs, files in os.walk(local_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        rel = os.path.relpath(root, local_path).replace('\\', '/')
        remote_dir = f"{remote_path}/{rel}" if rel != '.' else remote_path

        _mkdir_p(sftp, remote_dir)

        for f in files:
            local_file = os.path.join(root, f)
            remote_file = f"{remote_dir}/{f}"
            sftp.put(local_file, remote_file)
            count += 1

    sftp.close()
    client.close()
    print(f"Uploaded {count} files to {host}:{remote_path}")

def _mkdir_p(sftp, remote_dir):
    dirs_to_create = []
    current = remote_dir
    while True:
        try:
            sftp.stat(current)
            break
        except FileNotFoundError:
            dirs_to_create.append(current)
            current = os.path.dirname(current)
            if current == '/' or current == '':
                break
    for d in reversed(dirs_to_create):
        sftp.mkdir(d)

if __name__ == '__main__':
    upload_dir(
        local_path=r'D:\WorkSpace\Claude\mlps-pm',
        remote_path='/opt/mlps-pm'
    )
