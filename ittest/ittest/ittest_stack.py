from aws_cdk import core as cdk

from aws_cdk import (
    aws_ec2 as ec2,
    core
)

# user_data_str = \
# """
# #!/bin/bash -ex 
# yum -y update 
# yum -y install httpd php mysql php-mysql 
# chkconfig httpd on 
# service httpd start 
# cd /var/www/html 
# wget https://s3-us-west-2.amazonaws.com/us-west-2-aws-training/awsu-spl/spl-13/scripts/app.tgz 
# tar xvfz app.tgz 
# chown apache:root /var/www/html/rds.conf.php
# """

with open("./ittest/user_data.sh", "rb") as file:
    comment = file.read()

class IttestStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        myVPC = ec2.Vpc(self, "VPC", 
        cidr="10.0.0.0/16",
        max_azs=1,
        subnet_configuration=[
        ec2.SubnetConfiguration(
            subnet_type=ec2.SubnetType.PUBLIC,
            name="public-subnet1",
            cidr_mask= 24
        ),
        ec2.SubnetConfiguration(
            subnet_type=ec2.SubnetType.PUBLIC,
            name="public-subnet2",
            cidr_mask=24
        ),
        ]
        )
        
        mySubnet = ec2.PublicSubnet(self, "mySubnet",
        availability_zone="us-east-2a",
        cidr_block="10.0.20.0/24",
        vpc_id=myVPC.vpc_id,
        map_public_ip_on_launch=True)
        

        mySG = ec2.SecurityGroup(self, "SG",
        vpc=myVPC,
        allow_all_outbound=True,
        description="IT demo 30 days for CDK",
        security_group_name="CDK-SG-test")

        mySG.add_ingress_rule(ec2.Peer.any_ipv4(),
        ec2.Port.tcp(22),
        description="test ssh remote")
        
        mySG.add_ingress_rule(ec2.Peer.any_ipv4(),
        ec2.Port.tcp(80),
        description="test http access")

        ami = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            cpu_type=ec2.AmazonLinuxCpuType.X86_64,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )
        
        userdata = ec2.UserData.custom(str(comment, "utf-8"))
        
        myEc2 = ec2.Instance(self, "EC2",
        instance_type=ec2.InstanceType("t3.micro"),
        machine_image=ami,
        instance_name="CDK-EC2-TEST", key_name="itdemo",
        security_group=mySG,
        user_data=userdata,
        vpc_subnets=ec2.SubnetSelection(subnets=[mySubnet]),
        vpc=myVPC)

        mySubnet.add_default_internet_route(gateway_id=myVPC.internet_gateway_id, gateway_attachment=myVPC)
        
        core.CfnOutput(self, "DNS output", value=myEc2.instance_public_dns_name)
        core.CfnOutput(self, "IP output", value=myEc2.instance_public_ip)
        core.CfnOutput(self, "privateIP", value=myEc2.instance_private_ip)
        core.CfnOutput(self, "privateDNS", value=myEc2.instance_private_dns_name)

