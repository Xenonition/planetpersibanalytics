import streamlit as st
import datetime as dt
import pandas as pd
import datetime
import plotly.express as px

po_conn = st.connection("postgresql", type="sql")
transaction_df = po_conn.query('SELECT * FROM purchase_transactions', ttl="30m")[['user_id', 'amount', 'created_at', 'payment_status']]
user_df = po_conn.query('SELECT * FROM users', ttl="30m")[['id','displayname', 'email', 'phone_number']]

out_df = transaction_df.set_index('user_id').join(user_df.set_index('id'))[['displayname', 'email', 'phone_number','amount', 'created_at', 'payment_status']]
st.write(out_df)

growth_chart = out_df[out_df['payment_status'] == 'success'][['created_at', 'payment_status']].resample('D', on='created_at').count().reset_index().rename(columns={"payment_status": "count"})
growth_fig = px.line(growth_chart, x='created_at', y='count', title='Successful Full Sales')
growth_fig.update_layout(showlegend=False, xaxis_title="Date", yaxis_title="NFT Sales")
st.plotly_chart(growth_fig)