for aws lambda:
mkdir lambda_function
cd lambda_function
cp ../scraper.py .
pip install -t . bs4 requests mysql-connector-python python-dotenv
zip -r9 ../function.zip .