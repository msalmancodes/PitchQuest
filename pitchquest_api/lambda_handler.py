"""AWS Lambda handler for PitchQuest API"""
from mangum import Mangum
from .main import app

# Create the Lambda handler
handler = Mangum(app)
