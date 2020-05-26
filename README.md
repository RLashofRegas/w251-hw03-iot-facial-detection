# w251-hw03-iot-facial-detection
Facial detection at the edge with OpenCV, message passing with MQTT, and image storage with Cloud Object Storage

## Running
The code provided in this repo has two parts, the code under ./edge_device should be run on the edge_device while the code under ./cloud_server should be run on a central cloud server.

### Cloud Server
The code for deploying the cloud server is somewhat specific to the IBM Cloud due to the following:
1. `provision_server.sh` executes IBMCloud-specific commands to spin up the correct server
2. IAM authentication is used for cloud object storage access as recommended by IBM: https://cloud.ibm.com/docs/cloud-object-storage/iam?topic=cloud-object-storage-service-credentials#service-credentials-iam-hmac
3. The IBM boto3 fork is used for interfacing with Cloud Object Storage. For other cloud providers this could be switched out for the main boto3 repo with some small modifications to the authentication configuration. Details can be found here: https://cloud.ibm.com/docs/cloud-object-storage/libraries?topic=cloud-object-storage-python

The following configurations are not portable and will need to be changed if run on other systems:
1. `provision_server.sh` uses the ids of my ssh key and VM image template. This would need to be changed to run on another account.

To run the cloud section do the following:
* From a jumpbox within the infrastructure you would like to deploy from, clone the repo and run `sh provision_server.sh`

### Edge Device
The code for running on the edge device is specific to the Jetson TX2 in the following ways:
1. In the `Dockerfile` for the messenger it uses a Jetson specific docker image (w251/cuda:dev-tx2-4.3_b132)

To run the edge device code do the following:
1. Clone the repo.
2. Get the public IP address for the cloud server you are using as your cloud broker and update `./edge_device/message_forwarder/mosquitto.conf` to replace "cloud-ip" with the ip of your server.
3. Run `sh ./edge_device/install.sh` to install dependencies like docker-compose
4. Run `docker-compose up` from the `edge_device` folder.

## Running Tests

1. Install Dev Dependencies - Install dev dependencies (preferably in a virtual environment) using the requirements.txt file in the root of the repo.
2. Run Tests - Run `pytest` from the root of the repo.
