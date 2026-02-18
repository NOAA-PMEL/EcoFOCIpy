"""Contains a collection erddap access tools

"""
import requests
from erddapy import ERDDAP


def test_erddap_connection(url=''):
    e = ERDDAP(server=url)
    url = e.get_search_url(search_for="dy", response="csv")
    r = requests.head(url)
    assert r.raise_for_status() is None


def erddapCTDretrieve(url=None, cruiseid=None, concastno='001', qclevel='final'):
    """Retrieve a single cast from a FOCI cruise hosted via erddap

    Args:
        url (str, optional): url to foci hosted erddap. Defaults to ''.
        cruiseid (str, optional): standard foci cruise id without hyphens. eg dy2103 Defaults to ''.
        concastno (str, optional): three digit foci consecutive cast number. Defaults to '001'.
        qclevel (str, optional): preliminary or final. Defaults to 'final'.
    """

    e = ERDDAP(
      server=url,
      protocol="tabledap",
    )

    e.dataset_id = f'CTD_{cruiseid}_{qclevel}'

    df = e.to_pandas(parse_dates=True)

    try:
        df = df[df.profile_id.str.contains(concastno)]
    except:
        df = df.dropna()[df.dropna().profile_id.str.contains(concastno)]

    return df


def erddapMooredInstretrieve(url=None, mooringid=None, qclevel='final', instrid=None):
    """Retrieve a single instrument from a FOCI mooring hosted via erddap

    Args:
        url (str, optional): url to foci hosted erddap. Defaults to ''.
        cruiseid (str, optional): standard foci mooring id without hyphens. eg 19bs2c Defaults to ''.
        instrid (str, optional): full instrument reference - 19bs2c_s37_0064m - usually the archived filenmame.
        qclevel (str, optional): preliminary or final. Defaults to 'final'.
    """

    e = ERDDAP(
      server=url,
      protocol="tabledap",
    )

    e.dataset_id = f'datasets_Mooring_{mooringid}_{qclevel}'

    if instrid:
        e.constraints = {'timeseries_id=': instrid}

    df = e.to_pandas(parse_dates=True)

    try:
        df = df[df['timeseries_id'] == instrid].dropna(how='all', axis=1)
    except:
        df = df

    return df
