from houraiteahouse.app import app as application

# Use this for running locally at-will (eg, for debugging)

if __name__ == '__main__':
    application.run('0.0.0.0', 5000, debug = True, threaded=True)
