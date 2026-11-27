import json,sqlite3,time,sys,logging
from pathlib import Path
from datetime import datetime,timezone
from ruamel.yaml import YAML
from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s'); log=logging.getLogger('watchlist-cleanup')
DRY='--dry-run' in sys.argv
cfg=YAML(typ='safe').load(Path('/plex-config.yml').read_text())
url=cfg['plex']['url']; owner=PlexServer(url,cfg['plex']['token']); machine=owner.machineIdentifier
statePath=Path('/state/status.json')
def run():
 status={'time':datetime.now(timezone.utc).isoformat(),'dryRun':DRY,'users':[],'removed':0,'available':0,'errors':[]}
 db=sqlite3.connect('file:/seerr/db.sqlite3?mode=ro',uri=True)
 users=db.execute("select id,plexUsername,plexToken from user where plexToken is not null and length(plexToken)>0").fetchall();db.close()
 for uid,name,token in users:
  row={'userId':uid,'name':name,'watchlistMovies':0,'available':[],'removed':[]};status['users'].append(row)
  try:
   account=MyPlexAccount(token=token)
   resource=next((r for r in account.resources() if r.clientIdentifier==machine),None)
   if not resource:row['error']='Plex server access unavailable';continue
   server=PlexServer(url,resource.accessToken)
   movies=account.watchlist(libtype='movie');row['watchlistMovies']=len(movies)
   for item in movies:
    matches=server.library.search(guid=item.guid,libtype='movie')
    accessible=[]
    for movie in matches:
     # Read-only media mounts verify a real imported file exists, not just a Plex entry.
     if any(Path(part.file).is_file() for media in movie.media for part in media.parts if getattr(part,'file',None)):accessible.append(movie)
    if not accessible:continue
    row['available'].append(item.title);status['available']+=1
    if not DRY:
     account.removeFromWatchlist([item]);row['removed'].append(item.title);status['removed']+=1
     log.info('Removed available movie from watchlist: user=%s title=%s',name,item.title)
  except Exception as e:
   row['error']=type(e).__name__;status['errors'].append({'userId':uid,'type':type(e).__name__});log.error('User %s check failed: %s',uid,type(e).__name__)
 statePath.write_text(json.dumps(status,indent=2));log.info('Pass complete dryRun=%s available=%s removed=%s errors=%s',DRY,status['available'],status['removed'],len(status['errors']))
while True:
 try:run()
 except Exception as e:log.error('Pass failed: %s',type(e).__name__)
 if DRY or '--once' in sys.argv:break
 time.sleep(300)
