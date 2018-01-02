import csv
import tempfile
from flask import Flask, render_template, redirect, url_for, request, make_response,jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import Imputer,LabelEncoder,OneHotEncoder,StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.cross_validation import train_test_split
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
import copy
import json
import sys
app = Flask(__name__)

regressor = LinearRegression()

	
@app.route('/api/post/json', methods=['GET','POST'])
def json_view() :
	data = request.get_json(force=True)
	#print(data)
	df = pd.io.json.json_normalize(data)
	cols=list(df.columns.values)
	#print(df)
	X = df.values
	#print(X)
	Y_pred = regressor.predict(X)
	Y_pred=('%.3f' % Y_pred)
	data = Y_pred
	#print(Y_pred)
	'''response = app.response_class(
		response=json.dumps(data),
		status=200,
		mimetype='application/json'
	)
	return response'''
	return jsonify(
		Predicted_salary=data,
	)
	
@app.route('/')
def form():
	return render_template('index.html')
		
@app.route('/upload', methods=["POST"])
def transform_view():
	file = request.files['data_file']
	if request.method == 'POST':
		tempfile_path = tempfile.NamedTemporaryFile().name
		file.save(tempfile_path)
		sheet = pd.read_csv(tempfile_path )
		col=pd.read_csv(tempfile_path, nrows=1).columns.tolist()
		#print(col)
		#sys.stdout.flush()
		data=request.form
		length2=len(sheet.columns)
		t=col[length2-1]
		tc=length2
		#print(t)
		#sys.stdout.flush()
		col1=col.remove(t)
		X = sheet.iloc[:,:-1].values
		Y = sheet.iloc[:,-1].values
		tr=int(request.form['Total No. Of Rows'])
		trr=int(request.form['No. of rows for training'])
		X_org_test=copy.copy(X[trr:,:tc])
		#print(X_org_test)
		#sys.stdout.flush()
		mv=""
		if 'Column Containing Missing Values' in request.form:
			mv=request.form['Column Containing Missing Values']
		else:
			mv=""
		if mv is not "" :
			mv1=mv.split(',')
			for i in range(0 , len(mv1)):
				elem = int(mv1[i])
				d=elem+1
				imputer=Imputer(missing_values="NaN",strategy="mean",axis=0)
				imputer=imputer.fit(X[:,elem:d])
				X[:,elem:d]=imputer.transform(X[:,elem:d])
			#print(X)
			#sys.stdout.flush()
			#print(Y)
			#sys.stdout.flush()
		X_train= X[:trr,:]
		X_test= X[trr:,:]
		Y_train= Y[:trr]
		Y_test= Y[trr:]
		
		sc = StandardScaler()
		X_train = sc.fit_transform(X_train)
		X_test = sc.transform(X_test)

		pca = PCA(n_components = 2)
		X_train = pca.fit_transform(X_train)
		X_test = pca.transform(X_test)
		explained_variance = pca.explained_variance_ratio_
		
		classifier = LogisticRegression(random_state = 0)
		classifier.fit(X_train, Y_train)
		
		Y_pred = classifier.predict(X_test)
		print(Y_pred)
		#print("Printing Y_pred **************************\n\n")
		#sys.stdout.flush()
		#print(Y_pred)
		#sys.stdout.flush()
		#print("Printed Y_pred ***************************\n\n")
		#sys.stdout.flush()
		pred=[]
		for i in range(0,len(Y_pred)) :
			pre=int(Y_pred[i])
			pred.append(pre)
		#Y_pred=list(Y_pred)
		df = pd.DataFrame(X_org_test,columns=col)
		#print(df)
		#sys.stdout.flush()
		str='Predicted'
		str1=str+' '+t
		df[str1] = pd.Series(pred,index=df.index)
		return render_template("result.html",tables=[sheet.to_html(classes='sheet')],result=data,res=[df.to_html(classes='sheet')])
		return "success"

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)