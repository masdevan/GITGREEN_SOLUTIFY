import os
import json
import subprocess
from datetime import datetime
def auto_commit_and_push(log_func=None):
    # Pastikan working directory benar-benar bersih sebelum mulai
    try:
        for branch in branch_list:
            cmds_clean = [
                f'cd "{project_folder}"',
                'git stash --include-untracked',
                'git reset --hard',
                'git clean -fd',
                'git fetch --all',
                f'git checkout {branch}',
                f'git pull --rebase origin {branch}'
            ]
            clean_cmd = ' && '.join(cmds_clean)
            result_clean = subprocess.run(clean_cmd, shell=True, capture_output=True, text=True)
            if log_func:
                log_func(f"Membersihkan dan update branch {branch}...")
                log_func(result_clean.stdout)
                if result_clean.stderr:
                    log_func(result_clean.stderr)
    except Exception as e:
        if log_func:
            log_func(f"Gagal membersihkan repo: {e}")
    # Load settings
    with open('settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)

    project_folder = settings['project_folder']
    readme_path = os.path.join(project_folder, 'README.md')

    from datetime import timedelta
    import random
    from pathlib import Path

    commit_messages = settings['commit_messages'] if settings['commit_messages'] else ['auto commit']
    branch_list = settings['branch_names'] if settings['branch_names'] else ['main']
    allowed_extensions = settings.get('allowed_extensions', ['.php', '.js', '.py', '.txt', '.md'])
    excluded_folders = set(settings.get('excluded_folders', ['.git', 'node_modules', 'venv', '__pycache__']))
    push_per_day = int(settings.get('push_per_day', 1))
    start_date = datetime.strptime(settings['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(settings['end_date'], '%Y-%m-%d')


    # Validasi github_email dengan git config user.email
    try:
        result = subprocess.run(
            f'cd "{project_folder}" && git config user.email',
            shell=True, capture_output=True, text=True
        )
        git_email = result.stdout.strip()
        if git_email and git_email != settings['github_email']:
            if log_func:
                log_func(f"Peringatan: Email git config ({git_email}) berbeda dengan github_email di settings.json ({settings['github_email']})")
        elif not git_email:
            # Set git config user.email jika belum ada
            subprocess.run(f'cd "{project_folder}" && git config user.email "{settings["github_email"]}"', shell=True)
            if log_func:
                log_func(f"Set git user.email ke {settings['github_email']}")
    except Exception as e:
        if log_func:
            log_func(f"Gagal validasi/set git user.email: {e}")

    # Set git author name dan email
    author_name = settings.get('username', 'Auto Commit')
    author_email = settings.get('email', 'autocommit@example.com')

    # Pilih branch awal untuk inisialisasi (gunakan branch utama dari list)
    init_branch = branch_list[0]
    cmds_init = [
        f'cd "{project_folder}"',
        'git init',
        f'git config user.name "{author_name}"',
        f'git config user.email "{author_email}"',
        f'git checkout -B {init_branch}'
    ]
    subprocess.run(' && '.join(cmds_init), shell=True)

    # Backup semua file yang mungkin diubah
    file_backups = {}
    day = start_date
    while day <= end_date:
        for i in range(push_per_day):
            # Pilih branch acak
            branch = random.choice(branch_list)
            # Pilih file random selain README.md
            all_files = []
            for root, dirs, files in os.walk(project_folder):
                # Skip excluded folders
                dirs[:] = [d for d in dirs if d not in excluded_folders]
                for file in files:
                    if file.lower() == 'readme.md' or file.startswith('.'):
                        continue
                    ext = os.path.splitext(file)[1].lower()
                    if ext in allowed_extensions:
                        full_path = os.path.join(root, file)
                        all_files.append(full_path)
            if not all_files:
                if log_func:
                    log_func('No files found to modify (other than README.md).')
                return
            target_file = random.choice(all_files)
            if log_func:
                log_func(f'Randomly selected file: {target_file}')

            # Backup isi file (sekali saja per file)
            if target_file not in file_backups:
                try:
                    with open(target_file, 'r', encoding='utf-8') as f:
                        file_backups[target_file] = f.readlines()
                except Exception as e:
                    if log_func:
                        log_func(f'Failed to read {target_file}: {e}')
                    return

            original_lines = file_backups[target_file]

            # Commit 1: hapus 1/6 bagian
            n = len(original_lines)
            if n < 6:
                remove_count = 1
            else:
                remove_count = max(1, n // 6)
            # Simpan posisi dan isi baris yang dihapus
            remove_start = 0
            removed_lines = original_lines[remove_start:remove_start+remove_count]
            modified_lines = original_lines[:remove_start] + original_lines[remove_start+remove_count:]
            try:
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.writelines(modified_lines)
                if log_func:
                    log_func(f'Removed {remove_count} lines from {target_file} (posisi {remove_start})')
            except Exception as e:
                if log_func:
                    log_func(f'Failed to modify {target_file}: {e}')
                return

            commit_date = day.replace(hour=12, minute=0, second=0) + timedelta(minutes=i*2)
            env = os.environ.copy()
            env['GIT_AUTHOR_DATE'] = commit_date.strftime('%Y-%m-%dT%H:%M:%S')
            env['GIT_COMMITTER_DATE'] = commit_date.strftime('%Y-%m-%dT%H:%M:%S')
            env['GIT_AUTHOR_NAME'] = author_name
            env['GIT_AUTHOR_EMAIL'] = author_email
            env['GIT_COMMITTER_NAME'] = author_name
            env['GIT_COMMITTER_EMAIL'] = author_email

            commit_msg1 = random.choice(commit_messages)
            cmds1 = [
                f'cd "{project_folder}"',
                f'git checkout -B {branch}',
                f'git add "{os.path.relpath(target_file, project_folder)}"',
                f'git commit -m "{commit_msg1}"'
            ]
            full_cmd1 = ' && '.join(cmds1)
            if log_func:
                log_func(f'Commit 1: {commit_msg1} on branch {branch}')
            result1 = subprocess.run(full_cmd1, shell=True, capture_output=True, text=True, env=env)
            if log_func:
                log_func(result1.stdout)
                if result1.stderr:
                    log_func(result1.stderr)

            # Pull --rebase sebelum push commit 1
            pull_cmd1 = f'cd "{project_folder}" && git pull --rebase origin {branch}'
            if log_func:
                log_func(f'Pull --rebase before push 1 for {day.strftime("%Y-%m-%d")}:')
            result_pull1 = subprocess.run(pull_cmd1, shell=True, capture_output=True, text=True)
            if log_func:
                log_func(result_pull1.stdout)
                if result_pull1.stderr:
                    log_func(result_pull1.stderr)

            # Push commit 1
            push_cmd1 = f'cd "{project_folder}" && git push origin {branch}'
            if log_func:
                log_func(f'Push after commit 1 for {day.strftime("%Y-%m-%d")}:')
            result_push1 = subprocess.run(push_cmd1, shell=True, capture_output=True, text=True)
            if log_func:
                log_func(result_push1.stdout)
                if result_push1.stderr:
                    log_func(result_push1.stderr)

            # Commit 2: kembalikan baris yang dihapus ke posisi semula
            restored_lines = modified_lines[:remove_start] + removed_lines + modified_lines[remove_start:]
            try:
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.writelines(restored_lines)
                if log_func:
                    log_func(f'Restored {remove_count} lines to {target_file} (posisi {remove_start})')
            except Exception as e:
                if log_func:
                    log_func(f'Failed to restore {target_file}: {e}')
                return

            commit_date2 = day.replace(hour=12, minute=1, second=0) + timedelta(minutes=i*2)
            env['GIT_AUTHOR_DATE'] = commit_date2.strftime('%Y-%m-%dT%H:%M:%S')
            env['GIT_COMMITTER_DATE'] = commit_date2.strftime('%Y-%m-%dT%H:%M:%S')

            commit_msg2 = random.choice(commit_messages)
            cmds2 = [
                f'cd "{project_folder}"',
                f'git checkout -B {branch}',
                f'git add "{os.path.relpath(target_file, project_folder)}"',
                f'git commit -m "{commit_msg2}"'
            ]
            full_cmd2 = ' && '.join(cmds2)
            if log_func:
                log_func(f'Commit 2: {commit_msg2} on branch {branch}')
            result2 = subprocess.run(full_cmd2, shell=True, capture_output=True, text=True, env=env)
            if log_func:
                log_func(result2.stdout)
                if result2.stderr:
                    log_func(result2.stderr)

            # Pull --rebase sebelum push commit 2
            pull_cmd2 = f'cd "{project_folder}" && git pull --rebase origin {branch}'
            if log_func:
                log_func(f'Pull --rebase before push 2 for {day.strftime("%Y-%m-%d")}:')
            result_pull2 = subprocess.run(pull_cmd2, shell=True, capture_output=True, text=True)
            if log_func:
                log_func(result_pull2.stdout)
                if result_pull2.stderr:
                    log_func(result_pull2.stderr)

            # Push commit 2
            push_cmd2 = f'cd "{project_folder}" && git push origin {branch}'
            if log_func:
                log_func(f'Push after commit 2 for {day.strftime("%Y-%m-%d")}:')
            result_push2 = subprocess.run(push_cmd2, shell=True, capture_output=True, text=True)
            if log_func:
                log_func(result_push2.stdout)
                if result_push2.stderr:
                    log_func(result_push2.stderr)

            # Merge branch acak ke branch utama secara acak
            if len(branch_list) > 1 and random.random() < 0.5:
                main_branch = branch_list[0]
                if branch != main_branch:
                    merge_cmds = [
                        f'cd "{project_folder}"',
                        f'git checkout {main_branch}',
                        f'git pull --rebase origin {main_branch}',
                        f'git merge {branch}',
                        f'git push origin {main_branch}'
                    ]
                    merge_cmd = ' && '.join(merge_cmds)
                    if log_func:
                        log_func(f'Merging branch {branch} into {main_branch}')
                    result_merge = subprocess.run(merge_cmd, shell=True, capture_output=True, text=True)
                    if log_func:
                        log_func(result_merge.stdout)
                        if result_merge.stderr:
                            log_func(result_merge.stderr)

        day += timedelta(days=1)

    # Restore semua file yang pernah diubah ke kondisi awal
    for file_path, lines in file_backups.items():
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            if log_func:
                log_func(f'Restored {file_path} to original content (final restore)')
        except Exception as e:
            if log_func:
                log_func(f'Failed to final-restore {file_path}: {e}')
import sys
from PyQt5.QtWidgets import QApplication
from interface import SettingsWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    # Jalankan auto_commit_and_push dengan log ke interface setelah window ditutup
    app.exec_()
    auto_commit_and_push(win.add_log)
