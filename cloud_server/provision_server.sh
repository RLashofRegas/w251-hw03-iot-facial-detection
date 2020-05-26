# create vs
if [[ -z $( ibmcloud sl vs list | grep "week03-hw-vs01"  )  ]]
then
    printf "Server does not exist. Creating...\n"
    ibmcloud sl vs create --datacenter=wdc07 --hostname=week03-hw-vs01 --domain=rlashof-w251.cloud --flavor B1_1X2X25 --billing=hourly --san --network 1000 --key=1813258 --image=4852636
else
    printf "Server already exists, continuing.\n"
fi

SERVER_ID=$( ibmcloud sl vs list | grep "week03-hw-vs01" | awk '{print $1}'  )

while [[ ! -z $( ibmcloud sl vs detail $SERVER_ID --output json | jq '.activeTransaction // empty' ) ]]
do
    printf "Waiting for server to initialize...\n"
    sleep 10s
done

# provision cos instance
if [[ -z $( ibmcloud resource service-instances | grep "cos-lite-service01" ) ]]
then
    printf "COS Service does not exist, creating...\n"
    ibmcloud resource service-instance-create cos-lite-service01 cloud-object-storage lite global -g Default
else
    printf "COS Service exists, continuing...\n"
fi

if [[ -z $( ibmcloud resource service-keys | grep "cos-service-key" ) ]]
then
    printf "Service key does not exist, creating...\n"
    ibmcloud resource service-instance-create cos-lite-service01 cloud-object-storage lite global -g Default
else
    printf "Service key exists, continuing...\n"
fi

SERVER_IP=$( ibmcloud sl vs detail $SERVER_ID --output json | jq -r '.primaryBackendIpAddress'  )
ssh $SERVER_IP 'mkdir -p "/root/.bluemix"'
ibmcloud resource service-key cos-service-key --output json | ssh $SERVER_IP 'cat > ~/.bluemix/cos_credentials'

# clone repo and install dependencies
if ssh $SERVER_IP '[ -d w251-hw03-iot-facial-detection ]'
then
    printf "git repo exists, pulling latest...\n"
    ssh $SERVER_IP 'cd w251-hw03-iot-facial-detection && git pull'
else
    printf "git repo does not exist, cloning...\n"
    ssh $SERVER_IP 'git clone https://github.com/RLashofRegas/w251-hw03-iot-facial-detection.git'
fi
ssh $SERVER_IP 'apt install -y docker-compose'

