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

        # instantiate VPC with dns support and hostname enabled and cidr block at 10.0.0.0/24
        vpc = ec2.Vpc(self, "vpc-cf",
                      cidr="10.0.0.0/24",
                      enable_dns_support=True,
                      enable_dns_hostnames=True
                      )

        # instantiate internet gateway and attach VPC with internet gateway
        igw = ec2.CfnInternetGateway(self, "igw")
        igw_attach = ec2.CfnVPCGatewayAttachment(
            self, "igw_attach", vpc_id=vpc.vpc_id, internet_gateway_id=igw.attr_internet_gateway_id)

        # instantiate elastic IP with VPC domin
        eip = ec2.CfnEIP(self, "eip", domain="VPC")

        # instantiate public and private subnets and use first availability zone
        pub_subnetA = ec2.Subnet(
            self, "public-subnetA", availability_zone=super().availability_zones[0], cidr_block="10.0.0.0/26", vpc_id=vpc.vpc_id, map_public_ip_on_launch=True)
        pub_subnetB = ec2.Subnet(
            self, "public-subnetB", availability_zone=super().availability_zones[0], cidr_block="10.0.0.64/26", vpc_id=vpc.vpc_id, map_public_ip_on_launch=True)
        pri_subnetA = ec2.Subnet(
            self, "private-subnetA", availability_zone=super().availability_zones[0], cidr_block="10.0.0.128/26", vpc_id=vpc.vpc_id, map_public_ip_on_launch=False)
        pri_subnetB = ec2.Subnet(
            self, "private-subnetB", availability_zone=super().availability_zones[0], cidr_block="10.0.0.192/26", vpc_id=vpc.vpc_id, map_public_ip_on_launch=False)

        # instantiate NAT gateway
        nat_gateway = ec2.CfnNatGateway(
            self, "nat_gateway", allocation_id=eip.attr_allocation_id, subnet_id=pub_subnetA.subnet_vpc_id)

        # instantiate routing tables
        pub_route_table = ec2.CfnRouteTable(
            self, "pub_route_table", vpc_id=vpc.vpc_id)
        pri_route_table = ec2.CfnRouteTable(
            self, "pri_route_table", vpc_id=vpc.vpc_id)

        # instantiate public and private routes
        pub_route = ec2.CfnRoute(self, "pub_route", route_table_id=pub_route_table.attr_route_table_id,
                                 destination_cidr_block="0.0.0.0/0", gateway_id=igw.attr_internet_gateway_id)
        pri_route = ec2.CfnRoute(self, "pri_route", route_table_id=pri_route_table.attr_route_table_id,
                                 destination_cidr_block="0.0.0.0/0", nat_gateway_id=nat_gateway.ref)

        # instantiate subnet route table associations
        pub_subnetA_route_table_association = ec2.CfnSubnetRouteTableAssociation(
            self, "pub_subnetA_route_table_association", route_table_id=pub_route_table.attr_route_table_id, subnet_id=pub_subnetA.subnet_vpc_id)
        pub_subnetB_route_table_association = ec2.CfnSubnetRouteTableAssociation(
            self, "pub_subnetB_route_table_association", route_table_id=pub_route_table.attr_route_table_id, subnet_id=pub_subnetB.subnet_vpc_id)
        pri_subnetA_route_table_association = ec2.CfnSubnetRouteTableAssociation(
            self, "pri_subnetA_route_table_association", route_table_id=pri_route_table.attr_route_table_id, subnet_id=pri_subnetA.subnet_vpc_id)
        pri_subnetB_route_table_association = ec2.CfnSubnetRouteTableAssociation(
            self, "pri_subnetB_route_table_association", route_table_id=pri_route_table.attr_route_table_id, subnet_id=pri_subnetB.subnet_vpc_id)

        security_group = ec2.SecurityGroup(self, "security_group", vpc=vpc)
        security_group.add_ingress_rule(
            ec2.Peer.ipv4("0.0.0.0/0"), ec2.Port.tcp(22))

        ec2_instance = ec2.Instance(self, "EC2", instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO), machine_image=ec2.MachineImage.latest_amazon_linux(),
                                    key_name="KeyPairAcademy", security_group=security_group, vpc=vpc, vpc_subnets=pri_subnetA)
