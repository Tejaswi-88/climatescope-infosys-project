from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()
api.dataset_download_files(
    'nelgiriyewithana/global-weather-repository',
    path='data/raw',
    unzip=True
)
