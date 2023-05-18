# TableTennisMatchPredction
## Data Preparation

Create a folder named 'data' in the project and download the datasets from the Duke Box link in it. https://duke.box.com/s/26mitqjngbj1jefvigson4vuykm6trxe


## Methods
Run `ml.ipynb` for both decesion tree models and neural network models  

`data_preprocess.merge_dataset_total` returns a full dataframe that contains all players and match information

`data_preprocess.get_features_target` returns the features and targets given a dataframe (match data)
