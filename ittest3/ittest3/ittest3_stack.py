from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_ec2 as ec2,
    core
    )

with open("./ittest3/userdata.sh", "r", encoding="utf-8") as file:
    userdata = file.read()

class Ittest3Stack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        myVPC = ec2.Vpc(self, "myVPC", 
        cidr="10.10.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True,
        max_azs=1,
        subnet_configuration=[
            ec2.SubnetConfiguration(
                name="public-subnet1",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=24
            ),
            ec2.SubnetConfiguration(
                name="public-subnet2",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=24
            )
        ])

        ami = ec2.AmazonLinuxImage(cpu_type=ec2.AmazonLinuxCpuType.X86_64,
        edition=ec2.AmazonLinuxEdition.STANDARD,
        generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
        storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        virtualization=ec2.AmazonLinuxVirt.HVM
        )

        volume = ec2.BlockDevice(device_name="/dev/xvda",
        volume=ec2.BlockDeviceVolume.ebs(volume_size=10, 
        volume_type=ec2.EbsDeviceVolumeType.GP3),
        mapping_enabled=True)
        
        mysg = ec2.SecurityGroup(self, "mySG",
        vpc=myVPC,
        allow_all_outbound=True,
        description="CDK create security group",
        security_group_name="ec2-sg1")

        mysg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))
        mysg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))

        myec2 = ec2.Instance(self, "myEC2",
        instance_type=ec2.InstanceType("t3.micro"),
        machine_image=ami,
        vpc=myVPC,
        allow_all_outbound=True,
        block_devices=[volume],
        instance_name="myEC2",
        key_name="itdemo",
        security_group=mysg,
        vpc_subnets=ec2.SubnetSelection(subnet_group_name="public-subnet1"),
        user_data=ec2.UserData.custom(userdata),
        )

        core.CfnOutput(self, "publicIP", value=myec2.instance_public_ip)
        core.CfnOutput(self, "publicDNS", value=myec2.instance_public_dns_name)
        core.CfnOutput(self, "privateIP", value=myec2.instance_private_ip)
        core.CfnOutput(self, "privateDNS", value=myec2.instance_private_dns_name)