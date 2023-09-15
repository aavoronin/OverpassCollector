import bz2
import binascii
import datetime
import tarfile
from lxml import etree as et
from bz2file import BZ2File

from scipy.sparse import compressed


def test_decompress():
    #with tarfile.open("c:/OSM/Niue.bz2", "w:gz") as tar:
    #    tar.add("c:/OSM/Niue.osm")

    compressionLevel = 9
    source_file = "c:/OSM/Niue.osm"
    destination_file = "c:/OSM/Niue.bz2"

    with open(source_file, 'rb') as data:
        tarbz2contents = bz2.compress(data.read(), compressionLevel)

    fh = open(destination_file, "wb")
    fh.write(tarbz2contents)
    fh.close()
    """
    decompressor = bz2.BZ2Decompressor()
    block_size = 1024 * 1024 // 1024 // 16
    data_read = 0
    i = 0
    with open("c:/OSM/planet-220207.osm.bz2", 'rb') as fpr:
        while True:
            block = fpr.read(block_size)
            if block:
                data = decompressor.decompress(block)
                data_read += len(data)
                i += 1
                print(f'{i:7} {data_read} bytes read {datetime.datetime.today().isoformat()}')

    """

    nodes = 0
    tags = 0
    relations = 0
    others = 0
    changesets = 0

    nodes_counter = {}
    kvs = {}
    MAX_TRACKLIST = 100000

    osm_files = ["central-america-latest.osm.bz2"]
    i = 0
    for osm_file in osm_files:
        #with BZ2File("c:/OSM/planet-220207.osm.bz2") as xml_file:
        with BZ2File(f"c:/OSM/{osm_file}") as xml_file:

            parser = et.iterparse(xml_file, events=('end',), remove_blank_text=True, remove_comments=True, encoding=None, huge_tree=True)
            for events, elem in parser:
                i += 1

                if elem.tag not in nodes_counter:
                    nodes_counter[elem.tag] = 1
                else:
                    nodes_counter[elem.tag] += 1

                if "k" in elem.attrib and "v" in elem.attrib:
                    k_ = elem.attrib["k"]
                    if k_ not in kvs:
                        kvs[k_] = [elem.attrib["v"]]
                    else:
                        if len(kvs[k_]) < MAX_TRACKLIST:
                            kvs[k_].append(elem.attrib["v"])

                #if elem.tag == "tag":
                #    tags += 1
                #elif elem.tag == "node":
                #    nodes += 1
                #elif elem.tag == "relation":
                #    relations += 1
                #elif elem.tag == "changeset":
                #    changesets += 1
                #else:
                #    others += 1
                #if i % 100000 == 0:
                #    print(f"{i:12} _pos: {format((xml_file._pos // 1024 // 1024) / 1024, '.3f') } Gb "
                #          f"{elem.sourceline:12} lines read, tags:{tags:12} nodes:{nodes:12} "
                #          f"relations:{relations:12} changesets: {changesets:12} others: {others:12} "
                #          f"{datetime.datetime.today().isoformat()}")
                if i % 100000 == 0:
                    print(f"{i:12} _pos: {format((xml_file._pos // 1024 // 1024) / 1024, '.3f') } Gb " +
                        f"{elem.sourceline:12} lines read {datetime.datetime.today().isoformat()}")

                if i % 2000000 == 0:
                    kvs_sorted = [k for k in kvs]
                    kvs_sorted = sorted(kvs_sorted, key=lambda k: -len(kvs[k]))
                    for kk in kvs_sorted:
                        print(f'k="{kk}", #{len(kvs[kk])}')

                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]



            ## Do some cleaning
            # Get rid of that element
            elem.clear()

            # Also eliminate now-empty references from the root node to node
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            pass

    #decompressed = bz2.decompress(compressed)
