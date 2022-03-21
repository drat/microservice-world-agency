from glob import glob
import base64
import json


class Extract:
    def __init__(self) -> None:
        pass

    def pathNameToText(self, pathName):
        with open(pathName, 'r', encoding='utf-8', errors='ignore') as fOpen:
            return fOpen.read().strip()

    def textToValues(self, text):
        values = []
        try:
            for line in text.split('\n'):
                params = line.strip().split('\t')
                if params[0] == '.facebook.com':
                    values.append({
                        'name': params[5],
                        'value': params[6]
                    })
            return values
        except:
            return values

    def isValidWithFacebook(self, values):
        c_user = False
        xs = False

        for value in values:
            if value['name'] == 'c_user':
                c_user = True
            if value['name'] == 'xs':
                xs = True
        return c_user and xs

    def getDataFromValuesFacebook(self, values, keyName):
        for value in values:
            if value['name'] == keyName:
                return value['value']
        return None

    def encodeBase64(self, values):
        return base64.b64encode(json.dumps(values).encode('utf-8')).decode('utf-8')

    def toFile(self, pathName, fileName):
        database = {}

        for path in glob(pathName, recursive=True):
            text = self.pathNameToText(path)
            values = self.textToValues(text)

            if self.isValidWithFacebook(values):
                c_user = self.getDataFromValuesFacebook(values, 'c_user')
                if c_user not in database:
                    database[c_user] = values
                else:
                    if len(values) > len(database[c_user]):
                        database[c_user] = values

        lines = [
            f"{key}|{self.encodeBase64(database[key])}" for key in database
        ]
        with open(fileName, 'w') as fWrite:
            fWrite.write('\n'.join(lines))


Extract().toFile(
    './_temp/03-21-2022_5/**/*.txt',
    './_temp/03-21-2022_5.txt'
)
