-- Add endpoint
INSERT INTO ps_endpoints (id, transport, aors, auth, context, disallow, allow, direct_media) 
VALUES ('200005', 'transport-udp', '200005', '200005', 'testing', 'all', 'opus,ulaw,alaw', 'no');

-- Add AOR (Address of Record)
INSERT INTO ps_aors (id, max_contacts, qualify_frequency) 
VALUES ('200005', 1, 30);

-- Add authentication
INSERT INTO ps_auths (id, auth_type, password, username) 
VALUES ('200005', 'userpass', 'pass200005', '200005');