from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
    core
)


class Ec2Stack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        vpc = ec2.Vpc(self, "CDK-VPC",
                      max_azs=1,
                      nat_gateways=0,
                      subnet_configuration=[ec2.SubnetConfiguration(
                          name="public", subnet_type=ec2.SubnetType.PUBLIC)],
                      cidr="10.10.0.0/16"
                      )

        ami = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )
        sg = ec2.SecurityGroup(self, "CDK-sg",
                               vpc=vpc,
                               description="CDK configure security group",
                               security_group_name="CDK-SG",
                               allow_all_outbound=True,
                               )
        myip_cidr = ""
        sg.add_ingress_rule(ec2.Peer.ipv4(myip_cidr),
                            ec2.Port.tcp(22), "allow home ip to remote")
        sg.add_ingress_rule(ec2.Peer.ipv4(myip_cidr),
                            ec2.Port.all_icmp(), "allow icmp from home")
        # problem
        # role = iam.Role(self, "CDK-Instance-SSM",
        # assumed_by=iam.ServicePrincipal("ec2.amazons.com"))

        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
        # "AmazonSSManagedInstanceCore"))
        # -------------------------------------------------------------------------
        instance = ec2.Instance(self, "CDK-Instance",
                                instance_type=ec2.InstanceType("t3.micro"),
                                machine_image=ami,
                                vpc=vpc,
                                # vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                security_group=sg,
                                key_name="johnsonkeypair",
                                # role=role
                                )

        instance.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80), "allow http from world")
        instance.connections.allow_from_any_ipv4(
            ec2.Port.tcp(443), "allow https from world")
        core.CfnOutput(self, "Instance",
                       value=instance.instance_public_ip,
                       description="Instance's Public IP")
