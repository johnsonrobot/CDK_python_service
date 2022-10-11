from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_autoscaling as auto,
    core
)


class EcsTestStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        vpc = ec2.Vpc(self, "vpc", 
        cidr="10.10.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True,
        max_azs=1,
        nat_gateways=0,
        subnet_configuration=[
            ec2.SubnetConfiguration(name="public1",
            subnet_type=ec2.SubnetType.PUBLIC,
            cidr_mask=24)
        ])

        block = auto.BlockDevice(device_name="/dev/xvda",
        volume=auto.BlockDeviceVolume.ebs(volume_size=30, volume_type=auto.EbsDeviceVolumeType.GP3),
        mapping_enabled=True)

        cluster = ecs.Cluster(self, "Cluster", cluster_name="itdemo-cdk", vpc=vpc,
        capacity=ecs.AddCapacityOptions(
            can_containers_access_instance_role=True,
            instance_type=ec2.InstanceType("t3.micro"),
            desired_capacity=1,
            machine_image_type=ecs.MachineImageType.AMAZON_LINUX_2,
            key_name="itdemo",
            block_devices=[block]))
        
        cluster.connections.allow_from_any_ipv4(ec2.Port.all_traffic())
        
        task1 = ecs.TaskDefinition(self, "task-cdk",
        network_mode=ecs.NetworkMode.BRIDGE, 
        compatibility=ecs.Compatibility.EC2,
        cpu="256",
        memory_mib="512")
        
        task1.add_container("Application",
        memory_limit_mib=128,
        # image=ecs.ContainerImage.from_registry("httpd:2.4"),
        image=ecs.ContainerImage.from_registry("johnson860312/awswebdb")
        # entry_point=["sh", "-c"],
        # command=["/bin/sh -c \"echo '<html> <head> <title>Amazon ECS Sample App</title> <style>body {margin-top: 40px; background-color: #333;} </style> </head><body> <div style=color:white;text-align:center> <h1>Amazon ECS Sample App</h1> <h2>Congratulations!</h2> <p>Your application is now running on a container in Amazon ECS.</p> </div></body></html>' > /usr/local/apache2/htdocs/index.html && httpd-foreground\""],
        ).add_port_mappings(ecs.PortMapping(container_port=80, 
        host_port=80, 
        protocol=ecs.Protocol.TCP))        

        ecs.Ec2Service(self, "Service",
        cluster=cluster,
        task_definition=task1,
        desired_count=1,
        service_name="SVC-CDK",
        ) 