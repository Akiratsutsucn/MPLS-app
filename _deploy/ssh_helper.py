import paramiko
import sys

def ssh_exec(cmd, print_output=True):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('192.168.100.150', port=22, username='root', password='P@ssw0rd@2026', timeout=10)
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    client.close()
    if print_output:
        if out.strip():
            print(out.strip())
        if err.strip():
            print(f"[STDERR] {err.strip()}")
        print(f"[EXIT: {exit_code}]")
    return out, err, exit_code

if __name__ == '__main__':
    cmd = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'echo hello'
    ssh_exec(cmd)
