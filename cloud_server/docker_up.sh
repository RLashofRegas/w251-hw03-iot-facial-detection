export API_KEY=$( jq -r ".[0].credentials.apikey" /root/.bluemix/cos_credentials )
export CRN=$( jq -r ".[0].credentials.resource_instance_id" /root/.bluemix/cos_credentials )
docker-compose up --build