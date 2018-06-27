import MalShare
import datetime
import logging

logging.basicConfig(level=logging.INFO)

def process_sample(sample):
    print(sample)

def main():
    date_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    date_str = '2017-09-19'

    malshare = MalShare.MalShare(date_str=date_str, tmpdir='tmp')
    for sample in malshare.samples():
        process_sample(sample)

if __name__ == "__main__":
    main()
