"""
Pipeline timestamp manager.

This module is responsible for comparing the records in ADS and the records in
Invenio. Its only public method is get_record_status() which returns 3 sets of
bibcodes:
    * the bibcodes not yet added to Invenio.
    * the bibcodes of the records that have been modified.
    * the bibcodes of the records that have been deleted in ADS.
"""

import sys
sys.path.append('/proj/adsx/invenio/lib/python/')

from invenio.dbquery import run_sql
from invenio.search_engine import get_mysql_recid_from_aleph_sysno
from invenio.search_engine import get_fieldvalues

from settings import BIBCODES_AST, BIBCODES_PHY, BIBCODES_GEN, BIBCODES_PRE
from global_functions import printmsg

# Timestamps ordered by increasing order of importance.
TIMESTAMP_FILES_HIERARCHY = [
        BIBCODES_GEN,
        BIBCODES_PRE,
        BIBCODES_PHY,
        BIBCODES_AST,
        ]

def get_records_status(verbose=False):
    """
    Return 3 sets of bibcodes:
    * bibcodes added are bibcodes that are in ADS and not in Invenio.
    * bibcodes modified are bibcodes that are both in ADS and in Invenio and
      that have been modified since the last update.
    * bibcodes deleted are bibcodes that are in Invenio but not in ADS.
    """
    records_added = []
    records_modified = []
    records_deleted = []

    printmsg(verbose, 'Getting ADS timestamps.')
    ads_timestamps = _get_ads_timestamps()
    printmsg(verbose, 'Getting ADS bibcodes.')
    ads_bibcodes = set(ads_timestamps.keys())
    printmsg(verbose, 'Getting Invenio bibcodes.')
    invenio_bibcodes = _get_invenio_bibcodes()

    printmsg(verbose, 'Deducting the added records.')
    records_added = ads_bibcodes - invenio_bibcodes
    printmsg(verbose, '    %d records to add.' % len(records_added))
    printmsg(verbose, 'Deducting the deleted records.')
    records_deleted = invenio_bibcodes - ads_bibcodes
    printmsg(verbose, '    %d records to delete.' % len(records_deleted))

    records_to_check = invenio_bibcodes - records_deleted
    printmsg(verbose, 'Checking timestamps for %d records.' %
            len(records_to_check))

    # TODO: This can probably be sped up by working with chunks of bibcodes
    # instead of single bibcodes.
    for bibcode in records_to_check:
        ads_timestamp = ads_timestamps[bibcode]

        invenio_recid = get_mysql_recid_from_aleph_sysno(bibcode)
        invenio_timestamp = get_fieldvalues(invenio_recid, '995__a')
        if not invenio_timestamp:
            # Maybe we could add instead of exiting.
            print >> sys.stderr, ('Problem: Record %s in Invenio does not '
                    'have a timestamp.' % bibcode)
            sys.exit(1)
        elif invenio_timestamp != ads_timestamp:
            records_modified.append(bibcode)

    printmsg(verbose, 'Done.')

    return records_added, records_modified, records_deleted

def _get_invenio_bibcodes():
    """
    Returns a set of bibcodes found in Invenio.
    """
    query = "SELECT value FROM bib97x WHERE tag='970__a'"
    res = run_sql(query)
    return set((line[0] for line in res))

def _get_ads_timestamps():
    """
    Merges the timestamp files according to the importance of the database
    in ADS.

    Returns a dictionary with the bibcodes as keys and the timestamps as values.
    """
    timestamps = {}
    for filename in TIMESTAMP_FILES_HIERARCHY:
        db_timestamps = _read_timestamp_file(filename)
        timestamps.update(db_timestamps)

    return timestamps

def _read_timestamp_file(filename):
    """
    Reads a timestamp file and returns a dictionary with the bibcodes as keys
    and the timestamps as values.
    """
    fdesc = open(filename)
    timestamps = {}
    for line in fdesc:
        bibcode, timestamp = line[:-1].split('\t', 1)
        timestamps[bibcode] = timestamp
    fdesc.close()

    return timestamps
