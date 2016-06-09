# python youtube uploader
# written by jhertz
# large chunk of code borrowed from https://developers.google.com/youtube/v3/guides/uploading_a_video
# needs client_secrets.json for youtube API creds
import httplib
import httplib2
import os
import random
import sys
import time
import untangle

from sys import argv, exit
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# config -- these should be absolute paths
CLIENT_SECRETS_FILE = "C:\\Users\\NYCPM\\Desktop\\autovod\\client_secrets.json" 
STREAM_CONTROL_FILE = "C:\\Users\\NYCPM\\Dropbox\\Melee\\MeleeStreamControl\\Melee\\streamcontrol.xml"
VOD_FOLDER = "X:\\Vods\melee\\"
# constants
httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
PM_KEYWORDS = ["PM", "Project M", "SSBPM", "Wii"]
MELEE_KEYWORDS = ["Melee", "SSBM", "Gamecube"]
SMASH4_KEYWORDS = ["Smash4", "Sm4sh", "Smash4WiiU", "Smash 4 Wii U", "SSB4", "Wii U", "S4"]
SSB64_KEYWORDS = ["SSB", "64", "N64", "SSB64", "Smash64", "Smash 64"]
SMASH_KEYWORDS = ["Smash", "Smash Bros", "Super Smash Bros", "SmashBros", "SuperSmashBros"]
NEBS_KEYWORDS = ["nebs", "nebulous", "nebulous gaming", "nyc", "nebulous smash", "nebulous nyc", "nebulous gaming nyc", "esports"]



#functions
# parse stream control, return a dict with the options dict that initialize_upload() expects
def parse_xml(filename):
  contents= ""
  with open(filename, "r") as f:
    contents = f.readlines()
  #print "i read the xml file, here are its contents:\n\n"
  #print contents
  root = untangle.parse(filename)
  return_dict = {}
  player1 = root.items.pName1.cdata
  player2 = root.items.pName2.cdata
  main_title = root.items.eventTitle.cdata
  titleL = root.items.rOundl.cdata 
  titleR = root.items.rOundr.cdata
  #print "p1" + player1 + "p2" + player2 + "titleL" + titleL + "titleR" + titleR + "main" + main_title
  # figure out what game we're in right now
  game_keywords = MELEE_KEYWORDS

  vod_title = main_title + ": " + titleL + " - " + titleR + ": ", player1 + " vs. " + player2
  final_title = "".join(vod_title)
  if len(final_title) > 95:
    final_title = final_title[:95]
  return_dict['title'] = final_title
  print "going to upload with the title:" + return_dict['title']
  return_dict['description'] = "VOD from" + main_title + " created by khz's auto vod uploader"
  return_dict['keywords'] = SMASH_KEYWORDS + NEBS_KEYWORDS + game_keywords
  return_dict['category'] = "20" # this is the US category for gaming
  return_dict['privacyStatus'] = "public" #XXX: change this later
  return return_dict

def get_game_keywords(game):
  if "Melee" in game:
      return MELEE_KEYWORDS
  if "PM" in game:
      return PM_KEYWORDS
  if "Smash 4" in game:
      return SMASH4_KEYWORDS
  if "64" in game:
      return SSB64_KEYWORDS
  return []

# handle oauth stuff to give us the youtube service
def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message="clients secrets file not found!")

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

# entrypoint to actually upload
def initialize_upload(youtube, vod_file):

  options = parse_xml(STREAM_CONTROL_FILE)
  tags = ",".join(options['keywords'])

  body=dict(
    snippet=dict(
      title=options['title'],
      description=options['description'],
      tags=tags,
      categoryId=options['category']
    ),
    status=dict(
      privacyStatus=options['privacyStatus']
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(vod_file, chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print "Uploading file..."
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print "Video id '%s' was successfully uploaded." % response['id']
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError, e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS, e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print error
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print "Sleeping %f seconds and then retrying..." % sleep_seconds
      time.sleep(sleep_seconds)


#main entrypoint
if __name__ == '__main__':


    if not argv or not argv[1]:
      print "error! no file suppplied"
      exit(1)

    try:
      argparser.add_argument("--file", required=True, help="Video file to upload")
      args = argparser.parse_args()
      file_name = VOD_FOLDER + args.file
      print "file name: ", file_name
      old_size = -1
      print "about to loop waiting for file to be done"
      while True:
        size = os.path.getsize(file_name)
        print "size is", size
        if old_size == size:
          break
        old_size = size
        time.sleep(10)
      print "file is done"
      #print "read file name:", file_name
      youtube = get_authenticated_service(args)
      print "sucessfully created authenticated yt service"
    except Exception as ex:
      print ex
      raw_input()
    try:
        initialize_upload(youtube, file_name)
    except HttpError, e:
      print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
      raw_input()
    print "upload was sucessful!"
    time.sleep(10)
