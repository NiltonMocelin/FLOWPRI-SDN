ovs-ofctl add-flow s1 ip,nw_dst=172.16.10.1,actions:output=1
ovs-ofctl add-flow s1 ip,nw_dst=172.16.10.4,actions:output=4
ovs-ofctl add-flow s2 ip,nw_dst=172.16.10.1,actions:output=1
ovs-ofctl add-flow s2 ip,nw_dst=172.16.10.4,actions:output=2
ovs-ofctl add-flow s3 ip,nw_dst=172.16.10.1,actions:output=1
ovs-ofctl add-flow s3 ip,nw_dst=172.16.10.4,actions:output=2
ovs-ofctl add-flow s4 ip,nw_dst=172.16.10.1,actions:output=4
ovs-ofctl add-flow s4 ip,nw_dst=172.16.10.4,actions:output=1



