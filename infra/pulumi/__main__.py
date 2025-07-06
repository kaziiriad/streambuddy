import pulumi
import pulumi_aws as aws
from pulumi_command import local
import os
from dotenv import load_dotenv

# Load environment variables from .env file, assuming it's in the project root
load_dotenv(dotenv_path="../../.env")

# --- Pulumi Configuration ---
django_secret_key = os.getenv("DJANGO_SECRET_KEY")
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_storage_bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
postgres_db = os.getenv("POSTGRES_DB")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT")


# --- VPC Configuration ---
vpc = aws.ec2.Vpc("streambuddy-vpc",
    cidr_block="10.0.0.0/16",
    tags={"Name": "streambuddy-vpc"})

subnet = aws.ec2.Subnet("streambuddy-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    tags={"Name": "streambuddy-public-subnet"})

igw = aws.ec2.InternetGateway("streambuddy-igw",
    vpc_id=vpc.id,
    tags={"Name": "streambuddy-igw"})

route_table = aws.ec2.RouteTable("streambuddy-rt",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=igw.id,
    )],
    tags={"Name": "streambuddy-public-rt"})

aws.ec2.RouteTableAssociation("streambuddy-rta",
    route_table_id=route_table.id,
    subnet_id=subnet.id)

# --- SSH Key Configuration ---
key_pair = aws.ec2.get_key_pair(key_name="streambuddy-dev-key")


# --- Security Group Configuration ---
security_group = aws.ec2.SecurityGroup("web-sg",
    vpc_id=vpc.id,
    description="Enable HTTP and SSH access",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp", from_port=22, to_port=22, cidr_blocks=["0.0.0.0/0"],
            description="Allow SSH",
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp", from_port=8000, to_port=8000, cidr_blocks=["0.0.0.0/0"],
            description="Allow App traffic",
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"],
            description="Allow all outbound traffic",
        ),
    ],
    tags={"Name": "streambuddy-sg"})

# --- AMI and EC2 Instance Configuration ---
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],
    filters=[aws.ec2.GetAmiFilterArgs(name="name", values=["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"])],
)

ec2_instance = aws.ec2.Instance("web-instance",
    instance_type="t2.micro",
    subnet_id=subnet.id,
    vpc_security_group_ids=[security_group.id],
    ami=ami.id,
    key_name=key_pair.key_name,
    tags={"Name": "streambuddy-web-instance"})

# --- Ansible Inventory Generation ---
inventory_content = ec2_instance.public_ip.apply(lambda ip: f"""[web]
{ip}

[web:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/.ssh/streambuddy-dev-key.pem
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
django_secret_key="{django_secret_key}"
allowed_hosts="localhost,127.0.0.1,{ip}"
aws_access_key_id="{aws_access_key_id}"
aws_secret_access_key="{aws_secret_access_key}"
aws_storage_bucket_name="{aws_storage_bucket_name}"
postgres_db="{postgres_db}"
postgres_user="{postgres_user}"
postgres_password="{postgres_password}"
postgres_host="{postgres_host}"
postgres_port="{postgres_port}"
""")

# Create the inventory file using a local command
create_inventory = local.Command("create-inventory",
    create=pulumi.Output.concat("echo '", inventory_content, "' > ../../ansible/inventory"),
    opts=pulumi.ResourceOptions(depends_on=[ec2_instance])
)

# --- Ansible Provisioning ---
ansible_provisioner = local.Command("ansible-provisioner",
    create="ansible-playbook -i ../../ansible/inventory ../../ansible/playbook.yml",
    opts=pulumi.ResourceOptions(depends_on=[create_inventory])
)

# --- Exports ---
pulumi.export("public_ip", ec2_instance.public_ip)
pulumi.export("ssh_command", pulumi.Output.concat("ssh -i ~/.ssh/streambuddy-dev-key.pem ubuntu@", ec2_instance.public_ip))