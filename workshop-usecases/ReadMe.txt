- Run script populateDyDb with an email address to populate DynamoDb tables with items needed for the workshop
   ./populateDyDb <email-address>
- Run serverless deploy to deploy the service
   sls deploy
- Run aws cli to check list of lambdas deployed
   aws lambda list-functions
- Run script dumpDyDb to dump a particular DynamoDb table
  ./dumpDyDb Course 
        Or
  ./dumpDyDb Teacher
- Run script uploadFile to upload a file to a particular bucket
  ./uploadFile <bucketname> <filename>
