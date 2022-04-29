from ..connect_db import runQuery_tidb

def get_raw_data():
    data = runQuery_tidb(f"""
    SELECT
    CONVERT_TZ(FROM_UNIXTIME(psc.cl_date_clicked), 'GMT', 'US/Central') AS timecl,
    DATE_FORMAT(CONVERT_TZ(FROM_UNIXTIME(psc.cl_date_clicked), 'GMT', 'US/Central'),'%y-%m-%d') AS datecl,
    DATE_FORMAT(CONVERT_TZ(FROM_UNIXTIME(FLOOR(psc.cl_date_clicked/300)*300),'GMT', 'US/Central'),'%H:%i') AS h_m,
    psc.cl_id, psc.cl_tracked, psc.cl_approved, psc.cl_refunded, psc.cl_fraud, psc.cl_revenue_xe,

    psc.a_id AS project_id, a.a_name AS project_name, CONCAT('[',psc.a_id,'] ',a.a_name) AS project,
    a.d_id AS merchant_id, d.d_company AS merchant_name, CONCAT('[',a.d_id,'] ',d.d_company) AS merchant,
    psc.ps_id, ps.ps, 
    psc.pss_id, CASE WHEN psc.pss_id=0 OR psc.pss_id IS NULL THEN 'Unknown' ELSE pss.pss END AS pss,
    psc.co_id, co.co_code_alpha3, co.co_name


    FROM (SELECT * FROM ti_paymentwall.ps_clicks WHERE cl_date_clicked > FLOOR(UNIX_TIMESTAMP(NOW() - INTERVAL 3 HOUR)/300)*300) AS psc
    INNER JOIN ti_paymentwall.applications AS a ON psc.a_id = a.a_id
    INNER JOIN ti_paymentwall.developers AS d ON a.d_id = d.d_id
    INNER JOIN (SELECT ps_id, CONCAT('[',ps_id,'] ',ps_name) AS ps FROM ti_paymentwall.payment_systems) AS ps ON psc.ps_id = ps.ps_id
    LEFT JOIN (SELECT pss_id, CONCAT('[',pss_id,'] ',pss_name) AS pss FROM ti_paymentwall.ps_subaccounts) AS pss ON psc.pss_id = pss.pss_id
    INNER JOIN ti_paymentwall.countries AS co ON psc.co_id = co.co_id
    """)
    return data