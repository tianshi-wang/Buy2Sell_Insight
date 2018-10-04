from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import pandas as pd
import sklearn
import numpy as np
from connLocalDB import connDB
from sklearn.metrics import fbeta_score, make_scorer


class Rfc_cv(object):
    """
    Random Forest Classifer Cross Validation Class
    Methods:
        train_model: update best_parameter and best_model
        evaluate: evaluate on test-dataset, return scores
    """
    def __init__(self ):
        self.param_grid = {
            'n_estimators': [600],
            'max_depth':[2, 4, 8],
            'min_samples_split':[4,8],
            'class_weight':[{0:1,1:2},{0:1,1:4}],  # ,{0: 1, 1: 4},  {0:1, 1:10},{0:1,1:20}
            'random_state':[42]
        }
        self.best_model = None
        self.best_params = {}
        num_test = 1
        for key, val in enumerate(self.param_grid):
            num_test *= len(val)
        print("\nStart to find the best parameters for random forest classifier using cross-validation.")
        print("Parameters combinations to test are:")
        print(self.param_grid)
        print("Total test to run: "+str(num_test))

    def train_model(self, train_features, train_labels):
        # Create a based model
        print('Start training random forest classifier.')
        print('It will take a few')
        rfc = RandomForestClassifier()
        # Instantiate the grid search model
        scorer = make_scorer(fbeta_score, beta=1.4)
        grid_search = GridSearchCV(estimator = rfc, param_grid = self.param_grid,
                                  cv = 8, n_jobs = -1, verbose = 1,scoring=scorer)   # Using k-folds with cv=10
        grid_search.fit(train_features, train_labels)
        self.best_params = grid_search.best_params_
        self.best_model = grid_search.best_estimator_
        print('Best parameters for random forest classifier is: ')
        print(str(self.best_params))


    def evaluate(self, test_features, test_labels):
        predictions = self.best_model.predict(test_features)
        recallScore = sklearn.metrics.recall_score(test_labels, predictions)
        f1lScore = sklearn.metrics.f1_score(test_labels, predictions)
        errors = abs(predictions - test_labels)
        mape = 100 * np.sum(errors)/np.size(errors,0)
        accuracy = 100 - mape
        tp=0
        tpfp=0
        print("The false positives:")
        for i in range(len(predictions)):
            if predictions[i]==1 and test_labels.iloc[i]==1:
                tp+=1
            if test_labels.iloc[i]==1:
                tpfp+=1
        test_labels = np.array(test_labels)
        print(test_features[np.array(test_labels==1) & np.array(predictions==1)])
        recall = 1.0*tp/tpfp
        print('Model Performance')
        print('Average Error: {:0.4f} degrees.'.format(np.mean(errors)))
        print('Accuracy = {:0.2f}%.'.format(accuracy))
        return accuracy, recallScore, f1lScore

def getData():
    """
    Grep data from local SQL database
    :return: DataFrame containing train and test data
    """
    _, conn = connDB()
    join_email_query = """
        SELECT * From features
        ;
    """
    features = pd.read_sql_query(join_email_query, conn)
    features = features.fillna(value=0)
    new_features=pd.DataFrame()
    features['t-3-collectionNum'] = features.iloc[:,1:21].sum(axis=1)
    features['t-2-collectionNum'] = features.iloc[:,21:41].sum(axis=1)
    features['t-1-collectionNum'] = features.iloc[:,41:61].sum(axis=1)
    features = features.iloc[:,61:]
    selling = features['selling']
    features['sumFeatures'] = features.iloc[:,:].sum(axis=1)
    features.drop(labels=['selling'], axis=1, inplace=True)
    features['selling'] = selling
    columns = features.columns[:-1]

    print("Total sellers before removing ebay-migrant is"+ str(features[features['selling']==1].shape[0]))
    features = features[np.logical_or(features['selling']==0, np.logical_and(features['selling']==1,features['sumFeatures']>3))]
    print("Total sellers after removing ebay-migrant is"+ str(features[features['selling']==1].shape[0]))
    features = features.drop('sumFeatures',axis=1)
    return features


def resampleTraining(X_train, y_train, oversample=False):
    train_matrix = X_train.join(y_train)
    train_resampled_neg = train_matrix[train_matrix['selling'] == 0].sample(frac=0.01, random_state=42)
    train_resampled_pos = train_matrix[train_matrix['selling'] == 1]

    print("Number of sellers in training set is " + str(train_resampled_pos.shape[0]) + " and " + str(
        train_resampled_neg.shape[0]) + " are not.")

    X_train_resampled = train_resampled_neg.append(train_resampled_pos).iloc[:, :-1]
    y_train_resampled = train_resampled_neg.append(train_resampled_pos).iloc[:, -1]
    if not oversample:
        return X_train_resampled, y_train_resampled
    else:
        X_train_resampled_oversampled, y_train_resampled_oversampled = SMOTE(kind='borderline1').fit_sample(\
                            X_train_resampled, y_train_resampled)

        return X_train_resampled_oversampled, y_train_resampled_oversampled

def main():
    """
     Train random forest classifier
     1. Create freatures
     2. Split dataset to train/test
     3. Resample data (both undersampling and oversampling)
     4. Train the model
     5. Show test results
     """
    features = getData()   # Features (not split yet) from SQL
    X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split( \
        features.iloc[:, :-1], features.iloc[:, -1], test_size=0.30, random_state=32)
    X_train_resampled, y_train_resampled = resampleTraining(X_train, y_train)
    X_train_resampled_oversampled, y_train_resampled_oversampled = resampleTraining(X_train, y_train, oversample=True)
    print("Number of sellers in test set is " + str(sum(y_test)) + " and " + str(sum(y_test == 0)) + " are not.")

    rfc = Rfc_cv()
    print("Training model using undersample + oversample")
    rfc.train_model(X_train_resampled_oversampled, y_train_resampled_oversampled)
    print("Test set result:")
    accu, recallscore, f1Score = rfc.evaluate(X_test, y_test)
    print(str(accu) + ":" + str(recallscore) + ":" + str(f1Score))

    print('Weight for each features:')
    print(str(rfc.best_model.feature_importances_))
    #
    # print("Training model using undersample only")
    # rfc.train_model(X_train_resampled, y_train_resampled)
    #
    # print("Test set result:")
    # accu, recallscore, f1Score = rfc.evaluate(X_test, y_test)
    # print(str(accu) + ":" + str(recallscore) + ":" + str(f1Score))
    #
    # print('Weight for each features:')
    # print(str(rfc.best_model.feature_importances_))


if __name__ == "__main__":
    main()
