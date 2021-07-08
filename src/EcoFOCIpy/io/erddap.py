"""Contains a collection erddap access tools

"""
from erddapy import ERDDAP
import requests

def test_erddap_connection(url=''):
    e = ERDDAP(server=url)
    url = e.get_search_url(search_for="dy", response="csv")
    r = requests.head(url)
    assert r.raise_for_status() is None
    

def erddapCTDretrieve(url='',cruiseid='',concastno='001',qclevel='final'):
    """[summary]

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
    
    df = e.to_pandas()
    
    df = df[df.profile_id.str.contains(concastno)]
    
    return df