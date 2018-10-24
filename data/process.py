import urllib, urllib2
import os
import geojson


def readfile(filename):
  with open(filename, 'r') as f:
    read_data = f.read()
  f.closed
  return read_data

def writefile(file_name, buf):
  myFile = open(file_name, 'w')
  myFile.write(buf)
  myFile.close()

def url2file(url,file_name):
  req = urllib2.Request(url)
  try:
    rsp = urllib2.urlopen(req)
  except urllib2.HTTPError, err:
    print str(err.code) + " " + url
    return
  myFile = open(file_name, 'w')
  myFile.write(rsp.read())
  myFile.close()

def download():
    url2file("https://www.nrs.fs.fed.us/STEW-MAP/data/download/NYC2017_STEWMAP.zip", "NYC2017_STEWMAP.zip")
    os.system("unzip NYC2017_STEWMAP.zip")

def convert():
    os.system("rm NYC2017_STEWMAP_Polygons_Public.geojson NYC2017_STEWMAP_Points_Public.geojson NYC2017_STEWMAP_Networks_Public.geojson")

    os.system("ogr2ogr -t_srs epsg:4326 -f GeoJSON -select PopID NYC2017_STEWMAP_Polygons_Public.geojson NYC2017_STEWMAP_Polygons_Public.shp")
    os.system("ogr2ogr -t_srs epsg:4326 -f GeoJSON NYC2017_STEWMAP_Points_Public.geojson NYC2017_STEWMAP_Points_Public.shp")
    os.system("ogr2ogr -t_srs epsg:4326 -f GeoJSON NYC2017_STEWMAP_Networks_Public.geojson NYC2017_STEWMAP_Networks_Public.shp")

def encode_network():
    points_file = readfile("NYC2017_STEWMAP_Points_Public.geojson")
    points = geojson.loads(points_file)
    networks = geojson.loads(readfile("NYC2017_STEWMAP_Networks_Public.geojson"))
    network_list = {}

    for feature in networks.features:
        source = feature.properties['PopID_RESP']
        dest = feature.properties['PopID__ALT']

        if not (source in network_list):
            network_list[source] = []
        if not (dest in network_list):
            network_list[dest] = []

        network_list[source].append(str(dest))
        network_list[dest].append(str(source))

    result = {}
    result['type'] = 'FeatureCollection'
    result['features'] = []

    for feature in points.features:
        if feature.properties['PopID'] in network_list:
            feature.properties['network'] = ",".join( network_list[ feature.properties['PopID'] ] )
        else:
            feature.properties['network'] = ""

        result['features'].append( feature )

    dump = geojson.dumps(result, sort_keys=True, indent=2)
    writefile('NYC2017_STEWMAP_Points_Networks_Public.geojson',dump)


#download()
convert()
encode_network()
