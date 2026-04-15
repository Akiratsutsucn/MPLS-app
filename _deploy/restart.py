import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.100.150', port=22, username='root', password='P@ssw0rd@2026', timeout=10)
sftp = client.open_sftp()
sftp.put(r'D:\WorkSpace\Claude\mlps-pm\docker-compose.yml', '/opt/mlps-pm/docker-compose.yml')
sftp.close()
print("Uploaded docker-compose.yml")

stdin, stdout, stderr = client.exec_command('cd /opt/mlps-pm && docker compose down && docker compose up -d 2>&1', timeout=120)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
code = stdout.channel.recv_exit_status()
client.close()
print(out)
if err.strip(): print(f"[STDERR] {err}")
print(f"[EXIT: {code}]")
