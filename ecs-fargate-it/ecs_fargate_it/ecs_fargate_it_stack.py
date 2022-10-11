from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_rds as rds,
    core
    )

class EcsFargateItStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        
        vpc = ec2.Vpc(self, "VPC", 
        cidr="10.0.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True,
        max_azs=0,
        nat_gateways=1)

        public_subnet = ec2.Subnet(self, "public-subnet1", 
        availability_zone="us-east-2a",
        cidr_block="10.0.10.0/24",
        vpc_id=vpc.vpc_id,
        map_public_ip_on_launch=True)

        public_subnet2 = ec2.Subnet(
            self,
            "PublicSubnet2",
            availability_zone="us-east-2b",
            cidr_block="10.0.20.0/24",
            vpc_id=vpc.vpc_id,
            map_public_ip_on_launch=True
        )

        public_subnet.add_default_internet_route(gateway_id=vpc.internet_gateway_id, gateway_attachment=vpc)
        public_subnet2.add_default_internet_route(gateway_id=vpc.internet_gateway_id, gateway_attachment=vpc)

        sg = ec2.SecurityGroup(self, "CDK-SG", 
        vpc=vpc,
        description="cdk create security group",
        security_group_name="cdkSG")

        sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(80), description="cdk allow anywhere about HTTP protocol")

        alb = elbv2.ApplicationLoadBalancer(self, "CDK-ALB", 
            vpc=vpc,
            internet_facing=True,
            vpc_subnets=ec2.SubnetSelection(
                subnets=[public_subnet, public_subnet2]
            ),
            security_group=sg,
            load_balancer_name="cdkALB"
        )
        
        tg = elbv2.ApplicationTargetGroup(
            self,
            "CDK-TG",
            port= 80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            vpc=vpc
        )

        listener = alb.add_listener(
            "Listener", 
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_target_groups=[tg]
        )

        listener.add_target_groups(
            "CDK-addTG",
            target_groups=[tg]
        )
        

        cluster = ecs.Cluster(self, "Fargate-Cluster",
        enable_fargate_capacity_providers=True,
        vpc=vpc)

        task = ecs.FargateTaskDefinition(self, "fargate-task", 
        cpu=1024,
        memory_limit_mib=2048,
        )

        task.add_container(id="app",
        image=ecs.ContainerImage.from_registry("johnson860312/awswebdb"),
        container_name="mycontainer",
        port_mappings=[
            ecs.PortMapping(container_port=80,
            host_port=80,
            protocol=ecs.Protocol.TCP)
        ],
        cpu=128,
        memory_reservation_mib=256
        )

        svc = ecs.FargateService(self, "fargate-svc",
            task_definition=task,
            cluster=cluster,
            security_groups=[sg],
            assign_public_ip=True,
            vpc_subnets=ec2.SubnetSelection(
                subnets=[public_subnet, public_subnet2]
            ),
            desired_count=2
        )
        
        scale_policy = svc.auto_scale_task_count(
            max_capacity=5,
            min_capacity=1
        )

        scale_policy.scale_on_request_count(
            "asgPolicy",
            requests_per_target=5,
            target_group=tg,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60)
        )

        tg.add_target(svc)

        core.CfnOutput(self, "PublicDNS", value="http://" + listener.load_balancer.load_balancer_dns_name)