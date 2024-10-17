#!/usr/bin/env ptython
import json


class ParseJson:
    def __init__(self, jsonfile=''):
        self.jsonfile = jsonfile


    def makejson(self):
        """
        Reads the file in as a JSON object and returns that value
        :return:
        jsonobj
        """

        if self.jsonfile:
            with open(self.jsonfile, 'r') as jf:
                jsonobj = json.loads(jf.read())
                return jsonobj
        else:
            raise ValueError('No JSON specified, cannot run')


    def printout(self, *args):
        """
        prints the json object created in makejson()
        """
        if "pretty" in args:
            return json.dumps(self.makejson(), indent=4, sort_keys=True)
        else:
            return self.makejson()
