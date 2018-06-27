import urllib.request
from lxml import etree
import os
import logging
from concurrent.futures import ThreadPoolExecutor


class MalShare:
    def __init__(self, date_str, tmpdir):
        self.__MD5_url = 'http://www.malshare.com/daily/%s/malshare_fileList.%s.txt'
        self.__sample_HTML_url = 'http://www.malshare.com/sample.php?action=detail&hash=%s'
        self.__date_str = date_str
        self.__tmpdir = tmpdir

    def download_MalShare_MD5(self):
        try:
            md5_tmpdir = os.path.join(self.__tmpdir, 'md5')
            if not os.path.exists(md5_tmpdir):
                os.makedirs(md5_tmpdir)

            save_path = os.path.join(md5_tmpdir, '%s.md5' % self.__date_str)
            if os.path.exists(save_path):
                os.remove(save_path)

            urllib.request.urlretrieve(self.__MD5_url % (self.__date_str, self.__date_str), save_path)

        except Exception as e:
            logging.error(e)
            logging.error('Download MD5 error, date: %s' % self.__date_str)
            return False

        logging.info('Finshed download MD5: %s' % self.__date_str)
        return True

    def download_MalShare_HTML(self, MD5):
        try:
            html_tmpdir = os.path.join(self.__tmpdir, 'html')
            if not os.path.exists(html_tmpdir):
                os.makedirs(html_tmpdir)

            save_dir = os.path.join(html_tmpdir, self.__date_str)
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)

            save_path = os.path.join(save_dir, '%s.html' % MD5)
            if os.path.exists(save_path):
                os.remove(save_path)

            urllib.request.urlretrieve(self.__sample_HTML_url % MD5, save_path)

        except Exception as e:
            logging.error(e)
            logging.error('Download sample HTML error, MD5: %s' % MD5)
            return False

        logging.info('Finshed download html: %s' % MD5)
        return True

    @staticmethod
    def parse_MalShare_sample_HTML(content):
        sample = {
            'Hashes': {},
            'Details': {},
            'Yara Hits': [],
            'Source': [],
            'Strings': '',
            'Sub Files': [],
            'Parent Files': []
        }

        try:
            root = etree.HTML(content)

            if root is None:
                return False

            tables = root.xpath('//table[@class=\'table\']')

            for table in tables:
                ths = table.xpath('./thead/tr/th')

                if not len(ths):
                    continue

                thead = table.xpath('./thead/tr/th/text()')[0]

                if thead == 'Hashes':
                    trs = table.xpath('./tbody/tr')
                    for tr in trs:
                        hash_type = tr.xpath('./td/b/text()')[0]
                        sample['Hashes'][hash_type] = tr.xpath('./td/text()')[0].replace(':', '').strip()

                elif thead == 'Details':
                    trs = table.xpath('./tbody/tr')
                    for tr in trs:
                        detail_type = tr.xpath('./td/b/text()')[0]
                        sample['Details'][detail_type] = tr.xpath('./td/text()')[0].replace(':', '').strip()

                elif thead == 'Yara Hits':
                    spans = table.xpath('./tbody/tr/td/span')
                    for span in spans:
                        sample['Yara Hits'].append(span.xpath('./text()')[0])

                elif thead == 'Source':
                    tds = table.xpath('./tbody/tr/td')
                    for td in tds:
                        if len(td.xpath('./text()')):
                            sample['Source'].append(td.xpath('./text()')[0].strip())

                elif thead == 'Strings':
                    if len(table.xpath('./tbody/tr/td/pre/text()')):
                        sample['Strings'] = table.xpath('./tbody/tr/td/pre/text()')[0]

                elif thead == 'Sub Files':
                    subs = table.xpath('./tbody/tr/td/a')
                    for sub in subs:
                        if len(sub.xpath('./text()')):
                            sample['Sub Files'].append(sub.xpath('./text()')[0].strip())

                elif thead == 'Parent Files':
                    parents = table.xpath('./tbody/tr/td/a')
                    for parent in parents:
                        if len(parent.xpath('./text()')):
                            sample['Parent Files'].append(parent.xpath('./text()')[0].strip())

        except Exception as e:
            logging.error(e)
            return False

        return sample

    def samples(self):
        if not self.download_MalShare_MD5():
            return False

        pool = ThreadPoolExecutor(max_workers=20)
        with open(os.path.join(self.__tmpdir, 'md5', '%s.md5' % self.__date_str), 'r') as f:
            for line in f:
                pool.submit(MalShare.download_MalShare_HTML, self, line.strip())
        pool.shutdown()

        html_curdir = os.path.join(self.__tmpdir, 'html', self.__date_str)
        for html in os.listdir(html_curdir):
            with open(os.path.join(html_curdir, html), 'rb') as f:
                yield self.parse_MalShare_sample_HTML(f.read())

