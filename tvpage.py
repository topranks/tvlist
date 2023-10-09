#!/usr/bin/python3

import argparse
from bs4 import BeautifulSoup
import requests
import sys
from string import digits

# https://en.kingofsat.net/freqs.php?&pos=28.2E&standard=All&ordre=freq&filtre=Clear&cl=eng

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', help='Kingoofsat URL', type=str, default="")
parser.add_argument('-f', '--file', help='Kingoofsat saved HTML file', type=str, default="")
args = parser.parse_args()

def main():
    soup  = get_soup()

    transponders = []
    channels = []

    tables = soup.find_all('table')
    for table in tables:
        if table['class'] == ['frq']:
            tdata = table.find_all('td')
            pos = tdata[0].get_text().strip()
            if pos == "Pos":
                continue
            transponders.append({
                'pos': pos,
                'channels': [],
                'name': tdata[1].get_text().lstrip(digits).strip(),
                'freq': tdata[2].get_text().strip(),
                'polarity': tdata[3].get_text().strip(),
                'transponder_id': tdata[4].get_text().strip(),
                'beam': tdata[5].get_text().strip(),
                'standard': tdata[6].get_text().strip(),
                'modulation': tdata[7].get_text().strip(),
                'symbol_rate': tdata[8].get_text().strip().split()[0],
                'fec': tdata[8].get_text().strip().split()[1],
                'mbps': tdata[9].get_text().strip().split(",")[-1].split()[0],
                'nid': tdata[10].get_text().strip(),
                'tid': tdata[11].get_text().strip()
            })
        elif table['class'] == ['fl']:
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                video_pid = columns[8].get_text().strip()
                if video_pid:
                    try:
                        channels.append({
                            'transponder': len(transponders) - 1,
                            'v': columns[1].get_text().strip(),
                            'name': columns[2].get_text().strip(),
                            'country': columns[3].get_text().strip(),
                            'genre': columns[4].get_text().strip(),
                            'broadcaster': columns[5].get_text().strip(),
                            'encryption': columns[6].get_text().strip(),
                            'sid': columns[7].get_text().strip(),
                            'video_pid': video_pid,
                            'audio_pid': columns[9].get_text().strip().split()[0],
                            'pmt_pid': columns[10].get_text().strip(),
                            'pcr_pid': columns[11].get_text().strip(),
                            'txt_pid': columns[12].get_text().strip()
                        })
                    except IndexError as e:
                        print(len(columns[8].get_text().split()))
                        print(e)
                        print(channels[0])
                        sys.exit(1)
                    
                    
    for channel in channels:
        transponder = transponders[channel['transponder']]
        print(f"{channel['name']};2-{transponder['tid']}-{channel['sid']}")



def get_soup():
    if args.url:
        print(f"Getting URL {args.url}... ", end='')
        # Get the site with HTTP:
        try:
            site_html = requests.get(args.url)
        except Exception as e:
            print(f"Couldn't download {args.url} - {e}.")
            sys.exit(1)

        soup = BeautifulSoup(site_html.text, 'html.parser')
        print("done.")
        return soup

    elif args.file:
        print(f"Opening File {args.file}... ", end='')
        with open(args.file, 'r') as html_file:
            soup = BeautifulSoup(html_file.read(), 'html.parser')
            print("done.")
            return soup

    else:
        print("No URL or input file specified, quitting.")
        sys.exit(1)

if __name__ == '__main__':
    main()
