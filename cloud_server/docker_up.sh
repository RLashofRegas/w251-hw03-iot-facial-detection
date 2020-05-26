export API_KEY=$( jq ".[0].credentials.apikey" /root/.bluemix/cos_credentials )
export CRN=$( jq ".[0].credentials.resource_instance_id" /root/.bluemix/cos_credentials )
docker-compose up --build