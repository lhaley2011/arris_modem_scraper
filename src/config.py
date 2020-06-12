import logging
from pprint import pformat

def get_config():
    from dotenv import load_dotenv
    from pathlib import Path  # python3 only
    env_path = Path('.') / '.env'
    logging.debug('Loading config from %s', env_path)
    load_dotenv(dotenv_path=env_path)

    config = {}
    config['MAIN'] = get_main_config()
    config['INFLUXDB'] = get_influxdb_config()
    logging.debug(pformat(config))
    return config

def get_main_config():
    import os
    config = {}
    config['destination'] = os.getenv("DESTINATION")
    config['sleep_interval'] = os.getenv("SLEEP_INTERVAL")
    config['max_intervals'] = os.getenv("MAX_INTERVALS")
    config['modem_status_url'] = os.getenv("MODEM_STATUS_URL")
    config['modem_product_url'] = os.getenv("MODEM_PRODUCT_URL")
    config['modem_model'] = os.getenv("MODEM_MODEL")
    return config

def get_influxdb_config():
    import os
    config = {}
    config['host'] = os.getenv("INFLUXDB_HOST")
    config['port'] = os.getenv("INFLUXDB_PORT")
    config['database'] = os.getenv("INFLUXDB_DATABASE")
    config['username'] = os.getenv("INFLUXDB_USERNAME")
    config['password'] = os.getenv("INFLUXDB_PASSWORD")
    config['use_ssl'] = boolean(os.getenv("INFLUXDB_USE_SSL"))
    config['verify_ssl'] = boolean(os.getenv("INFLUXDB_VERIFY_SSL"), True)
    return config

def boolean(str, default=False):
    if str == None:
        return default
    return str.lower() in ['true', '1', 't', 'y', 'yes']
