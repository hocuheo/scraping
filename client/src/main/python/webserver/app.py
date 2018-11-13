import connexion
import logging
import asyncio
from twisted.internet import asyncioreactor
# get our reactor installed as early as possible, in case other
# imports decide to import a reactor and we get the default
asyncioreactor.install(asyncio.get_event_loop())

app = connexion.AioHttpApp(__name__, specification_dir="../../resources/swagger.yaml", options={"swagger_ui": False})
app.add_api('swagger.yaml')

if __name__ == '__main__':
    app.run(9090)