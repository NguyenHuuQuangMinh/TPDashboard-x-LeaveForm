from flask import Blueprint, session, redirect, url_for, request, render_template, flash, jsonify
from Controller.decorators import admin_required
from config.ConnectDB import get_postgres_engine
from sqlalchemy import text

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@admin_required
def before_all():
    pass

@admin_bp.route('/admin')
def dashboard():
    if session.get('is_admin') == 0:
        session['is_admin'] = 1
    return render_template("admin/dashboard.html")


@admin_bp.route('/admin/nts')
def nts_dashboard():
    engine = get_postgres_engine()
    code = request.args.get('code', '').strip()
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    tradeshow = request.args.get('tradeshow', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 100

    with engine.connect() as conn:
        filters = []
        params = {}
        if code:
            filters.append("code ILIKE :code")
            params['code'] = f"%{code}%"
        if name:
            filters.append("name ILIKE :name")
            params['name'] = f"%{name}%"
        if category:
            cats = [c.strip() for c in category.split(',')]
            filters.append("category = ANY(:cats)")
            params['cats'] = cats
        if tradeshow:
            filters.append("message_text ILIKE :tradeshow")
            params['tradeshow'] = f"%{tradeshow}%"

        where = "WHERE " + " AND ".join(filters) if filters else ""

        # Total count
        count_sql = text(f"SELECT COUNT(*) FROM drm_nts_messages {where}")
        total = conn.execute(count_sql, params).scalar()

        # Messages
        offset = (page - 1) * per_page
        params['limit'] = per_page
        params['offset'] = offset
        msg_sql = text(f"""
            SELECT code, name, category, message_text, created_date
            FROM drm_nts_messages
            {where}
            ORDER BY created_date DESC
            LIMIT :limit OFFSET :offset
        """)
        messages = conn.execute(msg_sql, params).mappings().all()

        # Categories for dropdown
        cat_sql = text("SELECT DISTINCT category FROM drm_nts_messages ORDER BY category")
        categories = [r['category'] for r in conn.execute(cat_sql).mappings().all()]

    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "admin/nts_dashboard.html",
        messages=messages,
        categories=categories,
        total=total,
        page=page,
        total_pages=total_pages,
        filters={'code': code, 'name': name, 'category': category, 'tradeshow': tradeshow}
    )


@admin_bp.route('/admin/nts/agent/<code>')
def nts_agent_detail(code):
    engine = get_postgres_engine()
    with engine.connect() as conn:

        # Contact info from drm_info
        contact_sql = text("""
            SELECT DISTINCT contact_name, title, email, phone
            FROM drm_info
            WHERE agent_code = :code
        """)
        contacts = conn.execute(contact_sql, {'code': code}).mappings().all()

        # Revenue by year/month — chỉ từ 2025 trở đi
        yearly_sql = text("""
            SELECT
                EXTRACT(YEAR FROM last_service_date)::int  AS year,
                EXTRACT(MONTH FROM last_service_date)::int AS month,
                SUM(profit) AS profit
            FROM "View_Revenue_By_Agent"
            WHERE agent_code = :code
              AND EXTRACT(YEAR FROM last_service_date) >= 2025
            GROUP BY
                EXTRACT(YEAR FROM last_service_date),
                EXTRACT(MONTH FROM last_service_date)
            ORDER BY year, month
        """)
        yearly = conn.execute(yearly_sql, {'code': code}).mappings().all()

    return jsonify({
        'contacts': [dict(c) for c in contacts],
        'yearly':   [dict(y) for y in yearly]
    })
