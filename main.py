import os
import requests
import shutil
from datetime import datetime
import subprocess
import win32gui
import win32con
import zipfile
import autoDownload
import psutil
import hashlib
import os


hosts_file_path = os.path.join(os.environ['SystemRoot'], 'System32', 'drivers', 'etc', 'hosts')
backup_folder_path = os.path.join(os.getcwd(), 'hosts_backup')
url = 'https://raw.hellogithub.com/hosts'
fastgithub_download_url = 'https://download.nuaa.cf/dotnetcore/FastGithub/releases/download/2.1.4/fastgithub_win-x64.zip'
fastgithub_zip_path = os.path.join(os.getcwd(), 'fastgithub.zip')
fastgithub_folder_path = os.path.join(os.getcwd(), 'fastgithub')

# 使用 psutil 来查看进程
def is_process_running(name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == name:
            return True
    return False

# 将窗口置顶
def set_foreground_window(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    win32gui.SetForegroundWindow(hwnd)

# 备份 hosts 文件
def backup_hosts():
    if not os.path.exists(backup_folder_path):
        os.mkdir(backup_folder_path)
    backup_file_name = 'hosts_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.txt'
    backup_file_path = os.path.join(backup_folder_path, backup_file_name)
    shutil.copy2(hosts_file_path, backup_file_path)
    print('已备份 hosts 文件到', backup_file_path)
    hwnd = win32gui.GetForegroundWindow()
    set_foreground_window(hwnd)
    subprocess.call(['explorer', '/select,', backup_file_path])
    hwnd = win32gui.GetForegroundWindow()
    set_foreground_window(hwnd)

# 恢复 hosts 文件
def restore_hosts():
    backup_file_names = []
    for file_name in os.listdir(backup_folder_path):
        if file_name.startswith('hosts_backup'):
            backup_file_names.append(file_name)
    if len(backup_file_names) == 0:
        print('未找到备份文件')
        return
    backup_file_names.sort(reverse=True)
    for i, file_name in enumerate(backup_file_names):
        print(i + 1, file_name)
    choice = input('请选择要恢复的备份文件：')
    try:
        choice = int(choice)
    except ValueError:
        print('无效的选择')
        return
    if choice < 1 or choice > len(backup_file_names):
        print('无效的选择')
        return
    backup_file_path = os.path.join(backup_folder_path, backup_file_names[choice-1])
    shutil.copy2(backup_file_path, hosts_file_path)
    print('已恢复 hosts 文件')
    os.system('ipconfig /flushdns')
    hwnd = win32gui.GetForegroundWindow()
    set_foreground_window(hwnd)

# 更新 hosts 文件
def update_hosts():
    response = requests.get(url)
    with open(hosts_file_path, 'w') as f:
        f.write(response.content.decode('utf-8'))
    print('已更新 hosts 文件')
    os.system('ipconfig /flushdns')
    hwnd = win32gui.GetForegroundWindow()
    set_foreground_window(hwnd)

# 清空备份
def clear_backup():
    if os.path.exists(backup_folder_path):
        shutil.rmtree(backup_folder_path)
        print('已清空备份')
    else:
        print('未找到备份文件夹')

# 下载 fastgithub
def download_fastgithub():
    autoDownload.AutoDownload(fastgithub_download_url, fastgithub_zip_path).start()
    with zipfile.ZipFile(fastgithub_zip_path, 'r') as zip_ref:
        zip_ref.extractall(fastgithub_folder_path)
    print('已下载 fastgithub')

# 运行 fastgithub
def run_fastgithub():
    fastgithub_exe_path = os.path.join(fastgithub_folder_path, 'fastgithub_win-x64' ,'FastGithub.UI.exe')
    if os.path.exists(fastgithub_exe_path):
        subprocess.Popen(fastgithub_exe_path)
        print('正在启动 fastgithub...')
    else:
        print('未找到 FastGithub.UI.exe，请先下载')

# 计算文件的 MD5
def calculate_folder_md5(folder_path):
    md5 = hashlib.md5()

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(8192)
                    if not data:
                        break
                    md5.update(data)

    return md5.hexdigest()

while True:
    print('1. 备份 hosts 文件\n2. 恢复 hosts 文件\n3. 更新 hosts 文件\n4. 清空备份\n5. 下载 fastgithub 最新版本并运行\n6. 退出程序')
    choice = input('请选择功能（输入数字）：')
    try:
        choice = int(choice)
    except ValueError:
        print('无效的选择')
        continue
    if choice == 1:
        backup_hosts()
    elif choice == 2:
        restore_hosts()
    elif choice == 3:
        update_hosts()
    elif choice == 4:
        clear_backup()
    elif choice == 5:
        md5 = calculate_folder_md5(fastgithub_folder_path)
        print(md5)
        if md5 == 'cffc7ddb90f0912fa77f898165f3c5ef':
            if is_process_running('FastGithub.UI.exe'):
                print('\033[91m' + 'FastGithub.UI.exe 正在运行' + '\033[0m')
                continue
            else:
                download_fastgithub()
                run_fastgithub()
        
    elif choice == 6:
        print('bye!')
        break
    else:
        print('无效的选择')

