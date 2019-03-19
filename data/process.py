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

def download(places):
    if places == "NYC" or places == "all":
        url2file("https://www.nrs.fs.fed.us/STEW-MAP/data/download/NYC2017_STEWMAP.zip", "NYC2017_STEWMAP.zip")
        os.system("unzip NYC2017_STEWMAP.zip")

    if places == "Baltimore" or places == "all":
        url2file("https://www.nrs.fs.fed.us/STEW-MAP/data/download/Baltimore_STEWMAP.zip", "Baltimore_STEWMAP.zip")
        os.system("unzip Baltimore_STEWMAP.zip")

def convert(places):
    if places == "NYC" or places == "all":
        os.system("rm NYC2017_STEWMAP_Polygons_Public.geojson NYC2017_STEWMAP_Points_Public.geojson NYC2017_STEWMAP_Networks_Public.geojson")

        os.system("ogr2ogr -t_srs epsg:4326 -f GeoJSON -select PopID NYC2017_STEWMAP_Polygons_Public.geojson NYC2017_STEWMAP_Polygons_Public.shp")
        os.system("ogr2ogr -t_srs epsg:4326 -f GeoJSON NYC2017_STEWMAP_Points_Public.geojson NYC2017_STEWMAP_Points_Public.shp")
        os.system("ogr2ogr -t_srs epsg:4326 -f GeoJSON NYC2017_STEWMAP_Networks_Public.geojson NYC2017_STEWMAP_Networks_Public.shp")

    if places == "Baltimore" or places == "all":
        os.system("rm Baltimore_Polygons.geojson Baltimore_Points.geojson Baltimore_Networks.geojson")

        os.system("ogr2ogr -t_srs epsg:4326 -f GeoJSON -select PopID Baltimore_Polygons.geojson Baltimore_STEWMAP/Baltimore_STEWMAP_shapefiles/Baltimore_Polygons.shp")
        os.system("ogr2ogr -t_srs epsg:4326 -f GeoJSON Baltimore_Points.geojson Baltimore_STEWMAP/Baltimore_STEWMAP_shapefiles/Baltmore_Points.shp")
        os.system("ogr2ogr -t_srs epsg:4326 -f GeoJSON Baltimore_Networks.geojson Baltimore_STEWMAP/Baltimore_STEWMAP_shapefiles/Baltimore_Networks.shp")


def _encode_network(points_file_name, networks_file_name, points_network_file_name, source_property, dest_property ):
    points_file = readfile(points_file_name)
    points = geojson.loads(points_file)
    networks = geojson.loads(readfile(networks_file_name))
    network_list = {}

    for feature in networks.features:
        source = feature.properties[source_property]
        dest = feature.properties[dest_property]

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
    writefile(points_network_file_name,dump)

def encode_network(places):
    if places == "NYC" or places == "all":
        _encode_network("NYC2017_STEWMAP_Points_Public.geojson", "NYC2017_STEWMAP_Networks_Public.geojson", "NYC2017_STEWMAP_Points_Networks_Public.geojson", "PopID_RESP", "PopID__ALT")

    if places == "Baltimore" or places == "all":
        _encode_network("Baltimore_Points.geojson", "Baltimore_Networks.geojson", "Baltimore_Points_Networks.geojson", "PopID_Resp", "PopID_Part")


#download('Baltimore')
convert('Baltimore')
encode_network('Baltimore')
