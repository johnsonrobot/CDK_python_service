from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
        aws_ec2 as ec2,
        core
    )

with open("./ittest2/userdata.sh", "r", encoding='utf-8') as file:
    userdata = file.read()

class Ittest2Stack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        

        myvpc = ec2.Vpc(self, "cdk-vpc", 
        max_azs=0,
        nat_gateways=0,
        cidr="10.0.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True
        )

        mysubnet = ec2.Subnet(self, "public-subnet", 
        availability_zone="us-east-2b",
        cidr_block="10.0.30.0/24",
        vpc_id=myvpc.vpc_id,
        map_public_ip_on_launch=True)

        mysubnet.add_default_internet_route(myvpc.internet_gateway_id, gateway_attachment=myvpc)
        
        mysg = ec2.SecurityGroup(self, "cdk-sg-it",
        vpc=myvpc,
        allow_all_outbound=True,
        description="it demo 30 days",
        security_group_name="cdk-sg")

        mysg.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(22), description="cdk remote access")
        mysg.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(80), description="cdk use browser to access")
        
        ami = ec2.AmazonLinuxImage(cpu_type=ec2.AmazonLinuxCpuType.X86_64,
        edition=ec2.AmazonLinuxEdition.STANDARD,
        generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
        storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        virtualization=ec2.AmazonLinuxVirt.HVM,
        )
        
        myec2 = ec2.Instance(self, "myEC2",
        instance_name="cdk-ec2-test",
        instance_type=ec2.InstanceType("t3.micro"),
        machine_image=ami,
        allow_all_outbound=True,
        availability_zone="us-east-2b",
        key_name="itdemo",
        security_group=mysg,
        vpc_subnets=ec2.SubnetSelection(subnets=[mysubnet]),
        user_data=ec2.UserData.custom(userdata),
        vpc=myvpc,
        block_devices=[ec2.BlockDevice(device_name="/dev/xvda",
        volume=ec2.BlockDeviceVolume.ebs(volume_size=10, volume_type=ec2.EbsDeviceVolumeType.GP3),
        mapping_enabled=True)])

        core.CfnOutput(self, "publicIP", value=myec2.instance_public_ip)
        core.CfnOutput(self, "publicDNS", value=myec2.instance_public_dns_name)
        core.CfnOutput(self, "privateIP", value=myec2.instance_private_ip)
        core.CfnOutput(self, "privateDNS", value=myec2.instance_private_dns_name)
