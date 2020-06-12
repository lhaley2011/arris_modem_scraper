import logging
from pprint import pformat

def parse_status(html):
    status = parse_status_page(html['status'])
    status.update(parse_product_page(html['product']))
    logging.debug(pformat(status))
    return status

def parse_product_page(html):
    """ Parse the HTML into the modem stats dict """
    logging.info('Parsing HTML Product Page for modem model sb6190')

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all("table", {'class': 'simpleTable'})
    stats = {}

    # downstream table
    stats['uptime'] = 0
    rows = tables[1].find_all("tr")
    td = rows[1].find_all('td')
    uptime = td[1].text.strip()
    uptime = uptime.split(':')

    minutes = int(uptime[2].strip().replace("  m", ""))
    hours = int(uptime[1].replace(" h", ""))
    minutes += hours * 60
    days = int(uptime[0].replace(" d", ""))
    minutes += days * 24 * 60

    stats['uptime'] = minutes
    logging.debug('Parsed Uptime: %d', minutes)
    return stats

def parse_status_page(html):
    """ Parse the HTML into the modem stats dict """
    logging.info('Parsing HTML Status Page for modem model sb6190')

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all("table", {'class': 'simpleTable'})
    stats = {}

    # downstream table
    stats['downstream'] = []
    for table_row in tables[1].find_all("tr"):
        if table_row.th:
            continue
        td = table_row.find_all('td')
        if td[0].text.strip() == "Channel":
            continue

        channel = td[0].text.strip()
        status = td[1].text.strip()
        modulation = td[2].text.strip()
        channel_id = td[3].text.strip()
        frequency = td[4].text.replace(" MHz", "").strip()
        power = td[5].text.replace(" dBmV", "").strip()
        snr = td[6].text.replace(" dB", "").strip()
        corrected = td[7].text.strip()
        uncorrectables = td[8].text.strip()

        stat = {
            'channel': channel,
            'status': status,
            'modulation': modulation,
            'channel_id': channel_id,
            'frequency': frequency,
            'power': power,
            'snr': snr,
            'corrected': corrected,
            'uncorrectables': uncorrectables
        }
        stats['downstream'].append(stat)

    logging.debug('downstream stats:')
    logging.debug(pformat(stats['downstream']))
    if not stats['downstream']:
        logging.error('Failed to get any downstream stats! Probably a parsing issue in parse_html_sb6190()')

    # upstream table
    stats['upstream'] = []
    for table_row in tables[2].find_all("tr"):
        if table_row.th:
            continue
        td = table_row.find_all('td')
        if td[0].text.strip() == "Channel":
            continue

        channel = td[0].text.strip()
        status = td[1].text.strip()
        channel_type = td[2].text.strip()
        channel_id = td[3].text.strip()
        symbol_rate = td[4].text.replace(" kSym/s", "").strip()
        frequency = td[5].text.replace(" MHz", "").strip()
        power = td[6].text.replace(" dBmV", "").strip()

        stat = {
            'channel': channel,
            'status': status,
            'channel_type': channel_type,
            'channel_id': channel_id,
            'symbol_rate': symbol_rate,
            'frequency': frequency,
            'power': power,
        }
        stats['upstream'].append(stat)

    logging.debug('upstream stats:')
    logging.debug(pformat(stats['upstream']))
    if not stats['upstream']:
        logging.error('Failed to get any upstream stats! Probably a parsing issue in parse_html_sb6190()')

    return stats
