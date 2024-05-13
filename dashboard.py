import streamlit as st
import datetime as dt
import pandas as pd
import datetime
import plotly.express as px
from helpers import *
from plotly import graph_objects as go

dfs = df_connect()

left, middle, right = st.columns(3)

with left:
    st.header("Full Payment Sales")

    payment_df = pd.merge(dfs['transactions'], dfs['pp_users'], left_on='user_id', right_on='id')
    full_df = payment_df.query('payment_status == "success" & installment_user == 0')[['displayname', 'email', 'phone_number', 'updated_at_x', 'amount']]

    full_chart = payment_df[['updated_at_x', 'amount']].resample('D', on='updated_at_x').count().reset_index().rename(columns={"amount": "count"})
    full_fig = px.line(full_chart, x='updated_at_x', y='count', title='Full Payment Sales')
    full_fig.update_layout(showlegend=False, xaxis_title="Date", yaxis_title="Transactions")
    st.plotly_chart(full_fig, use_container_width=True)

    latest = full_df['updated_at_x'].max()
    week1_ago = latest - dt.timedelta(days=7)
    week2_ago = week1_ago - dt.timedelta(days=7)

    this_week_sales = sum((full_df['updated_at_x'] >= week1_ago) & (full_df['updated_at_x'] <= latest))
    last_week_sales = sum((full_df['updated_at_x'] >= week2_ago) & (full_df['updated_at_x'] <= week1_ago))

    st.metric('Total Sales', len(full_df), '{0}%'.format(weird_division(this_week_sales, last_week_sales)))
    
    st.write(full_df)

with middle:
    st.header("Installment Sales")

    installment_status_df = dfs['user_payments'].groupby('user_installment_id').agg({'created_date':'last', 'status':installment_status}).reset_index()
    installment_df = pd.merge(dfs['installments'], dfs['installment_users'], left_on='user_info_id', right_on='id')
    installment_df = pd.merge(installment_df, dfs['pp_users'], left_on='planet_persib_user_id', right_on='id')
    installment_df = pd.merge(installment_df, installment_status_df, left_on='id_x', right_on='user_installment_id')

    installment_status_df = pd.DataFrame(installment_df['status'].value_counts()).reset_index()
    installment_status_fig = px.pie(installment_status_df, names='status', values='count', title='Installment Status Distribution')
    st.plotly_chart(installment_status_fig, use_container_width=True)

    st.metric('Total Installment Users', len(installment_df), '{0}%'.format('?'))
    st.write(installment_df[['displayname', 'email', 'phone_number', 'address', 'down_payment', 'monthly_payment','tenor','created_date','status']])

with right:
    st.header("Engagement")

    col1, col2, col3 = st.columns(3)
    col1.metric('Waitlisted Emails', 10696, '{0}%'.format('?'))
    col2.metric('Followers', 10696, '{0}%'.format('?'))
    col3.metric('Etc', 10696, '{0}%'.format('?'))

    st.chat_message("user").write("Some random message to contact@planetpersib.com")
    st.chat_message("user").write("Some random comment from IG @planetpersib")
    st.chat_message("user").write("Some random Whatsapp Message")

    st.header("PlanetPersib.com Funnels")

    funnel_fig = go.Figure(go.Funnel(
        y = ["Homepage", "Minting Page", "Payment Options", "Price Menu", "Review Order", "Successful Transaction"],
        x = [6634, 1768, 613, 551, 39, 12],
        textposition = "auto",
        textinfo = "value+percent previous")
        )
    funnel_fig.update_layout(
        title="PlanetPersib Sales Funnel (May 2-7, 2024)",
    )
    funnel_fig.update_traces(texttemplate='%{value:,2s} <br> %{percentPrevious:.1%}')

    st.plotly_chart(funnel_fig, use_container_width=True)