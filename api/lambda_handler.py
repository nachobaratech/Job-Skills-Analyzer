from mangum import Mangum
from main import app

# Mangum adapter for AWS Lambda
handler = Mangum(app, lifespan="off")
