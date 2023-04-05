import sys, os
import random
import argparse
import shutil
import re
import subprocess
import json
import multiline # multiline json parser
import codecs
import magic
import traceback
from configparser import ConfigParser
from pathlib import Path
from collections import defaultdict

from zipfile import ZipFile
from pprint import pprint
from glob import glob

try:
  cfg_path = open(os.path.join(Path(__file__).parent.resolve(), "config.json"))
  config = json.load(cfg_path)
except Exception as e:
  print(f"Could not read config. Fallback to defaults.\n{e}")
  config = {
    "dirs": {
      "ac": "/opt/assetto",
      "content": "/home/steam/ac/content",
      "track": "/home/steam/ac/content/tracks",
      "car": "/home/steam/ac/content/cars",
      "server": "/home/steam"
    },
    "db": {
      "dbname": "acconfig",
      "pass": "changethis",
      "user": "acconf"
    }
  }

ac_dir = config['dirs']['ac']
content_dir = config['dirs']['content']
track_dir = config['dirs']['track']
car_dir = config['dirs']['car']
server_dir = config['dirs']['server']

class AcConfig:

  def __init__(self, srvnum=None, srvname=None, cars=None, track=None, layout=None, password=None, admin_password=None, dry_run=False, random_ks_only=False):
    self.srvnum = srvnum
    self.password = password or ""
    self.admin_password = admin_password or ""
    self.dry_run = dry_run
    self.srvname = srvname
    self.cars = []
    self.track = track or None
    self.layout = layout or None
    self.random_ks_only = random_ks_only

    self.store_cars(cars)
    if self.layout == "default":
      self.layout = ""

  def store_cars(self, cars):
    car_store = {}
    for c in cars:
      car_store[c] = 1 if not c in car_store.keys() else car_store[c] + 1
    for (c, skincount) in car_store.items():
      self.cars.append((c, self.get_random_car_skin(c, skincount)))

  def set_password(self, password=None, admin_password=None):
    if password is not None:
      self.password = password
    if admin_password is not None:
      self.admin_password = admin_password

  def ready_check(self):
    not_ready = []
    to_check = ['srvname', 'track', 'layout']

    for c in to_check:
      if getattr(self, c) is None or not getattr(self, c):
        not_ready.append(c)

    if len(self.cars) == 0:
      not_ready.append('cars')

    if len(not_ready):
      return {"result": False, "missing": not_ready }
    return {"result": True}

  @staticmethod
  def get_available_tracks(ks_only_tracks=False):
    if ks_only_tracks:
      with open('original_tracks.txt') as otracks:
        track_dirs = otracks.read().splitlines()
    else:
      track_dirs = [t.name for t in os.scandir(track_dir) if t.is_dir()]
    tracks = defaultdict(dict)
    for t in track_dirs:
      tpath = Path(track_dir + "/" + t + "/ui/ui_track.json")
      # only one track layout
      if tpath.is_file():
        with open(tpath, 'rb') as blobread:
          blob = blobread.read()
          m = magic.open(magic.MAGIC_MIME_ENCODING)
          m.load()
          enc = m.buffer(blob)
          enc = 'utf-8-sig' if enc == 'utf-8' else enc
          print(f"Enc for track {t} layout {l}: {enc}")
          with codecs.open(tpath, 'r', enc) as ui:
            tdata = multiline.load(ui, multiline=True)
        tracks[t]['layouts'] = {'default': tdata}
      # multiple track layouts
      else:
        layouts = [d.name for d in os.scandir(track_dir + "/" + t + "/ui") if d.is_dir()]
        tracks[t]['layouts'] = {}
        for l in layouts:
          # this 'magic' stuff is needed, because the files are either in utf-8-sig, utf-8 or ISO-8859-1 ffs!
          ui_json_path = Path(track_dir).joinpath(t, 'ui', l, 'ui_track.json')
          print(f"Determining encoding of track {t} layout {l}")
          with open(ui_json_path, 'rb') as blobread:
            blob = blobread.read()
            m = magic.open(magic.MAGIC_MIME_ENCODING)
            m.load()
            enc = m.buffer(blob)
            enc = 'utf-8-sig' if enc == 'utf-8' else enc
            print(f"Enc for track {t} layout {l}: {enc}")
            with codecs.open(ui_json_path, 'r', enc) as ui:
              tracks[t]['layouts'][l] =  multiline.load(ui, multiline=True)
    return tracks

  def specific_track(self, track, layout=''):
    self.track = track
    self.layout = layout

  def random_track(self):
    tracks = AcConfig.get_available_tracks(self.random_ks_only)
    selected_track = random.choice(tracks)
    pprint(selected_track)
    track_models = [f.name for f in os.scandir(selected_track[1]) if f.is_file() and f.name.startswith('models_')]
    track_model = ''
    if len(track_models) > 0:
      track_model = re.sub(r'.ini$', '', re.sub(r'^models_', '', random.choice(track_models)))
    # check layouts and chose one
    ret_track = (selected_track[0], track_model)
    self.track = ret_track

  def get_car_skins(self, carname):
    return [f.name for f in os.scandir(os.path.join(car_dir, carname, "skins")) if f.is_dir()]

  def get_random_car_skin(self, carname, count=1):
    c = 0
    skins = self.get_car_skins(carname)
    return_skins = []
    while c<count:
      random.shuffle(skins)
      try:
        return_skins.append(skins.pop())
      except:
        skins = self.get_car_skins(carname)
        return_skins.append(random.choice(skins))
      c = c + 1
    return return_skins

  @staticmethod
  def get_available_cars(ks_only_cars=False):
    if ks_only_cars:
      with open('original_cars.txt') as ocars:
        car_dirs = ocars.read().splitlines()
    else:
      car_dirs = [f.name for f in os.scandir(car_dir) if f.is_dir()]
    cars = dict()
    for c in car_dirs:
      cpath = car_dir + "/" + c + "/ui/ui_car.json"
      with open(cpath) as f:
        cdata = multiline.load(f, multiline=True)
      cars[c] = cdata
    return cars

  def specific_cars(self, cars, skins_per_car=None, add=False):
    car_list = []
    if skins_per_car is None:
      skins_per_car = self.skins_per_car
    for c in cars:
      car_list.append((c, self.get_random_car_skin(c, skins_per_car)))
    if add:
      self.cars = self.cars + car_list
    else:
      self.cars = car_list

  def add_specific_cars(self, cars, skins_per_car=None):
    return self.specific_cars(cars, skins_per_car, True)

  def random_cars(self, count_cars=None, skins_per_car=None, add=False):
    if count_cars is None:
      count_cars = self.count_cars
    if skins_per_car is None:
      skins_per_car = self.skins_per_car
    cars_result = []
    car_list = []
    cars_tmp = AcConfig.get_available_cars(self.random_ks_only)
    for c in cars_tmp:
      car_list.append((c, self.get_random_car_skin(c, self.skins_per_car)))
    random.shuffle(car_list)
    while len(cars_result) < count_cars:
      cars_result.append(car_list.pop())
    if add:
      self.cars = self.cars + cars_result
    else:
      self.cars = cars_result

  def add_random_cars(self, count_cars=None, skins_per_car=None):
    return self.random_cars(count_cars, skins_per_car, True)

  def generate_entry_list(self, cars):
    entry_str = """
[CAR_{0}]
MODEL={1}
SKIN={2}
SPECTATOR_MODE=0
DRIVERNAME=
TEAM=
GUID=
BALLAST=0
RESTRICTOR=0
"""

    res_str = ""
    counter = 0
    for c in cars:
      for skin in c[1]:
        res_str = res_str + (entry_str.format(str(counter), c[0], skin))
        counter = counter + 1
    return res_str


  def write_config(self):
    srvnum = self.srvnum
    cfg_dir = Path(f"{server_dir}").joinpath(f"server{srvnum}/cfg")
    srvport = 9600 + int(self.srvnum)
    httpport = 8600 + int(self.srvnum)
    cars_string = ";".join([c[0] for c in self.cars])
    car_count = 0
    for c in self.cars:
      for s in c[1]:
        car_count = car_count + 1
    with open("./server_cfg.tpl", "rt") as fin:
      with open(cfg_dir.joinpath("server_cfg.ini"), "wt") as fout:
        for line in fin:
          fout.write(line.replace("{{TRACK}}", self.track)
            .replace("{{CARS}}", cars_string)
            .replace("{{TRACK_CONFIG}}", self.layout)
            .replace("{{SRVNAME}}", self.srvname)
            .replace("{{PASSWORD}}", self.password)
            .replace("{{ADMIN_PASSWORD}}", self.admin_password)
            .replace("{{SRVPORT}}", str(srvport))
            .replace("{{HTTPPORT}}", str(httpport))
            .replace("{{CAR_COUNT}}", str(car_count)))

    with open(cfg_dir.joinpath("entry_list.ini"), "wt") as fout:
      fout.write(self.generate_entry_list(self.cars))

  def print_config(self):
    print("Track: %s | Layout: %s" % (self.track, self.layout))
    for c in self.cars:
      print("Car: %-30s | Skins: %s" % (c[0], c[1]))

  def build_config(self):
    self.ready_check()
    self.print_config()
    if (self.dry_run):
      return
    self.write_config()

  def pack_mods(self, target_dir='/var/www/html/download/'):
    zip_file = '/var/www/html/download/acmods.zip'
    try:
      os.remove(zip_file)
    except:
      pass
    # pack track
    track_path = os.path.join('tracks', self.track[0])
    p = subprocess.Popen(['zip', '-r', zip_file, track_path], cwd=content_dir)
    p.wait()
    # pack cars
    for c in self.cars:
      car_path = os.path.join('cars', c[0])
      p = subprocess.Popen(['zip', '-r', zip_file, car_path], cwd=content_dir)
      p.wait()

class AcServer:

  def __init__(self, srvnum):
    self.ac_config = None
    self.srvnum = str(srvnum).zfill(3)
    if srvnum is None:
      self.srvnum = str(AcServer.get_free_srvnum()).zfill(3)

  @staticmethod
  def get_free_srvnum():
    srvnums = set([int(s.name.replace('server', '')) for s in os.scandir(f"{server_dir}") if s.is_dir()])
    pprint(srvnums)
    all_nums = set(range(1,99))
    print("min: ", str(min(all_nums - srvnums)))
    return min(all_nums - srvnums)


  @staticmethod
  def get_all_servers():
    servers = {}
    srvnums = [s.name.replace('server', '') for s in os.scandir(f"{server_dir}") if s.is_dir()]
    for num in srvnums:
      servers[num] = AcServer.get_server(num)
    return servers

  @staticmethod
  def get_server_list():
    servers = [] 
    srvnums = [s.name.replace('server', '') for s in os.scandir(f"{server_dir}") if s.is_dir()]
    for num in srvnums:
      servers.append(AcServer.get_server(num))
    return servers

  def stop_server(self):
    os.system(f'systemctl stop ac@{self.srvnum}')

  def delete_server(self):
    self.stop_server()
    path = Path(f"{server_dir}").joinpath(f"server{self.srvnum}/")
    shutil.rmtree(path)

  def get_server(srvnum):
    srvcfg = ConfigParser()
    srvcfg.read(Path(f"{server_dir}").joinpath(f"server{srvnum}/cfg/server_cfg.ini"))
    entrycfg = ConfigParser()
    entrycfg.read(Path(f"{server_dir}").joinpath(f"server{srvnum}/cfg/entry_list.ini"))

    server = {section: dict(srvcfg.items(section)) for section in srvcfg.sections()}
    entries = {section: dict(entrycfg.items(section)) for section in entrycfg.sections()}
    return {"server": server, "entries": entries, "srvnum": srvnum}


  def create_files(self):
    srvnum = self.srvnum
    usr = config['settings']['steam_user']
    Path(f"{server_dir}").joinpath(f"server{srvnum}/cfg").mkdir(parents=True, exist_ok=True)
    Path(f"{server_dir}").joinpath(f"server{srvnum}/results").mkdir(parents=True, exist_ok=True)
    # link ac server executable
    if not Path(f"{server_dir}").joinpath(f"server{srvnum}/acServer{srvnum}").is_symlink():
      Path(f"{server_dir}").joinpath(f"server{srvnum}/acServer{srvnum}").symlink_to(Path(f"{ac_dir}/acServer"))
    #if not Path(f"{server_dir}").joinpath(f"server{srvnum}/content").is_symlink():
    #  Path(f"{server_dir}").joinpath(f"server{srvnum}/content").symlink_to(Path(f"{ac_dir}/content"))
    #os.system(f"chown -R {usr}:{usr} {server_dir}/server{srvnum}")

  def create_config(self, data):
    pprint(data)
    try:
      self.create_files()
      srvdata = data['server']
      if not srvdata['password']:
        srvdata['password'] = ''
      if not srvdata['admin_password']:
        srvdata['admin_password'] = 'thisisthedefaultpassword'
      self.ac_config = AcConfig(srvnum=self.srvnum,
                        srvname=srvdata['name'],
                        cars=data['cars'],
                        track=srvdata['track'],
                        layout=srvdata['config_track'],
                        password=srvdata['password'],
                        admin_password=srvdata['admin_password'])
      self.ac_config.print_config()
      self.ac_config.write_config()
      self.restart_server()
      return (True, None)
    except Exception as e:
      print(str(e))
      traceback.print_exc()
      return (False, e)

  def restart_server(self):
    os.system(f'systemctl restart ac@{self.srvnum}')

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Build AC Server config')
  parser.add_argument('-d', dest='dry_run', action='store_true')
  args = parser.parse_args()

  rb = AcConfig(dry_run=args.dry_run, srvname="Feldberg - Lotus Type 49 - Practice (by wullxz)")
  rb.specific_track('feldberg')
  rb.specific_cars(['lotus_49'], 20)
  rb.set_password(password="pfora")
  rb.build_config()
