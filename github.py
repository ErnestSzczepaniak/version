import subprocess, pathlib
from typing import List
from commit import Commit

class Github():
    def __init__(self, path: str):
        self.path = pathlib.Path(path).absolute()

    def command_execute(self, command) -> List[str]:
        output = subprocess.check_output(command, shell=True).decode()
        if output == '': return []
        output = output.split('\n')
        return output

    def url(self):
        syntax = f"git -C {self.path} remote get-url origin"
        response = self.command_execute(syntax)[0]
        response = response[response.find(':')+1:-4]
        return f'https://github.com/{response}'

    def commits(self):
        syntax = f"git -C {self.path} log --pretty=format:'%h | %ad | %an | %s | %b' --date=format:'%d.%m.%Y, %H:%M:%S'"
        lines = self.command_execute(syntax)
        if lines == []: return None

        commit_lines = []

        current_header = ''
        current_body = []

        for line in lines:
            if '|' in line:
                items = line.split(' | ')
                current_header = ' | '.join(items[0:len(items) - 1])
                current_body = [line.split(' | ')[-1]]
            elif line != '':
                current_body.append(line)
            else:
                commit_lines.append(current_header + ' | ' + '\n'.join(current_body))
                current_header = ''
                current_body = []

        commit_lines.reverse()

        return [Commit(line) for line in commit_lines]

    def versions(self, commits: List[Commit], major: str = 'break', minor: str = 'feat', patch: str = 'fix'):
        version = [0, 0, 0]
        result = []
        for commit in commits:
            if commit.keyword == patch:
                version[2] += 1
                result.append('.'.join([str(number) for number in version]))
            elif commit.keyword == minor:
                version[1] += 1
                version[2] = 0
                result.append('.'.join([str(number) for number in version]))
            elif commit.keyword == major:
                version[0] += 1
                version[1] = 0
                version[2] = 0
                result.append('.'.join([str(number) for number in version]))
            else:
                result.append('.'.join([str(number) for number in version]))
        return result