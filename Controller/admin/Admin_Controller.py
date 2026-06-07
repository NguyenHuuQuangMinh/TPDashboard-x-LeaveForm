from flask import Blueprint, session, redirect, url_for, request, render_template, flash, jsonify
from Controller.decorators import admin_required
from Model.entity import Entity
from Model.admin.admin import Admin

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@admin_required
def before_all():
    pass

@admin_bp.route('/admin')
def dashboard():
    if session.get('is_admin') == 0:
        session['is_admin'] = 1
    code = request.args.get('code', '').strip()
    name = request.args.get('name', '').strip()
    year = request.args.get('year', '').strip()
    category = request.args.get('category', '').strip()
    tradeshow = request.args.get('tradeshow', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 100
    total, messages = Entity.get_nts(code, name, category, tradeshow, page)
    categories = Entity.get_cate()
    total_pages = (total + per_page - 1) // per_page
    detailscate = Entity.get_nts_detail()
    return render_template("admin/dashboard.html",
                           messages=messages,
                           categories=categories,
                           total=total,
                           page=page,
                           total_pages=total_pages,
                           nts_detail=detailscate,
                           filters={'code': code, 'name': name, 'category': category, 'tradeshow': tradeshow, 'year': year}
                           )



@admin_bp.route('/admin/nts/agent/<code>')
def nts_agent_detail(code):
    contacts, yearly = Entity.get_details(code)
    return jsonify({
        'contacts': [dict(c) for c in contacts],
        'yearly':   [dict(y) for y in yearly]
    })

@admin_bp.route('/admin/chart/revenue-quarter')
def revenue_quarter_chart():

    code = request.args.get('code', '').strip()
    name = request.args.get('name', '').strip()
    year = request.args.get('year', '').strip()
    category = request.args.get('category', '').strip()
    tradeshow = request.args.get('tradeshow', '').strip()

    quarter_chart = Admin.get_revenue_quarter(
        code,
        name,
        category,
        tradeshow,
        year
    )

    return jsonify([
        dict(r)
        for r in quarter_chart
    ])

@admin_bp.route('/admin/chart/revenue-monthly')
def revenue_monthly_chart():

    code = request.args.get('code', '').strip()
    name = request.args.get('name', '').strip()
    year = request.args.get('year', '').strip()
    category = request.args.get('category', '').strip()
    tradeshow = request.args.get('tradeshow', '').strip()

    monthly_chart = Admin.get_revenue_monthly(
        code,
        name,
        category,
        tradeshow,
        year
    )


    return jsonify([
        dict(r)
        for r in monthly_chart
    ])

@admin_bp.route('/admin/chart/top-agents')
def top_agents_chart():

    code = request.args.get('code', '').strip()
    name = request.args.get('name', '').strip()
    year = request.args.get('year', '').strip()
    category = request.args.get('category', '').strip()
    tradeshow = request.args.get('tradeshow', '').strip()

    agent_chart = Admin.get_top_agents(
        code,
        name,
        category,
        tradeshow,
        year
    )

    return jsonify([
        dict(r)
        for r in agent_chart
    ])

@admin_bp.route('/admin/chart/revenue-quarter-detail')
def revenue_quarter_detail():

    quarter = request.args.get('quarter')
    year = request.args.get('year')
    code = request.args.get('code', '').strip()
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    tradeshow = request.args.get('tradeshow', '').strip()
    from_date =request.args.get('from_date')
    to_date =request.args.get('to_date')
    data = Admin.get_revenue_quarter_detail(
        quarter=quarter,
        year=year,
        code=code,
        name=name,
        category=category,
        tradeshow=tradeshow,
        from_date=from_date,
        to_date=to_date
    )

    return jsonify(data)

@admin_bp.route('/admin/chart/revenue-monthly-detail')
def revenue_monthly_detail():

    month = request.args.get('month')
    year = request.args.get('year')
    code = request.args.get('code', '').strip()
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    tradeshow = request.args.get('tradeshow', '').strip()
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    data = Admin.get_revenue_monthly_detail(
        month=month,
        year=year,
        code=code,
        name=name,
        category=category,
        tradeshow=tradeshow,
        from_date=from_date,
        to_date=to_date
    )

    return jsonify(data)

@admin_bp.route('/admin/chart/top-agents-detail')
def top_agents_detail():

    agent_code = request.args.get('agent_code')
    year = request.args.get('year')
    code = request.args.get('code', '').strip()
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    tradeshow = request.args.get('tradeshow', '').strip()
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    data = Admin.get_top_agents_detail(

        agent_code=agent_code,
        year=year,
        code=code,
        name=name,
        category=category,
        tradeshow=tradeshow,
        from_date=from_date,
        to_date=to_date
    )

    return jsonify(data)

