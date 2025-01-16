import pandas as pd
import numpy as np
import streamlit as st
import datetime
import math
import copy
import timeit
import itertools
# from sqlalchemy import create_engine
import subprocess
import sys
import plotly.express as px
import plotly.graph_objects as go
import locale
from streamlit_option_menu import option_menu


selected = option_menu(
        menu_title="Choose the information which is needed", 
        options=["Expense Comparison - Actual vs Expected", "Item Movement YTD", "Item Movement MTM"],
        menu_icon="cloudy-fill",
        default_index=0,
        orientation="horizontal",
        styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "20px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "green"},
    }
    )

pd.set_option('display.max_columns', None)

def round_school(x):
    i, f = divmod(x, 1)
    return int(i + ((f >= 0.5) if (x > 0) else (f > 0.5)))

def round_school_sig(x,y):
    x    = int(x * 10 ** (y + 1)) / 10
    i, f = divmod(x, 1)
    return int(i + ((f >= 0.5) if (x > 0) else (f > 0.5))) / (10 ** y)

begin_date                  = datetime.datetime(2024, 1, 1)
end_date                    = datetime.datetime(2024, 12, 1)

LRKJ_2023                   = pd.read_csv("streamlit_output_rev/LRKJ_2023.csv")
LRKJ_2023['IFRS_MONTH']     = pd.to_datetime(LRKJ_2023['IFRS_MONTH'], errors='coerce', format='%Y-%m-%d')

LRKJ_2023_Gabungan          = LRKJ_2023[LRKJ_2023["Uraian"] == "Gabungan"]
LRKJ_2023_Tradisional       = LRKJ_2023[LRKJ_2023["Uraian"] == "Tradisional"]
LRKJ_2023_PAYDI             = LRKJ_2023[LRKJ_2023["Uraian"] == "PAYDI"]


LRKJ_2024                   = pd.read_csv("streamlit_output_rev/LRKJ_2024.csv")
LRKJ_2024['IFRS_MONTH']     = pd.to_datetime(LRKJ_2024['IFRS_MONTH'], errors='coerce', format='%Y-%m-%d')
LRKJ_2024                   = LRKJ_2024.drop(LRKJ_2024[LRKJ_2024.IFRS_MONTH < begin_date].index)
LRKJ_2024                   = LRKJ_2024.drop(LRKJ_2024[LRKJ_2024.IFRS_MONTH > end_date].index)
LRKJ_2024                   = LRKJ_2024.reset_index(drop=True)

LRKJ_2024_Gabungan          = LRKJ_2024[LRKJ_2024["Uraian"] == "Gabungan"]
LRKJ_2024_Tradisional       = LRKJ_2024[LRKJ_2024["Uraian"] == "Tradisional"]
LRKJ_2024_PAYDI             = LRKJ_2024[LRKJ_2024["Uraian"] == "PAYDI"]
IFRS_MONTH_list             = LRKJ_2024_Gabungan['IFRS_MONTH'].tolist()
date_list                   = [x.strftime("%B-%Y") for x in IFRS_MONTH_list]
date_month_list             = [x.strftime("%B") for x in IFRS_MONTH_list]
length                      = len(IFRS_MONTH_list)

balance_sheet                   = pd.read_csv("streamlit_output_rev/balance_sheet_total.csv")
balance_sheet['IFRS_MONTH']     = pd.to_datetime(balance_sheet['IFRS_MONTH'], errors='coerce', format='%Y-%m-%d')
balance_sheet_2023_12           = balance_sheet.drop(balance_sheet[balance_sheet.IFRS_MONTH != begin_date].index)
balance_sheet                   = balance_sheet.drop(balance_sheet[balance_sheet.IFRS_MONTH < begin_date].index)
balance_sheet                   = balance_sheet.drop(balance_sheet[balance_sheet.IFRS_MONTH > end_date].index)
balance_sheet                   = balance_sheet.reset_index(drop=True)
balance_sheet_summary           = balance_sheet[["IFRS_MONTH", "Ekspektasi Klaim & Beban Attributable (Estimasi)", "Perubahan pada Penyesuaian Risiko (RA)", "Perubahan pada CSM (Amortisasi)", 
                                                 "Ekspektasi Klaim", "Ekspektasi Komisi", "Ekspektasi Beban Attributable", "Arus Kas Akuisisi Asuransi", 
                                                 "Liabilitas Kontrak Asuransi (Saldo Awal)", "Aset Kontrak Asuransi (Saldo Awal)", "Saldo Bersih Kontrak Asuransi (Saldo Awal)", 
                                                 "Liabilitas Kontrak Asuransi (Saldo Akhir)", "Aset Kontrak Asuransi (Saldo Akhir)", "Saldo Bersih Kontrak Asuransi (Saldo Akhir)"]]
balance_sheet_summary           = balance_sheet_summary.groupby(by=["IFRS_MONTH"]).sum().reset_index()

balance_sheet_PAA               = pd.read_csv("streamlit_output_rev/balance_sheet_total_PAA.csv")
balance_sheet_PAA['IFRS_MONTH'] = pd.to_datetime(balance_sheet_PAA['IFRS_MONTH'], errors='coerce', format='%Y-%m-%d')
balance_sheet_PAA_2023_12       = balance_sheet_PAA.drop(balance_sheet_PAA[balance_sheet_PAA.IFRS_MONTH != begin_date].index)
balance_sheet_PAA               = balance_sheet_PAA.drop(balance_sheet_PAA[balance_sheet_PAA.IFRS_MONTH < begin_date].index)
balance_sheet_PAA               = balance_sheet_PAA.drop(balance_sheet_PAA[balance_sheet_PAA.IFRS_MONTH > end_date].index)
balance_sheet_PAA               = balance_sheet_PAA.reset_index(drop=True)
balance_sheet_PAA_summary       = balance_sheet_PAA[["IFRS_MONTH", 
                                                     "Ekspektasi Klaim", "Ekspektasi Komisi", "Ekspektasi Beban Attributable", "Arus Kas Akuisisi Asuransi", 
                                                     "Liabilitas Kontrak Asuransi (Saldo Awal)", "Aset Kontrak Asuransi (Saldo Awal)", "Saldo Bersih Kontrak Asuransi (Saldo Awal)", 
                                                     "Liabilitas Kontrak Asuransi (Saldo Akhir)", "Aset Kontrak Asuransi (Saldo Akhir)", "Saldo Bersih Kontrak Asuransi (Saldo Akhir)"]]
balance_sheet_PAA_summary       = balance_sheet_PAA_summary.groupby(by=["IFRS_MONTH"]).sum().reset_index()

csm_total                   = pd.read_csv("streamlit_output_rev/csm_total.csv")
csm_total['IFRS_MONTH']     = pd.to_datetime(csm_total['IFRS_MONTH'], errors='coerce', format='%Y-%m-%d')
csm_total_2023_12           = csm_total.drop(csm_total[csm_total.IFRS_MONTH >= begin_date].index)
csm_total                   = csm_total.drop(csm_total[csm_total.IFRS_MONTH < begin_date].index)
csm_total                   = csm_total.drop(csm_total[csm_total.IFRS_MONTH > end_date].index)
csm_summary                 = csm_total.drop(columns=['NAMA_PRODUK'])
csm_summary                 = csm_summary.groupby(by=["IFRS_MONTH"]).sum().reset_index()
csm_summary                 = csm_summary.reset_index(drop=True)

claim_risk_act_prv              = LRKJ_2023_Tradisional['Klaim_dan_Manfaat_Dibayar'].tolist()
acquisition_cost_act_prv        = LRKJ_2023_Gabungan['Jumlah_Biaya_Akuisisi'].tolist()
general_expense_act_prv         = LRKJ_2023_Gabungan['Beban_Umum_dan_Administrasi'].tolist()
inv_inc_list_prv                = LRKJ_2023_Tradisional['Hasil_Investasi'].tolist()
inv_inc_list_prv                = inv_inc_list_prv[:length]

claim_risk_act                  = LRKJ_2024_Tradisional['Klaim_dan_Manfaat_Dibayar'].tolist()
acquisition_cost_act            = LRKJ_2024_Gabungan['Jumlah_Biaya_Akuisisi'].tolist()
general_expense_act             = LRKJ_2024_Gabungan['Beban_Umum_dan_Administrasi'].tolist()
inv_inc_list                    = LRKJ_2024_Tradisional['Hasil_Investasi'].tolist()

claim_risk_exp_month            = balance_sheet_summary['Ekspektasi Klaim'].tolist()
acquisition_cost_exp_month      = [-x for x in balance_sheet_summary['Arus Kas Akuisisi Asuransi'].tolist()]
# acquisition_cost_exp_month      = [x for x in balance_sheet_summary['Ekspektasi Komisi'].tolist()]
general_expense_exp_month       = balance_sheet_summary['Ekspektasi Beban Attributable'].tolist()
claim_expense_exp_month         = balance_sheet_summary['Ekspektasi Klaim & Beban Attributable (Estimasi)'].tolist()
ra_release_exp_month            = balance_sheet_summary['Perubahan pada Penyesuaian Risiko (RA)'].tolist()
csm_release_month               = balance_sheet_summary['Perubahan pada CSM (Amortisasi)'].tolist()

claim_risk_exp_month_PAA        = balance_sheet_PAA_summary['Ekspektasi Klaim'].tolist()
acquisition_cost_exp_month_PAA  = [x for x in balance_sheet_PAA_summary['Arus Kas Akuisisi Asuransi'].tolist()]
general_expense_exp_month_PAA   = balance_sheet_PAA_summary['Ekspektasi Beban Attributable'].tolist()

Liabilitas_2023_12              = sum(balance_sheet_2023_12['Saldo Bersih Kontrak Asuransi (Saldo Awal)']) / 1000000
Aset_2023_12                    = sum(balance_sheet_2023_12['Aset Kontrak Asuransi (Saldo Awal)']) / 1000000
Liabilitas_2023_12_PAA          = sum(balance_sheet_PAA_2023_12['Saldo Bersih Kontrak Asuransi (Saldo Awal)']) / 1000000
Aset_2023_12_PAA                = sum(balance_sheet_PAA_2023_12['Aset Kontrak Asuransi (Saldo Awal)']) / 1000000
csm_total_2023_12               = sum(csm_total_2023_12['Contractual Service Margin']) / 1000000

Liabilitas_list_PAA             = [x / 1000000 for x in balance_sheet_PAA_summary['Saldo Bersih Kontrak Asuransi (Saldo Akhir)'].tolist()]
Aset_list_PAA                   = [x / 1000000 for x in balance_sheet_PAA_summary['Aset Kontrak Asuransi (Saldo Akhir)'].tolist()]
Liabilitas_list                 = [x / 1000000 for x in balance_sheet_summary['Saldo Bersih Kontrak Asuransi (Saldo Akhir)'].tolist()]
Aset_list                       = [x / 1000000 for x in balance_sheet_summary['Aset Kontrak Asuransi (Saldo Akhir)'].tolist()]

Liabilitas_list                 = [x + y for x, y in zip(Liabilitas_list_PAA, Liabilitas_list)]
Aset_list                       = [x + y for x, y in zip(Aset_list_PAA, Aset_list)]
csm_list                        = [x / 1000000 for x in csm_summary['Contractual Service Margin'].tolist()]
premium_Traditional             = LRKJ_2024_Tradisional['Pendapatan_premi'].tolist()
premium_UL                      = LRKJ_2024_PAYDI['Pendapatan_premi'].tolist()

date_list_add                   = [datetime.datetime(2023, 12, 1).strftime("%B-%Y")] + date_list
Liabilitas_list_add             = [Liabilitas_2023_12 + Liabilitas_2023_12_PAA] + Liabilitas_list
Aset_list_add                   = [Aset_2023_12 + Aset_2023_12_PAA] + Aset_list
csm_list_add                    = [csm_total_2023_12] + csm_list

claim_risk_exp                  = np.cumsum(claim_risk_exp_month)
acquisition_cost_exp            = np.cumsum(acquisition_cost_exp_month)
general_expense_exp             = np.cumsum(general_expense_exp_month)

claim_risk_exp_PAA              = np.cumsum(claim_risk_exp_month_PAA)
acquisition_cost_exp_PAA        = np.cumsum(acquisition_cost_exp_month_PAA)
general_expense_exp_PAA         = np.cumsum(general_expense_exp_month_PAA)

claim_risk_exp                  = [(x + y) / 1000000 for x, y in zip(claim_risk_exp, claim_risk_exp_PAA)]
acquisition_cost_exp            = [(x + y) / 1000000 for x, y in zip(acquisition_cost_exp, acquisition_cost_exp_PAA)]
general_expense_exp             = [(x + y) / 1000000 for x, y in zip(general_expense_exp, general_expense_exp_PAA)]

claim_act_exp                   = [x / y * 100 for x, y in zip(claim_risk_act, claim_risk_exp)]
acquisition_cost_act_exp        = [x / y * 100 for x, y in zip(acquisition_cost_act, acquisition_cost_exp)]
general_expense_act_exp         = [x / y * 100 for x, y in zip(general_expense_act, general_expense_exp)]

###############################################################################################################################################
if selected == "Expense Comparison - Actual vs Expected":
    
    st.write("## Claim Comparison - Expected vs Actual")
    st.write("### Claim Comparison year-to-date is " + f"{claim_act_exp[length - 1]:,.2f}" +" %")
    fig = go.Figure(data=[
        go.Bar(name='claim risiko actual', x=date_list[length - 1:], y=claim_risk_act[length - 1:], 
            text=f"{claim_risk_act[length - 1]:,.2f}" + " million", textposition='inside', insidetextanchor='middle', marker=dict(color='#ffe599'), 
            textfont=dict(
                size=24,  # Text size
                family='Calibri',  # Font family
                color='black',  # Text color
            )),
        go.Bar(name='claim risiko expected', x=date_list[length - 1:], y=list(claim_risk_exp[length - 1:]), 
            text=f"{claim_risk_exp[length - 1]:,.2f}" + " million", textposition='inside', insidetextanchor='middle', marker=dict(color='#bcbcbc'), 
            textfont=dict(
                size=24,  # Text size
                family='Calibri',  # Font family
                color='black',  # Text color
            ))
    ])

    # Update layout for better visualization
    fig.update_layout(
        barmode='group',
        title='',
        xaxis_title='Date',
        yaxis_title='Claim Value'
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    st.write("### Claim Comparison History")
    # Create the grouped bar chart
    fig = go.Figure(data=[
        go.Bar(name='claim risiko actual', x=date_list, y=claim_risk_act),
        go.Bar(name='claim risiko expected', x=date_list, y=list(claim_risk_exp))
    ])

    # Update layout for better visualization
    fig.update_layout(
        barmode='group',
        title='',
        xaxis_title='Date',
        yaxis_title='Claim Value'
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)


    data_claim = {
        'Date'                              : date_list,
        'claim risiko actual'               : claim_risk_act,
        'claim risiko expected'             : list(claim_risk_exp),
        'claim risiko - actual vs expected' : [f"{p:.2f}" + " %" for p in claim_act_exp]  # Format percentages
    }
    st.dataframe(data_claim, use_container_width=True)


    st.write("## Acqusition Cost Comparison - Expected vs Actual")
    st.write("### Acqusition Cost Comparison year-to-date " + f"{acquisition_cost_act_exp[length - 1]:,.2f}" +" %")
    fig = go.Figure(data=[
        go.Bar(name='acquisition cost actual', x=date_list[length - 1:], y=acquisition_cost_act[length - 1:], 
            text=f"{acquisition_cost_act[length - 1]:,.2f}" + " million", textposition='inside', insidetextanchor='middle', marker=dict(color='#ffe599'), 
            textfont=dict(
                size=24,  # Text size
                family='Calibri',  # Font family
                color='black',  # Text color
            )),
        go.Bar(name='acquisition cost expected', x=date_list[length - 1:], y=list(acquisition_cost_exp[length - 1:]), 
            text=f"{acquisition_cost_exp[length - 1]:,.2f}" + " million", textposition='inside', insidetextanchor='middle', marker=dict(color='#bcbcbc'), 
            textfont=dict(
                size=24,  # Text size
                family='Calibri',  # Font family
                color='black',  # Text color
            ))
    ])

    # Update layout for better visualization
    fig.update_layout(
        barmode='group',
        title='',
        xaxis_title='Date',
        yaxis_title='Acquisition Cost'
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    st.write("### Acqusition Cost Comparison History")
    # Create the grouped bar chart
    fig = go.Figure(data=[
        go.Bar(name='acquisition cost actual', x=date_list, y=acquisition_cost_act),
        go.Bar(name='acquisition cost expected', x=date_list, y=list(acquisition_cost_exp))
    ])

    # Update layout for better visualization
    fig.update_layout(
        barmode='group',
        title='',
        xaxis_title='Date',
        yaxis_title='Acquisition Cost'
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    data_acquisition_cost = {
        'Date'                                  : date_list,
        'acquisition cost actual'               : acquisition_cost_act,
        'acquisition cost expected'             : list(acquisition_cost_exp),
        'acquisition cost - actual vs expected' : [f"{p:.2f}" + " %" for p in acquisition_cost_act_exp]  # Format percentages
    }
    st.dataframe(data_acquisition_cost, use_container_width=True)


    st.write("## General Expense Comparison - Expected vs Actual")
    st.write("### General Expense Comparison year-to-date is " + f"{general_expense_act_exp[length - 1]:,.2f}" +" %")
    fig = go.Figure(data=[
        go.Bar(name='acquisition cost actual', x=date_list[length - 1:], y=general_expense_act[length - 1:], 
            text=f"{general_expense_act[length - 1]:,.2f}" + " million", textposition='inside', insidetextanchor='middle', marker=dict(color='#ffe599'), 
            textfont=dict(
                size=24,  # Text size
                family='Calibri',  # Font family
                color='black',  # Text color
            )),
        go.Bar(name='acquisition cost expected', x=date_list[length - 1:], y=list(general_expense_exp[length - 1:]), 
            text=f"{general_expense_exp[length - 1]:,.2f}" + " million", textposition='inside', insidetextanchor='middle', marker=dict(color='#bcbcbc'), 
            textfont=dict(
                size=24,  # Text size
                family='Calibri',  # Font family
                color='black',  # Text color
            ))
    ])

    # Update layout for better visualization
    fig.update_layout(
        barmode='group',
        title='',
        xaxis_title='Date',
        yaxis_title='General Expense'
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    st.write("### General Expense Comparison History")
    # Create the grouped bar chart
    fig = go.Figure(data=[
        go.Bar(name='General Expense actual', x=date_list, y=general_expense_act),
        go.Bar(name='General Expense expected', x=date_list, y=list(general_expense_exp))
    ])

    # Update layout for better visualization
    fig.update_layout(
        barmode='group',
        title='',
        xaxis_title='Date',
        yaxis_title='General Expense'
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    data_general_expense = {
        'Date'                                  : date_list,
        'General Expense actual'                : general_expense_act,
        'General Expense expected'              : list(general_expense_exp),
        'General Expense - actual vs expected'  : [f"{p:.2f}" + " %" for p in general_expense_act_exp]  # Format percentages
    }
    st.dataframe(data_general_expense, use_container_width=True)


print(inv_inc_list[length - 1], inv_inc_list_prv[length - 1])
###############################################################################################################################################
if selected == "Item Movement YTD":

    st.write("## Investment Income")
    compare_inv = (inv_inc_list[length - 1] / inv_inc_list_prv[length - 1] - 1) * 100
    print(compare_inv)
    if compare_inv / 100 >= 0:
        st.write(f"### Investment Income in " + date_month_list[length - 1] + f" increases {compare_inv:,.2f}" + " % " + "compared to the same month in 2023")
    else:
        st.write(f"### Investment Income in " + date_month_list[length - 1] + f" decreases {compare_inv:,.2f}" + " % " + "compared to the same month in 2023")

    # Create the figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=date_month_list, y=inv_inc_list_prv, mode='lines', name='Inv Income 2023'))
    fig.add_trace(go.Scatter(x=date_month_list, y=inv_inc_list, mode='lines', name='Inv Income 2024'))

    # Display the chart
    st.plotly_chart(fig)



    st.write("## Liability Movement - BEL + RA + CSM")
    movement_liability = (Liabilitas_list[length - 1] / (Liabilitas_2023_12 + Liabilitas_2023_12_PAA) - 1) * 100
    if movement_liability / 100 >= 0:
        st.write(f"### Liability increases {movement_liability:,.2f}" + " % " + "compared to the end of 2023")
    else:
        st.write(f"### Liability decreases {movement_liability:,.2f}" + " % " + "compared to the end of 2023")

    data_Liability = {
        'Date'          : date_list_add,
        'Liability'     : Liabilitas_list_add
    }

    # Create the line chart
    fig = px.line(data_Liability, x='Date', y='Liability', title="", markers=True)
    st.plotly_chart(fig)

    st.write("## Asset Movement - Deferred Acquisition Cost")
    movement_asset      = (Aset_list[length - 1] / (Aset_2023_12 + Aset_2023_12_PAA) - 1) * 100
    if movement_asset / 100 >= 0:
        st.write(f"### Asset increases {movement_asset:,.2f}" + " % " + "compared to the end of 2023")
    else:
        st.write(f"### Asset decreases {movement_asset:,.2f}" + " % " + "compared to the end of 2023")

    data_Asset = {
        'Date'          : date_list_add,
        'Asset'         : Aset_list_add
    }

    # Create the line chart
    fig = px.line(data_Asset, x='Date', y='Asset', title="", markers=True)
    st.plotly_chart(fig)

    st.write("## Contractual Service Margin")
    movement_csm      = (csm_list[length - 1] / csm_total_2023_12 - 1) * 100
    if movement_csm / 100 >= 0:
        st.write(f"### CSM increases {movement_csm:,.2f}" + " % " + "compared to the end of 2023")
    else:
        st.write(f"### CSM decreases {movement_csm:,.2f}" + " % " + "compared to the end of 2023")

    data_csm = {
        'Date'          : date_list_add,
        'CSM'           : csm_list_add
    }

    # Create the line chart
    fig = px.line(data_csm, x='Date', y='CSM', title="", markers=True)
    st.plotly_chart(fig)
###############################################################################################################################################
# Define a function to apply color based on value
def highlight_score(val):
    """
    Function to set the color of text based on the score value.
    """
    if val < 50:
        color = 'red'
    elif val >= 50 and val < 80:
        color = 'orange'
    else:
        color = 'green'
    return f'color: {color}'
    
# Function to apply background color
def highlight_cells(value):
    if value["different"] >= 0:
        return "background-color: lightgreen"
    else:
        return "background-color: red"


if selected == "Item Movement MTM":
    st.write("## Item Movement MTM")

    index_pos                   = list(range(0, len(claim_risk_act)))
    inv_inc_list_month          = [inv_inc_list[x] if x == 0 else inv_inc_list[x] - inv_inc_list[x - 1] for x in index_pos]
    claim_risk_act_month        = [claim_risk_act[x] if x == 0 else claim_risk_act[x] - claim_risk_act[x - 1] for x in index_pos]
    acquisition_cost_act_month  = [acquisition_cost_act[x] if x == 0 else acquisition_cost_act[x] - acquisition_cost_act[x - 1] for x in index_pos]
    general_expense_act_month   = [general_expense_act[x] if x == 0 else general_expense_act[x] - general_expense_act[x - 1] for x in index_pos]

    data_item_movement                          = pd.DataFrame()
    data_item_movement['IFRS_MONTH']            = IFRS_MONTH_list
    data_item_movement['Date']                  = date_list
    data_item_movement['Premium Traditional']   = premium_Traditional
    data_item_movement['Premium UL']            = premium_UL
    data_item_movement['Investment Income']     = inv_inc_list_month
    data_item_movement['Claim Risk']            = claim_risk_act_month
    data_item_movement['Acquisition Cost']      = acquisition_cost_act_month
    data_item_movement['General Expense']       = general_expense_act_month
    data_item_movement['Insurance Revenue']     = [x / 1000000 for x in claim_expense_exp_month]
    data_item_movement['Release RA']            = [x / 1000000 for x in ra_release_exp_month]
    data_item_movement['Release CSM']           = [x / 1000000 for x in csm_release_month]

    IFRS_MONTH_data_item        = st.selectbox("SELECT DATE", list(data_item_movement["IFRS_MONTH"].unique())[1:])
    month_IFRS                  = IFRS_MONTH_data_item.month
    year_IFRS                   = IFRS_MONTH_data_item.year
    IFRS_MONTH_data_item_prv    = datetime.datetime(year_IFRS, month_IFRS - 1, 1)
    st.write("### Comparing " + IFRS_MONTH_data_item_prv.strftime("%B-%Y") + " vs " + IFRS_MONTH_data_item.strftime("%B-%Y"))

    filtered_data_item                  = data_item_movement.drop(data_item_movement[data_item_movement.IFRS_MONTH < IFRS_MONTH_data_item_prv].index)
    filtered_data_item                  = filtered_data_item.drop(filtered_data_item[filtered_data_item.IFRS_MONTH > IFRS_MONTH_data_item].index)
    filtered_data_transposed            = filtered_data_item.T
    filtered_data_transposed            = filtered_data_transposed.reset_index()
    filtered_data_date_list             = filtered_data_item['Date'].tolist()
    filtered_data_transposed.columns    = ["Item"] + filtered_data_date_list
    filtered_data_transposed            = filtered_data_transposed.iloc[2:, 0:]
    filtered_data_transposed            = filtered_data_transposed.reset_index(drop=True)
    
                    
    filtered_data_transposed['different']              = filtered_data_transposed[filtered_data_date_list[1]] - filtered_data_transposed[filtered_data_date_list[0]]
    filtered_data_transposed['different (%)']               = filtered_data_transposed['different'] / filtered_data_transposed[filtered_data_date_list[0]]
    # filtered_data_transposed[filtered_data_date_list[0]]    = [f"{x:,.2f}" for x in filtered_data_transposed[filtered_data_date_list[0]].tolist()]
    # filtered_data_transposed[filtered_data_date_list[1]]    = [f"{x:,.2f}" for x in filtered_data_transposed[filtered_data_date_list[1]].tolist()]
    
    
    # # filtered_data_transposed   = filtered_data_transposed.style.applymap(highlight_cells, subset=["different (%)"])
    styled_df   = filtered_data_transposed.style.apply(lambda value: [highlight_cells(value) if col == "different" or col == "different (%)" else "" for col in filtered_data_transposed.columns], axis=1,)
    styled_df   = styled_df.format({
        "different"                 : "{:.2f}",     # Display scores with 2 decimal places
        "different (%)"             : "{:.2%}",     # Display percentages in percentage format
        filtered_data_date_list[0]  :"{:.2f}",
        filtered_data_date_list[1]  :"{:.2f}"
        })
    # # Display the styled DataFrame in Streamlit
    st.dataframe(styled_df, use_container_width=True)



    # Generate data for animation
    x = np.linspace(0, 2 * np.pi, 100)
    frames = []

    # Create frames for animation
    for i in range(1, 50):
        y1 = np.sin(x + i / 10.0)
        y2 = np.cos(x + i / 10.0)
        frames.append(go.Frame(data=[
            go.Scatter(x=x, y=y1, mode='lines', name='Sine'),
            go.Scatter(x=x, y=y2, mode='lines', name='Cosine')
        ]))

    # Create the figure
    fig = go.Figure(
        data=[
            go.Scatter(x=x, y=np.sin(x), mode='lines', name='Sine'),
            go.Scatter(x=x, y=np.cos(x), mode='lines', name='Cosine'),
        ],
        layout=go.Layout(
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]),
                        dict(label="Pause",
                            method="animate",
                            args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
                    ]
                )
            ]
        ),
        frames=frames
    )

    # Display the animated chart in Streamlit
    # st.plotly_chart(fig)



    

  

