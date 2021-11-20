from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
# from aws_cdk import core


class CdkWorkshop3Stack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # COPY LINES FROM BELOW HERE

        vpc = ec2.Vpc(self, "vpc-cf",
                      cidr="10.0.0.0/24",
                      enable_dns_support=True,
                      enable_dns_hostnames=True,
                      nat_gateways=1,
                      max_azs=1,
                      subnet_configuration=[ec2.SubnetConfiguration(
                          name="public-subnetA",
                          cidr_mask=26,
                          subnet_type=ec2.SubnetType.PUBLIC
                      ), ec2.SubnetConfiguration(
                          name="public-subnetB",
                          cidr_mask=26,
                          subnet_type=ec2.SubnetType.PUBLIC
                      ), ec2.SubnetConfiguration(
                          name="private-subnetA",
                          cidr_mask=26,
                          subnet_type=ec2.SubnetType.PRIVATE
                      ), ec2.SubnetConfiguration(
                          name="private-subnetB",
                          cidr_mask=26,
                          subnet_type=ec2.SubnetType.PRIVATE)]
                      )

        ec2_instance = ec2.Instance(self, "EC2", instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO), machine_image=ec2.MachineImage.latest_amazon_linux(
        ), key_name="KeyPair2", vpc=vpc, vpc_subnets=vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnets[0])

        ec2_instance.connections.allow_from_any_ipv4(
            ec2.Port.tcp(22), 'Allow inbound SSH from anywhere')
