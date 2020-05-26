export API_KEY=$( jq ".[0].credentials.apikey" /root/.bluemix/cos_credentials )
export CRN=$( jq ".[0].crn" /root/.bluemix/cos_credentials )
docker-compose up --build