import toml
import paramiko
from sshtunnel import SSHTunnelForwarder
import streamlit as st
from random import randrange
 
with open('connection.toml', 'r') as f:
    st.secrets = toml.load(f)

tunnels = {'ansi': SSHTunnelForwarder(
        (st.secrets['tunnel']['hostname'], 22),
        ssh_username=st.secrets['tunnel']['username'],
        ssh_pkey=paramiko.Ed25519Key.from_private_key_file(st.secrets['tunnel']['pkey']),
        remote_bind_address=(st.secrets['ansi']['hostname'], int(st.secrets['ansi']['port'])),
        local_bind_address=('localhost',randrange(6500,6600)),
        ),
        'installment': SSHTunnelForwarder(
        (st.secrets['tunnel']['hostname'], 22),
        ssh_username=st.secrets['tunnel']['username'],
        ssh_pkey=paramiko.Ed25519Key.from_private_key_file(st.secrets['tunnel']['pkey']),
        remote_bind_address=(st.secrets['installment']['hostname'], int(st.secrets['installment']['port'])),
        local_bind_address=('localhost',randrange(6500,6600)),
        )}

@st.cache_data(ttl=1800)
def df_connect():
    if st.secrets['local']:
        tunnels = {'ansi': SSHTunnelForwarder(
        (st.secrets['tunnel']['hostname'], 22),
        ssh_username=st.secrets['tunnel']['username'],
        ssh_pkey=paramiko.Ed25519Key.from_private_key_file(st.secrets['tunnel']['pkey']),
        remote_bind_address=(st.secrets['ansi']['hostname'], int(st.secrets['ansi']['port'])),
        local_bind_address=('localhost',randrange(6500,6600)),
        ),
        'installment': SSHTunnelForwarder(
        (st.secrets['tunnel']['hostname'], 22),
        ssh_username=st.secrets['tunnel']['username'],
        ssh_pkey=paramiko.Ed25519Key.from_private_key_file(st.secrets['tunnel']['pkey']),
        remote_bind_address=(st.secrets['installment']['hostname'], int(st.secrets['installment']['port'])),
        local_bind_address=('localhost',randrange(6500,6600)),
        )}

        with tunnels['ansi'] as tunnel:
            conn = st.connection("ansi", type="sql", host=tunnel.local_bind_host, port=tunnel.local_bind_port,)
            transaction_df = conn.query('select * from purchase_transactions')
            user_df = conn.query('select * from users')
            #st.write(conn.query('select * from waitlists'))
        
        with tunnels['installment'] as tunnel:
            conn = st.connection("installment", type="sql", host=tunnel.local_bind_host, port=tunnel.local_bind_port,)
            installment_df = conn.query('select * from user_installment')
            user_info_df = conn.query('select * from user_info')
            user_payment_df = conn.query('select * from user_payment')

        return {'transactions': transaction_df,
                'pp_users': user_df,
                'installments': installment_df,
                'installment_users': user_info_df,
                'user_payments': user_payment_df}
    
    else:
        conn = st.connection("postgresql", type="sql", host='persib-db-production-cluster.cluster-ro-cm7jwitr9nnt.ap-southeast-1.rds.amazonaws.com', port=5432,)
        transaction_df = conn.query('select * from purchase_transactions limit 5')
        return transaction_df
    
def installment_status(x):
    unpaid_count = (x == 'UNPAID').sum()
    if unpaid_count >= 3:
        return 'Non-performing'
    elif unpaid_count == 0:
        return 'Ongoing'
    else:
        return 'Payment Due'
    
def weird_division(n, d):
    return (n - d) / d if d else (n - d) / (d+1)