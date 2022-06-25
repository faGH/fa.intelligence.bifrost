import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, ConfusionMatrixDisplay, accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputRegressor
from sklearn.utils import shuffle


class BifrostGradientBoosterEngine():
    is_timeseries_problem: bool = False
    global_scaling_factor: int = 1
    default_parameters = {
        'learning_rate': 0.1,
        'max_depth': 3,
        'colsample_bytree': 1,
        'subsample': 1,
        'min_child_weight': 1,
        'gamma': 1,
        'random_state': 1502,
        'eval_metric': 'rmse',
        'objective': 'reg:squarederror'
    }
    tuning_parameter_range = {
        'learning_rate': [0.3, 0.1, 0.03],
        'max_depth': [2, 6, 12],
        'colsample_bytree': [0.5, 0.75, 1],
        'subsample': [0.5, 0.75, 1],
        'min_child_weight': [1, 5, 15],
        'gamma': [1],
        'random_state': [1502],
        'eval_metric': ['rmse'],
        'objective': ['reg:squarederror']
    }

    def __init__(self,
                 data: pd.DataFrame,
                 column_name_to_predict: str,
                 use_binary_classifier: bool = False,
                 data_time_column_name: str = None,
                 enable_global_scaling: bool = False,
                 replace_missing_values: bool = True,
                 drop_columns_with_no_unique_values: bool = True,
                 replace_whitespace: bool = True):
        self.data = data.copy()
        self.columns_to_drop = list()
        self.column_name_to_predict = column_name_to_predict
        self.use_binary_classifier = use_binary_classifier
        self.model = None
        self.data_time_column_name = data_time_column_name

        if enable_global_scaling:
            self.global_scaling_factor = self.__determine_common_scale__(self.data)
            self.__apply_common_scale__(data=self.data, scale=self.global_scaling_factor)

            print(f'Global scaling has been set to {self.global_scaling_factor}.')

        if self.data_time_column_name is not None:
            # Move all Y values one into the future as we would want to predict the future Y given a current state (X).
            self.data[self.column_name_to_predict] = self.data[self.column_name_to_predict].shift(1, fill_value=0)
            self.data = self.__featurize_time_from_column__(self.data, self.data_time_column_name)

        if replace_missing_values:
            self.replace_missing_values()

        if drop_columns_with_no_unique_values:
            self.drop_columns_with_no_unique_values()

        if replace_whitespace:
            self.replace_whitespace()

    def __determine_common_scale__(self, data: pd.DataFrame):
        maximum_common_scale = 1

        for column in data.columns:
            column_is_long_float_type = data[column].dtype == np.float64

            if column_is_long_float_type:
                first_column_value_str = str(data[column].values[0])
                should_scale = len(first_column_value_str.split('.')[1]) > 1
                maximum_local_scale = 1

                while should_scale:
                    maximum_local_scale *= 10
                    should_scale = len(str(data[column].values[0] * maximum_local_scale).split('.')[1]) > 1

                maximum_common_scale = max(maximum_common_scale, maximum_local_scale)

        return maximum_common_scale

    def __apply_common_scale__(self, data: pd.DataFrame, scale: int, reverse: bool = False):
        for column in data.columns:
            column_is_long_float_type = data[column].dtype == np.float64

            if column_is_long_float_type:
                if reverse:
                    data[column] = data[column] / scale
                else:
                    data[column] = data[column] * scale

    def __get_training_test_dfs__(self, training_split: float):
        training_record_count = int(len(self.data) * training_split)

        return self.data[:training_record_count], self.data[training_record_count:]

    def __get_x_y_dfs__(self, df: pd.DataFrame, column_name_to_predict: str) -> pd.DataFrame:
        x = df.drop(columns=[column_name_to_predict])
        y = df.loc[:, [column_name_to_predict]]

        return x, y

    def __get_df_matrix__(self, df: pd.DataFrame, column_name_to_predict: str, name: str) -> xgb.DMatrix:
        x, y = self.__get_x_y_dfs__(df, column_name_to_predict=column_name_to_predict)
        matrix = xgb.DMatrix(data=x, label=y)

        print(f'[{name}] Matrix X: {x.shape}, Matrix Y: {y.shape}')

        return matrix, x, y

    def __calculate_mape_score__(self, y_true: pd.Series, y_pred: pd.Series):
        y_true, y_pred = np.array(y_true), np.array(y_pred)

        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def __print_model_assessment__(self, test_column_data: pd.Series, predictions: pd.Series):
        if not self.use_binary_classifier:
            print(f'Mean Absolute Error: {mean_absolute_error(test_column_data, predictions)} ({mean_absolute_error(test_column_data, predictions) / self.global_scaling_factor} reverse-scaled.)')
            print(f'Mean Squared Error: {np.sqrt(mean_squared_error(test_column_data, predictions))} ({np.sqrt(mean_squared_error(test_column_data, predictions)) / self.global_scaling_factor} reverse-scaled.)')
            print(f'MAPE: {self.__calculate_mape_score__(test_column_data, predictions)} ({self.__calculate_mape_score__(test_column_data, predictions) / self.global_scaling_factor} reverse-scaled.)')
        else:
            print(f'Test Data Accuracy: {accuracy_score(test_column_data, predictions)}')

    def __featurize_time_from_column__(self, data: pd.DataFrame, column_name: str, column_prefix: str = 't_'):
        __data__: pd.DataFrame = data.copy()

        parsed_date_temporary_column = pd.to_datetime(__data__[column_name])
        __data__.drop(columns=[column_name], inplace=True)

        __data__[f'{column_prefix}year'] = parsed_date_temporary_column.dt.year
        __data__[f'{column_prefix}month'] = parsed_date_temporary_column.dt.month
        __data__[f'{column_prefix}day'] = parsed_date_temporary_column.dt.day
        __data__[f'{column_prefix}hour'] = parsed_date_temporary_column.dt.hour
        __data__[f'{column_prefix}minute'] = parsed_date_temporary_column.dt.minute
        __data__[f'{column_prefix}day_of_year'] = parsed_date_temporary_column.dt.dayofyear
        __data__[f'{column_prefix}day_of_week'] = parsed_date_temporary_column.dt.dayofweek
        __data__[f'{column_prefix}quarter'] = parsed_date_temporary_column.dt.quarter
        self.is_timeseries_problem = True

        print(f'Extracted time series features from column "{column_name}" and dropped the original column.')

        return __data__

    def drop_columns_with_no_unique_values(self):
        self.columns_to_drop = [c for c in self.data.columns if len(self.data[c].unique()) <= 1]
        print(f'Dropping {len(self.columns_to_drop)} columns due to only containing 1 or less unique values. -> {self.columns_to_drop}')
        self.data.drop(columns=self.columns_to_drop, inplace=True)

        return self

    def replace_whitespace(self,
                           substitute: str = '_',
                           from_column_names: bool = True,
                           from_values: bool = True):
        if from_column_names:
            self.data.columns = self.data.columns.str.replace(' ', substitute)

        if from_values:
            self.data.replace(' ', substitute, regex=True, inplace=True)

        print(f'Whitespace replaced with "{substitute}".')

        return self

    def replace_missing_values(self, value: int = 0):
        self.data.fillna(value)

        print(f'Replaced all missing values with {value}.')

        return self

    def onehot_encode_categorical_columns(self, column_names: list):
        if len(column_names) > 0:
            self.data = pd.get_dummies(self.data, columns=column_names)
            print(f'One-Hot encoded {len(column_names)} columns. -> {column_names}')

        return self

    def fit(self,
            enable_hyperparameter_optimization: bool,
            training_split: float = 0.8):
        self.training_split = training_split

        if not self.is_timeseries_problem:
            self.data = shuffle(self.data)

        training_df, testing_df = self.__get_training_test_dfs__(training_split=training_split)
        training_matrix, training_x, training_y = self.__get_df_matrix__(training_df, column_name_to_predict=self.column_name_to_predict, name='Training')
        testing_matrix, testing_x, testing_y = self.__get_df_matrix__(testing_df, column_name_to_predict=self.column_name_to_predict, name='Testing')
        parameters_to_use = self.default_parameters

        if enable_hyperparameter_optimization:
            grid_result = None

            if self.use_binary_classifier:
                xgbc0 = xgb.XGBClassifier(objective='binary:logistic',
                                          booster='gbtree',
                                          eval_metric='auc',
                                          tree_method='hist',
                                          grow_policy='lossguide',
                                          use_label_encoder=False)
                default_params = {}
                gparams = xgbc0.get_params()

                for key in gparams.keys():
                    gp = gparams[key]
                    default_params[key] = [gp]

                grid_search = GridSearchCV(
                    estimator=xgb.XGBClassifier(),
                    param_grid=default_params,
                    cv=3,
                    scoring='accuracy',
                    verbose=1,
                    return_train_score=True,
                    n_jobs=-1
                )
                grid_result = MultiOutputRegressor(grid_search).fit(training_x, training_y)
            else:
                grid_search = GridSearchCV(
                    estimator=xgb.XGBRegressor(),
                    param_grid=self.tuning_parameter_range,
                    cv=3,
                    scoring='neg_mean_squared_error',
                    verbose=1,
                    n_jobs=-1
                )
                grid_result = MultiOutputRegressor(grid_search).fit(training_x, training_y)

            parameters_to_use = grid_result.estimators_[0].best_params_
            print('Hyperparameter optimization completed successfully.')

        self.model = xgb.train(
            params=parameters_to_use,
            dtrain=training_matrix,
            num_boost_round=1000,
            evals=[(testing_matrix, self.column_name_to_predict)],
            verbose_eval=200
        )

        return self

    def evaluate(self):
        training_df, testing_df = self.__get_training_test_dfs__(training_split=self.training_split)
        testing_matrix, testing_x, testing_y = self.__get_df_matrix__(testing_df, column_name_to_predict=self.column_name_to_predict, name='Testing')

        # Predict.
        predictions = self.predict(future_data=testing_df,
                                   bypass_scale_application=True)

        if not self.use_binary_classifier:
            (training_df[self.column_name_to_predict] / self.global_scaling_factor)[1:].rename('Training Data').plot(figsize=(9, 6), legend=True)
            (testing_df[self.column_name_to_predict] / self.global_scaling_factor).rename('Test Data').plot(legend=True)
            predictions.rename('Predictions').plot(legend=True)
        else:
            predictions = (predictions > 0.5).astype(int)
            ConfusionMatrixDisplay.from_predictions(y_true=testing_y, y_pred=predictions)

        self.__print_model_assessment__(testing_df[self.column_name_to_predict], predictions)

        return self

    def predict(self,
                future_data: pd.DataFrame,
                bypass_scale_application: bool = False) -> pd.Series:
        __future_data__: pd.DataFrame = future_data.copy()

        if self.is_timeseries_problem and self.data_time_column_name in future_data.columns:
            __future_data__ = self.__featurize_time_from_column__(__future_data__, self.data_time_column_name)
            __future_data__.drop(columns=self.columns_to_drop, inplace=True)

        if not bypass_scale_application:
            self.__apply_common_scale__(__future_data__, self.global_scaling_factor)

        matrix, x, y = self.__get_df_matrix__(__future_data__, column_name_to_predict=self.column_name_to_predict, name='Prediction')
        predictions = pd.Series(self.model.predict(matrix)) / self.global_scaling_factor
        predictions.index = __future_data__.index

        return predictions

    def visualize(self, verbose: bool = False):
        if verbose:
            for importance_type in ('weight', 'gain', 'cover', 'total_gain', 'total_cover'):
                print(f'{importance_type}: {self.model.get_score(importance_type=importance_type)}')

        return xgb.to_graphviz(self.model, num_trees=0, size='10,10')
