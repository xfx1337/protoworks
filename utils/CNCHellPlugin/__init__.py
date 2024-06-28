from . import CNCHellPlugin

def getMetaData():
    return {
        "stage": {
            "name": i18n_catalog.i18nc("@item:inmenu", "Preview"),
            "weight": 20
        }
    }


def register(app):
    return {
        "stage": PreviewStage.PreviewStage(app)
    }
